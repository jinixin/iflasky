from flask import g, abort
from functools import wraps


def require_api_permit(permit):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if not g.current_user.check_permit(permit):
                abort(403)
            return func(*args, **kwargs)

        return inner

    return decorator
