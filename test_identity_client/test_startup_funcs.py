# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import g, url_for
from mock import patch
from ._base import TestCase

from flask_identity_client.startup_funcs import user_required


__all__ = ['TestUserRequired']


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

        self.assertStatus(response, 302)
        self.assertEqual(response.headers['Location'], url_for('identity_client.index', next='http://localhost/'))
