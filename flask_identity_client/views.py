# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import current_app as app, escape, redirect, request, url_for, session
from flaskext.oauth import OAuthRemoteApp, OAuthException, parse_response
from .application import blueprint
from .models import get_service_account

__all__ = []


@blueprint.route('/', methods=['GET'])
def index():
    #-------------------------------------------------------------------
    # Autenticação
    #
    ServiceAccount = get_service_account()
    access_token = session.get('access_token')

    if access_token is None:
        return redirect(url_for('identity_client.login'))

    config = app.config['PASSAPORTE_WEB']
    fetch_user_data_url = '/'.join((config['HOST'], config['FETCH_USER_DATA_PATH']))
    original_user_data = PWRemoteApp.get_instance().post(fetch_user_data_url).data

    #-------------------------------------------------------------------
    # Extração de dados
    #
    user_data = {
        'uuid': original_user_data['uuid'],
        'email': original_user_data['email'],
    }

    first_name = original_user_data.get('first_name')
    last_name = original_user_data.get('last_name')

    if first_name and last_name:
        user_data['full_name'] = ' '.join((first_name, last_name))
    elif first_name:
        user_data['full_name'] = first_name
    elif last_name:
        user_data['full_name'] = last_name
    else:
        user_data['full_name'] = user_data['email']

    user_data['accounts'] = ServiceAccount.update(original_user_data.get('accounts', []))
    session['user_data'] = user_data

    next_url = escape(request.values.get('next') \
                   or url_for(app.config.get('ENTRYPOINT', 'index')))
    return redirect(next_url)


@blueprint.route('/login', methods=['GET'])
def login():

    next_url = escape(request.values.get('next', ''))
    if next_url:
        callback = url_for('identity_client.authorized', next=next_url, _external=True)
    else:
        callback = url_for('identity_client.authorized', _external=True)

    return PWRemoteApp.get_instance().authorize(callback=callback)


@blueprint.route('/logout', methods=['GET'])
def logout():
    session.pop('user_data', None)
    session.pop('access_token', None)

    # TODO: trocar pela página comercial
    next_url = escape(request.values.get('next', '')) \
            or url_for('static', filename='docs/')
    return redirect(next_url)


@blueprint.route('/callback', methods=['GET'])
def authorized():
    passaporte_web = PWRemoteApp.get_instance()
    next_url = escape(request.values.get('next', ''))

    @passaporte_web.authorized_handler
    def authorized_handler(resp):
        access_token = resp['oauth_token']
        token_secret = resp['oauth_token_secret']
        session['access_token'] = (access_token, token_secret)

        if next_url:
            index = url_for('identity_client.index', next=next_url)
        else:
            index = url_for('identity_client.index')

        return redirect(index)

    return authorized_handler()


class PWRemoteApp(OAuthRemoteApp):

    # TODO: colocar isso no módulo da aplicação
    __passaporte_web = None

    def handle_oauth1_response(self):
        client = self.make_client()

        data = 'oauth_verifier={0}'.format(request.values['oauth_verifier'])
        resp, content = client.request(
            self.expand_url(self.access_token_url),
            self.access_token_method,
            body = data,
        )

        data = parse_response(resp, content)
        if resp['status'] != '200':
            raise OAuthException('Invalid response from {0.name}'.format(self), data)
        return data

    @classmethod
    def get_instance(cls):
        if cls.__passaporte_web is None:
            config = app.config['PASSAPORTE_WEB']
            passaporte_web = cls(None, 'passaporte web',
                # unless absolute urls are used to make requests, this will be added
                # before all URLs.  This is also true for request_token_url and others.
                base_url = config['HOST'],

                # where flask should look for new request tokens
                request_token_url = config['REQUEST_TOKEN_PATH'],
                request_token_params = { 'scope': 'auth:api' },

                # where flask should exchange the token with the remote application
                access_token_url = config['ACCESS_TOKEN_PATH'],
                access_token_method = 'POST',

                # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
                # they mostly work the same, but for sign on /authenticate is
                # expected because this will give the user a slightly different
                # user interface on the twitter side.
                authorize_url = config['AUTHORIZATION_PATH'],

                # the consumer keys from the passaporteweb application registry.
                consumer_key = config['CONSUMER_TOKEN'],
                consumer_secret = config['CONSUMER_SECRET'],
            )

            @passaporte_web.tokengetter
            def tokengetter():
                return session.get('access_token')

            cls.__passaporte_web = passaporte_web

        return cls.__passaporte_web
