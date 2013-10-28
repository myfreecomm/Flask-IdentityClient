# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from mock import patch
from model_resource import ServiceAccount
from ._base import TestCase

__all__ = ['TestIndex', 'TestLogin', 'TestAuthorized', 'TestLogout']


class TestIndex(TestCase):

    endpoint = 'identity_client.index'

    def get_url(self, next_url=None):
        if next_url:
            return url_for(self.endpoint, next=next_url)
        else:
            return url_for(self.endpoint)

    @patch('flask_identity_client.views.session')
    def test_index_redirects_to_login(self, session):
        session.get.return_value = None
        response = self.client.get(self.get_url())

        self.assertStatus(response, 302)
        self.assertEqual(response.headers['Location'], url_for('identity_client.login', _external=True))
        session.get.assert_called_once_with('access_token')

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_inactive_user(self, session, remote_app):
        session.get.return_value = ('R0JaNT1RKNDP', 'W3oZSRHACS090Xwf')
        remote_app_instance = remote_app.get_instance.return_value
        remote_app_instance.post.return_value.data = {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'is_active': False,
            'accounts': [
                {
                    'uuid': 'd9a795c8-c891-4665-ac63-9d408209be29',
                    'name': 'Test Account',
                    'plan_slug': 'basic',
                }
            ],
        }

        response = self.client.get(self.get_url())
        self.assertStatus(response, 302)

        config = self.app.config['PASSAPORTE_WEB']
        fetch_user_data_url = '/'.join((config['HOST'], config['FETCH_USER_DATA_PATH']))

        self.assertEqual(response.headers['Location'], url_for('index', _external=True))
        remote_app.get_instance.assert_called_once_with()
        remote_app_instance.post.assert_called_once_with(fetch_user_data_url)

        session.__setitem__.assert_called_once_with('user_data', {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'full_name': 'johndoe@myfreecomm.com.br',
            'accounts': ['d9a795c8-c891-4665-ac63-9d408209be29'],
        })

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_user_without_accounts(self, session, remote_app):
        session.get.return_value = ('R0JaNT1RKNDP', 'W3oZSRHACS090Xwf')
        remote_app_instance = remote_app.get_instance.return_value
        remote_app_instance.post.return_value.data = {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'is_active': True,
            'accounts': [],
        }

        response = self.client.get(self.get_url())
        self.assertStatus(response, 302)

        config = self.app.config['PASSAPORTE_WEB']
        fetch_user_data_url = '/'.join((config['HOST'], config['FETCH_USER_DATA_PATH']))

        self.assertEqual(response.headers['Location'], url_for('index', _external=True))
        remote_app.get_instance.assert_called_once_with()
        remote_app_instance.post.assert_called_once_with(fetch_user_data_url)

        session.__setitem__.assert_called_once_with('user_data', {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'full_name': 'johndoe@myfreecomm.com.br',
            'accounts': [],
        })

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_new_account(self, session, remote_app):
        session.get.return_value = ('R0JaNT1RKNDP', 'W3oZSRHACS090Xwf')
        remote_app_instance = remote_app.get_instance.return_value
        remote_app_instance.post.return_value.data = {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'is_active': True,
            'accounts': [
                {
                    'uuid': 'd9a795c8-c891-4665-ac63-9d408209be29',
                    'name': 'Test Account',
                    'plan_slug': 'basic',
                }
            ],
        }

        response = self.client.get(self.get_url())
        self.assertStatus(response, 302)

        config = self.app.config['PASSAPORTE_WEB']
        fetch_user_data_url = '/'.join((config['HOST'], config['FETCH_USER_DATA_PATH']))

        self.assertEqual(response.headers['Location'], url_for('index', _external=True))
        remote_app.get_instance.assert_called_once_with()
        remote_app_instance.post.assert_called_once_with(fetch_user_data_url)

        session.__setitem__.assert_called_once_with('user_data', {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'full_name': 'johndoe@myfreecomm.com.br',
            'accounts': ['d9a795c8-c891-4665-ac63-9d408209be29'],
        })

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_next_url(self, session, remote_app):
        session.get.return_value = ('R0JaNT1RKNDP', 'W3oZSRHACS090Xwf')
        remote_app_instance = remote_app.get_instance.return_value
        remote_app_instance.post.return_value.data = {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'is_active': True,
            'accounts': [
                {
                    'uuid': 'd9a795c8-c891-4665-ac63-9d408209be29',
                    'name': 'Test Account',
                    'plan_slug': 'basic',
                }
            ],
        }

        response = self.client.get(self.get_url('http://www.google.com/'))
        self.assertStatus(response, 302)

        self.assertEqual(response.headers['Location'], 'http://www.google.com/')


