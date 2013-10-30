# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from time import time
from httplib2 import HttpLib2Error
from flask import g, url_for
from mock import patch
from ._base import TestCase

from flask_identity_client.startup_funcs import user_required, resources_from_middle, Resources


__all__ = ['TestUserRequired', 'TestResourcesFromMiddle']


class TestUserRequired(TestCase):

    def setUp(self):
        self.account_uuid = 'd9a795c8-c891-4665-ac63-9d408209be29'

    @patch('flask_identity_client.startup_funcs.session')
    def test_user_required(self, mock_session):
        uuid = self.account_uuid

        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [uuid],
            },
        }
        def side_effect(key):
            return session.pop(key)
        mock_session.get.side_effect = side_effect

        self.assertTrue(user_required() is None)
        self.assertEqual(g.user_data, {
            'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
            'email': 'johndoe@myfreecomm.com.br',
            'accounts': [uuid],
        })
        self.assertEqual(session, {})

    @patch('flask_identity_client.startup_funcs.session')
    def test_no_user(self, mock_session):
        mock_session.get.return_value = None
        response = user_required()

        self.assertStatus(response, 302)
        self.assertEqual(response.headers['Location'], url_for('identity_client.index', next='http://localhost/'))

    @patch('flask_identity_client.startup_funcs.session')
    def test_no_account(self, mock_session):
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [],
            },
        }
        def side_effect(key):
            return session.pop(key)
        mock_session.get.side_effect = side_effect

        response = user_required()
        self.assertIsNone(response)


