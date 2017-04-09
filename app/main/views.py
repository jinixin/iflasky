# coding=utf-8
from flask import render_template as rt, flash, redirect, url_for, request, abort
from . import main
from ..decorators import require_permit, require_admin_permit
from ..models import Permit, Post, Follow
from flask_login import login_required, current_user
from .forms import *
from .. import db


@main.route('/')
def index():
    return rt('index.html')


@main.route('/checkPermit')
@require_permit(Permit.manage_comment)
def check_permit():
    flash('Meet the permission.')
    return rt('index.html')


@main.route('/user/<username>')
def user_profile(username):
    page_now = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    pagination = user.post_list.order_by(Post.timestamp.desc()).paginate(page_now, per_page=15, error_out=True)
    posts = pagination.items
    return rt('user/profile.html', user=user, posts=posts, pagination=pagination)


@main.route('/user/editProfile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Edit profile successfully.')
        return redirect(url_for('main.user_profile', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return rt('user/edit_profile.html', form=form)


@main.route('/user/editProfile/<int:user_id>', methods=['GET', 'POST'])
@require_admin_permit
@login_required
def admin_edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditProfileForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.role_id = form.role.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        # user.avatar_hash = md5(user.email.encode('utf-8')).hexdigest() #邮箱变了，头像不该变
        db.session.add(user)
        flash('Administrator edit profile successfully.')
        return redirect(url_for('main.user_profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return rt('user/edit_profile.html', form=form)


@main.route('/article/edit', methods=['GET', 'POST'])
@login_required
def write_article():
    form = EditPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user._get_current_object())
        db.session.add(post)
        flash('Article publish successfully.')
        return redirect(url_for('main.user_profile', username=current_user.username))
    return rt('article/edit_post.html', form=form)


@main.route('/article/showList')
def show_article_list():
    page_now = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page_now, per_page=20, error_out=True)
    posts = pagination.items
    return rt('article/show_list.html', posts=posts, pagination=pagination)


@main.route('/article/<int:article_id>')
def show_article(article_id):
    post = Post.query.get_or_404(article_id)
    return rt('article/post.html', post=post)


@main.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def rewrite_article(article_id):
    post = Post.query.get_or_404(article_id)
    if current_user != post.author and not current_user.is_administrator():
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.add(post)
        flash('Article changed successfully.')
        return redirect(url_for('main.show_article', article_id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    return rt('article/edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@require_permit(Permit.follow)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('The user is not existed.')
        return redirect(url_for('main.index'))
    elif current_user.is_following(user):
        flash('The user has already been following.')
        return redirect(url_for('main.user_profile', username=username))
    else:
        current_user.follow(user)
        flash('You have followed %s successfully.' % username)
        return redirect(url_for('main.user_profile', username=username))


@main.route('/unfollow/<username>')
@login_required
@require_permit(Permit.follow)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('The user is not existed.')
        return redirect(url_for('main.index'))
    elif not current_user.is_following(user):
        flash('You have not followed %s.' % username)
        return redirect(url_for('main.user_profile', username=username))
    else:
        current_user.unfollow(user)
        flash('You have unfollowed %s successfully.' % username)
        return redirect(url_for('main.user_profile', username=username))


def show_common(username, flag):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    if flag == 1:
        pagination = user.idol_list.order_by(Follow.timestamp).paginate(page, per_page=24, error_out=True)
        relation = [{'user': item.idol, 'timestamp': item.timestamp} for item in pagination.items]
        endpoint = 'main.show_idols'
        title = 'Idols of %s' % username
    else:
        pagination = user.fans_list.order_by(Follow.timestamp).paginate(page, per_page=24, error_out=True)
        relation = [{'user': item.fans, 'timestamp': item.timestamp} for item in pagination.items]
        endpoint = 'main.show_fans'
        title = 'Fans of %s' % username
    return rt('user/relation.html', relation=relation, pagination=pagination, endpoint=endpoint, title=title,
              username=username)


@main.route('/following/show/<username>')
def show_idols(username):
    return show_common(username, 1)


@main.route('/followed/show/<username>')
def show_fans(username):
    return show_common(username, 2)
