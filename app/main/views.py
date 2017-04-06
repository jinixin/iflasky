# coding=utf-8
from flask import render_template as rt, flash, redirect, url_for, request
from . import main
from ..decorators import require_permit, require_admin_permit
from ..models import Permit, Post
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
