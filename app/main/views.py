from flask import session, render_template as rt, url_for, redirect, current_app as app
from . import main
from .forms import NameForm
from ..models import User
from .. import db
from ..email import send_email


# @main.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             session['known'] = False
#             send_email([app.config['FLASKY_MAIL_ADMIN']], 'New User', 'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         form.name.data = ''
#         return redirect(url_for('main.index'))
#     return rt('index.html', form=form, name=session.get('name'), known=session.get('known') or False)

@main.route('/')
def index():
    return rt('index.html')