class TestResourcesFromMiddle(TestCase):

    def setUp(self):
        self.account_uuid = 'd9a795c8-c891-4665-ac63-9d408209be29'

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_resources_from_middle(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
        }

        response = mock_remote_app.get_instance.return_value.get.return_value
        response.status = 200
        response.data = { 'msg': 'some data' }
        response.headers = {}

        with patch('flask_identity_client.startup_funcs.session', session):
            self.assertTrue(startup_func() is None)

        mock_remote_app.get_instance.assert_called_once_with()
        mock_remote_app.get_instance.return_value.get.assert_called_once_with(
            'http://middle.localhost/resources/'
            '?oauth_token_secret=17a799ddbbbfb855f25e89d0bf51ae19'
            '&oauth_scope=http%3A%2F%2Fmiddle.localhost%2Fresources%2F',
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Basic WDpZV1J6Wm1Ga2MyWm1aR0Z6WkE=',
            }
        )
        self.assertEqual(session['resources'].data, { 'msg': 'some data' })
        self.assertEqual(session['resources'].status, 200)
        self.assertTrue(session['resources'].etag is None)
        self.assertTrue(session['resources'].expires is None)

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_resources_from_middle_with_etag(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
        }

        response = mock_remote_app.get_instance.return_value.get.return_value
        response.status = 200
        response.data = { 'msg': 'some data' }
        response.headers = { 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"' }

        with patch('flask_identity_client.startup_funcs.session', session):
            self.assertTrue(startup_func() is None)

        mock_remote_app.get_instance.assert_called_once_with()
        mock_remote_app.get_instance.return_value.get.assert_called_once_with(
            'http://middle.localhost/resources/'
            '?oauth_token_secret=17a799ddbbbfb855f25e89d0bf51ae19'
            '&oauth_scope=http%3A%2F%2Fmiddle.localhost%2Fresources%2F',
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Basic WDpZV1J6Wm1Ga2MyWm1aR0Z6WkE=',
            }
        )
        self.assertEqual(session['resources'].data, { 'msg': 'some data' })
        self.assertEqual(session['resources'].status, 200)
        self.assertEqual(session['resources'].etag, '"d41d8cd98f00b204e9800998ecf8427e"')

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_error(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
        }

        from flask_identity_client.startup_funcs import app
        mock_remote_app.get_instance.return_value.get.side_effect = HttpLib2Error

        with patch('flask_identity_client.startup_funcs.session', session), \
             patch.object(app.logger, 'getChild') as mock_child:
            self.assertTrue(startup_func() is None)
            mock_child.assert_called_once_with('resources_from_middle')
            mock_child.return_value.getChild.assert_called_once_with('MIDDLE_TEST')
            call_args = mock_child.return_value.getChild.return_value.error.call_args[0]
            self.assertEqual(call_args[0], '(%s) %s')
            self.assertEqual(call_args[1], 'HttpLib2Error')
            self.assertTrue(isinstance(call_args[2], HttpLib2Error))

        mock_remote_app.get_instance.assert_called_once_with()
        self.assertEqual(session['resources'], None)

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_authorization_failure(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
        }

        response = mock_remote_app.get_instance.return_value.get.return_value
        response.status = 401
        response.data = 'authorization failure'
        response.headers = {}

        with patch('flask_identity_client.startup_funcs.session', session):
            self.assertTrue(startup_func() is None)

        mock_remote_app.get_instance.assert_called_once_with()
        mock_remote_app.get_instance.return_value.get.assert_called_once_with(
            'http://middle.localhost/resources/'
            '?oauth_token_secret=17a799ddbbbfb855f25e89d0bf51ae19'
            '&oauth_scope=http%3A%2F%2Fmiddle.localhost%2Fresources%2F',
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Basic WDpZV1J6Wm1Ga2MyWm1aR0Z6WkE=',
            }
        )
        self.assertEqual(session['resources'].data, 'authorization failure')
        self.assertEqual(session['resources'].status, 401)
        self.assertTrue(session['resources'].etag is None)

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_not_modified(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
            'resources': Resources(
                data = { 'msg': 'some data' },
                etag = '"d41d8cd98f00b204e9800998ecf8427e"',
                status = 200,
                expires = None,
            ),
        }

        response = mock_remote_app.get_instance.return_value.get.return_value
        response.status = 304
        response.headers = { 'ETag': '"d41d8cd98f00b204e9800998ecf8427e"' }

        with patch('flask_identity_client.startup_funcs.session', session):
            self.assertTrue(startup_func() is None)

        mock_remote_app.get_instance.assert_called_once_with()
        mock_remote_app.get_instance.return_value.get.assert_called_once_with(
            'http://middle.localhost/resources/'
            '?oauth_token_secret=17a799ddbbbfb855f25e89d0bf51ae19'
            '&oauth_scope=http%3A%2F%2Fmiddle.localhost%2Fresources%2F',
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Basic WDpZV1J6Wm1Ga2MyWm1aR0Z6WkE=',
                'If-None-Match': '"d41d8cd98f00b204e9800998ecf8427e"',
            }
        )
        self.assertEqual(session['resources'].data, { 'msg': 'some data' })
        self.assertEqual(session['resources'].status, 304)
        self.assertEqual(session['resources'].etag, '"d41d8cd98f00b204e9800998ecf8427e"')

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_not_expired(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        expires = time() + 600
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
            'resources': Resources(
                data = { 'msg': 'some data' },
                etag = '"d41d8cd98f00b204e9800998ecf8427e"',
                status = 200,
                expires = expires,
            ),
        }

        with patch('flask_identity_client.startup_funcs.session', session):
            self.assertTrue(startup_func() is None)

        self.assertFalse(mock_remote_app.get_instance.called)
        self.assertEqual(session['resources'].data, { 'msg': 'some data' })
        self.assertEqual(session['resources'].status, 200)
        self.assertEqual(session['resources'].etag, '"d41d8cd98f00b204e9800998ecf8427e"')
        self.assertEqual(session['resources'].expires, expires)

    @patch('flask_identity_client.startup_funcs.PWRemoteApp')
    def test_expired(self, mock_remote_app):
        startup_func = resources_from_middle('MIDDLE_TEST')
        session = {
            'user_data': {
                'uuid': 'a82670c2-027e-4079-b5c7-81f2433041b3',
                'email': 'johndoe@myfreecomm.com.br',
                'accounts': [self.account_uuid],
            },
            'access_token': ['ZHNkc2VyZWY', '17a799ddbbbfb855f25e89d0bf51ae19'],
            'resources': Resources(
                data = { 'msg': 'some data' },
                etag = None,
                status = 200,
                expires = time() - 1,
            ),
        }

        response = mock_remote_app.get_instance.return_value.get.return_value
        response.status = 200
        response.data = { 'msg': 'some data' }
        response.headers = { 'Expires': 'Sun, 06 Nov 1994 08:49:37 GMT' }

        with patch('flask_identity_client.startup_funcs.session', session):
            self.assertTrue(startup_func() is None)

        mock_remote_app.get_instance.assert_called_once_with()
        mock_remote_app.get_instance.return_value.get.assert_called_once_with(
            'http://middle.localhost/resources/'
            '?oauth_token_secret=17a799ddbbbfb855f25e89d0bf51ae19'
            '&oauth_scope=http%3A%2F%2Fmiddle.localhost%2Fresources%2F',
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Basic WDpZV1J6Wm1Ga2MyWm1aR0Z6WkE=',
            }
        )
        self.assertEqual(session['resources'].data, { 'msg': 'some data' })
        self.assertEqual(session['resources'].status, 200)
        self.assertTrue(session['resources'].etag is None)
        self.assertEqual(session['resources'].expires, 784111777)
