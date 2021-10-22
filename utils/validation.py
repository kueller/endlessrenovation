import functools

from flask import request, abort


def api_validate(api_key):
    def decorator_api_validate(func):
        @functools.wraps(func)
        def wrapper_api_validate(*args, **kwargs):
            if request.headers.get("x-api-key") != api_key:
                abort(401)
            return func(*args, **kwargs)

        return wrapper_api_validate

    return decorator_api_validate
