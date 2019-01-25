#
# Flask-Sixpack
#
# Copyright (C) 2019 Boris Raicheff
# All rights reserved
#


from datetime import timedelta

from flask import current_app, g, request
from sixpack import sixpack


try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Sixpack(object):
    """
    Flask-Sixpack
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(current_app)

    @staticmethod
    def init_app(app):
        app.config.setdefault('SIXPACK_HOST', 'http://localhost:5000')
        app.config.setdefault('SIXPACK_TIMEOUT', 0.5)
        app.config.setdefault('SIXPACK_COOKIE_NAME', 'sixpack_client_id')
        app.config.setdefault('SIXPACK_COOKIE_TIMEOUT', timedelta(days=365))
        app.after_request(_after_request)

    @staticmethod
    def session():
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sixpack_session'):
                ctx.sixpack_session = create_session()
            return ctx.sixpack_session


def create_session():
    options = {
        'host': current_app.config['SIXPACK_HOST'],
        'timeout': current_app.config['SIXPACK_TIMEOUT']
    }
    params = {
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    }
    cookie_name = current_app.config['SIXPACK_COOKIE_NAME']
    client_id = request.cookies.get(cookie_name, None)
    if client_id is None:
        client_id = str(sixpack.generate_client_id())
        setattr(g, cookie_name, client_id)
    return sixpack.Session(client_id=client_id, options=options, params=params)


def _after_request(response):
    cookie_name = current_app.config['SIXPACK_COOKIE_NAME']
    if getattr(g, cookie_name, None) is not None:
        response.set_cookie(cookie_name, getattr(g, cookie_name), max_age=current_app.config['SIXPACK_COOKIE_TIMEOUT'])
        response.vary.add('Cookie')
    return response


# EOF
