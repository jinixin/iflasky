from flask import render_template as rt, flash
from . import main
from ..decorators import require_permit
from ..models import Permit, User


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
