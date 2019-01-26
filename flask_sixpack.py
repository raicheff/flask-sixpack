#
# Flask-Sixpack
#
# Copyright (C) 2019 Boris Raicheff
# All rights reserved
#


import requests

from flask import current_app, g, request, session
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
        app.config.setdefault('SIXPACK_SESSION_KEY', 'sixpack_client_id')
        app.after_request(_after_request)

    @property
    def session(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sixpack_session'):
                ctx.sixpack_session = create_session()
            return ctx.sixpack_session

    @staticmethod
    def status():
        return requests.get(current_app.config['SIXPACK_HOST'] + '/_status')


def create_session():
    options = {
        'host': current_app.config['SIXPACK_HOST'],
        'timeout': current_app.config['SIXPACK_TIMEOUT']
    }
    params = {
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    }
    session_key = current_app.config['SIXPACK_SESSION_KEY']
    client_id = session.get(session_key, None)
    if client_id is None:
        client_id = str(sixpack.generate_client_id())
        setattr(g, session_key, client_id)
    return sixpack.Session(client_id=client_id, options=options, params=params)


def _after_request(response):
    session_key = current_app.config['SIXPACK_SESSION_KEY']
    if getattr(g, session_key, None) is not None:
        session[session_key] = getattr(g, session_key)
    return response


# EOF
