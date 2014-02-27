# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals
from flask.signals import Namespace

__all__ = ['update_service_account']


ns = Namespace()
update_service_account = ns.signal('update-service-account')
