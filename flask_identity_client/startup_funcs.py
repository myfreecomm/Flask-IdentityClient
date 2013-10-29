# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

import urllib
from functools import wraps
from httplib2 import HttpLib2Error
from flask import current_app as app, redirect, request, session, url_for, g
from .views import PWRemoteApp

__all__ = ['user_required', 'resources_from_middle']


def user_required():
    login_url = url_for('identity_client.index', next=request.url)

    user_data = g.user_data = session.get('user_data')
    if not user_data:
        return redirect(login_url)


def resources_from_middle(settings_key):

    @wraps(resources_from_middle)
    def startup_func():
        settings = app.config[settings_key]
        token = ':'.join((settings['TOKEN'], settings['SECRET'])).encode('base64').strip()
        auth = ' '.join(('Basic', token))
        url = join_path(settings['HOST'], settings['PATH'])

        _, oauth_secret = session['access_token']
        url = '{url}?oauth_token_secret={secret}&oauth_scope={scope}' \
              .format(
                  url = url,
                  secret = escape(oauth_secret),
                  scope = escape(url),
              )

        headers = {
            'Authorization': auth,
            'Accept': 'application/json',
        }

        domains = None
        try:
            session['resources'] = PWRemoteApp.get_instance().get(url, headers=headers).data

        except HttpLib2Error, exc:
            logger = app.logger.getChild(resources_from_middle.__name__)
            logger.error('(%s) %s', type(exc).__name__, exc)
            session['resources'] = None

    return startup_func


def join_path(host, path):
    host = host[:-1] if host.endswith('/') else host
    path = path[1:] if path.startswith('/') else path
    return '/'.join((host, path))


escape = lambda s: urllib.quote(s.encode('utf-8'), safe='~ ').replace(' ', '+')
