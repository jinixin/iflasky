# coding=utf-8
from flask import render_template as rt, flash, redirect, url_for
from . import main
from ..decorators import require_permit, require_admin_permit
from ..models import Permit, User
from flask_login import login_required, current_user
from .forms import EditProfileForm, AdminEditProfileForm
from .. import db
from hashlib import md5


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
    user = User.query.filter_by(username=username).first_or_404()
    return rt('user/profile.html', user=user)


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
