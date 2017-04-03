# coding=utf-8
from flask import render_template as rt, redirect, request, url_for, flash
from . import auth
from .forms import *
from ..models import User
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..email import send_email
from ..decorators import require_permit
from ..models import Permit


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return rt('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid username or password.')
    return rt('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()  # 必须提交，否则不能获得token
        token = user.make_confirm_token()
        send_email([user.email], 'Confirm Your Account', 'auth/mail/confirm', user=user, token=token)
        # 必须要传user，html中current_user不可用
        flash('A confirmation email has been sent to your mail.')
        return redirect(url_for('main.index'))
    return rt('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        pass
    elif current_user.check_token(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.make_confirm_token()
    send_email([current_user.email], 'Confirm Your Account', 'auth/mail/confirm', user=current_user, token=token)
    # 为了统一使用user，故传入current_user
    flash('A new confirmation email has been sent to your mail.')
    return rt('index.html')


@auth.route('/changePassword', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        send_email([current_user.email], 'Your password has changed', 'auth/mail/ChangePassword')
        flash('You have changed the password.')
        return redirect(url_for('main.index'))
    return rt('auth/changePassword.html', form=form)


@auth.route('/requestResetPassword', methods=['GET', 'POST'])
def request_reset_password():
    form = RequestResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.make_confirm_token()
            send_email([user.email], 'Reset password', 'auth/mail/resetPassword', user=user, token=token)
            flash('An email to reset password has been sent to you mail.')
            return redirect(url_for('auth.login'))
        else:
            flash('The email not existed.')
            return redirect(url_for('auth.request_reset_password'))
    return rt('auth/resetPassword.html', form=form)


@auth.route('/resetPassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        user = User.query.get(user_id)
        user.password = form.new_password.data
        db.session.add(user)
        flash('The password has been reset.')
        return redirect(url_for('auth.login'))
    else:
        user_id = User.token2id(token)
        if user_id is not None:
            form.user_id.data = user_id  # 写入隐藏域
            return rt('auth/resetPassword.html', form=form)
        return redirect(url_for('main.index'))
