from flask import render_template as rt
from app.main import main


@main.app_errorhandler(404)
def page_not_found(e):
    return rt('error/404.html'), 404


@main.app_errorhandler(500)
def server_error(e):
    return rt('error/500.html'), 500


@main.app_errorhandler(403)
def server_error(e):
    return rt('error/403.html'), 403
