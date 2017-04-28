from flask import jsonify, g
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from . import api
from .errors import forbidden, unauthenticated

http_auth = HTTPBasicAuth()


@api.before_request
@http_auth.login_required
def check_whether_authenticated():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return unauthenticated()


@http_auth.error_handler
def http_auth_error():
    return unauthenticated()


@http_auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.check_api_token(email_or_token)
        g.used_token = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first_or_404()
    g.current_user = user
    g.used_token = False
    return user.check_password(password)


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.used_token:
        return forbidden()
    expire = 3600
    return jsonify({'token': g.current_user.make_token(expire=expire), 'expire': expire})
