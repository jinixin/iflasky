# coding=utf-8
from functools import wraps
from flask_login import current_user
from flask import abort, request
from .models import Permit
from . import redis_cli


def require_permit(permit):
    def decorator(func):
        @wraps(func)  # help返回真实的函数信息
        def inner(*args, **kwargs):
            if not current_user.check_permit(permit):
                abort(403)
            return func(*args, **kwargs)

        return inner

    return decorator


def require_admin_permit(func):
    return require_permit(Permit.admin)(func)


def redis_page_cache(expire=3600):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            url = request.url
            page_source = redis_cli.get(url)
            if page_source is None:
                page_source = func(*args, **kwargs)
                redis_cli.set(url, page_source, ex=expire)
            return page_source

        return inner

    return decorator
