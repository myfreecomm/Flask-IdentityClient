# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask_testing import TestCase as BaseTestCase

__all__ = ['TestCase']


class TestCase(BaseTestCase):

    maxDiff = None

    def create_app(self):
        from application import app
        return app
