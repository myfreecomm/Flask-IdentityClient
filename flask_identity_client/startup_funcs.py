# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import redirect, request, session, url_for, g

__all__ = ['user_required']


def user_required():
    login_url = url_for('identity_client.index', next=request.url)

    user_data = g.user_data = session.get('user_data')
    if not user_data:
        return redirect(login_url)