class TestLogin(TestCase):

    endpoint = 'identity_client.login'

    def get_url(self, next_url=None):
        if next_url:
            return url_for(self.endpoint, next=next_url)
        else:
            return url_for(self.endpoint)

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_login(self, session, remote_app):
        remote_app_instance = remote_app.get_instance.return_value
        remote_app_instance.authorize.return_value = 'AUTHORIZED'
        response = self.client.get(self.get_url())

        self.assert_200(response)
        self.assertEqual(response.data, 'AUTHORIZED')

        remote_app_instance.authorize.assert_called_once_with(
            callback = url_for('identity_client.authorized', _external=True))

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_next_url(self, session, remote_app):
        remote_app_instance = remote_app.get_instance.return_value
        remote_app_instance.authorize.return_value = 'AUTHORIZED'

        response = self.client.get(self.get_url('http://www.google.com/'))
        remote_app_instance.authorize.assert_called_with(
            callback = url_for('identity_client.authorized', next='http://www.google.com/', _external=True)
        )


class TestAuthorized(TestCase):

    endpoint = 'identity_client.authorized'

    def get_url(self, next_url=None):
        if next_url:
            return url_for(self.endpoint, next=next_url)
        else:
            return url_for(self.endpoint)

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_authorized(self, session, remote_app):
        remote_app_instance = remote_app.get_instance.return_value

        def side_effect(f):
            def callback():
                resp = {
                    'oauth_token': 'R0JaNT1RKNDP',
                    'oauth_token_secret': 'W3oZSRHACS090Xwf',
                }
                return f(resp)
            return callback

        remote_app_instance.authorized_handler.side_effect = side_effect

        response = self.client.get(self.get_url())
        self.assertStatus(response, 302)

        self.assertEqual(response.headers['Location'], url_for('identity_client.index', _external=True))
        self.assertTrue(remote_app_instance.authorized_handler.called)
        session.__setitem__.assert_called_once_with('access_token', ('R0JaNT1RKNDP', 'W3oZSRHACS090Xwf'))

    @patch('flask_identity_client.views.PWRemoteApp')
    @patch('flask_identity_client.views.session')
    def test_next_url(self, session, remote_app):
        remote_app_instance = remote_app.get_instance.return_value

        def side_effect(f):
            def callback():
                resp = {
                    'oauth_token': 'R0JaNT1RKNDP',
                    'oauth_token_secret': 'W3oZSRHACS090Xwf',
                }
                return f(resp)
            return callback

        remote_app_instance.authorized_handler.side_effect = side_effect

        response = self.client.get(self.get_url('http://www.google.com/'))
        self.assertStatus(response, 302)

        self.assertEqual(response.headers['Location'],
            url_for('identity_client.index', next='http://www.google.com/', _external=True))


class TestLogout(TestCase):

    endpoint = 'identity_client.logout'

    def get_url(self, next_url=None):
        if next_url:
            return url_for(self.endpoint, next=next_url)
        else:
            return url_for(self.endpoint)

    @patch('flask_identity_client.views.session')
    def test_logout(self, session):
        pop_response = { 'user_data': '', 'access_token': '' }
        def side_effect(key, default):
            self.assertEqual(pop_response.pop(key), '')
            self.assertTrue(default is None)
        session.pop.side_effect = side_effect

        response = self.client.get(self.get_url())
        self.assertStatus(response, 302)
        self.assertEqual(response.headers['Location'], 'http://localhost/static/docs/')
        self.assertEqual(pop_response, {}) # todas as chaves foram removidas
