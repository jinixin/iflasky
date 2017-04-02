from flask import render_template as rt, flash
from . import main
from ..decorators import require_permit
from ..models import Permit


@main.route('/')
def index():
    return rt('index.html')


@main.route('/checkPermit')
@require_permit(Permit.manage_comment)
def check_permit():
    flash('Meet the permission.')
    return rt('index.html')
