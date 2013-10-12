# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['ServiceAccount']


class ServiceAccount(object):

    @classmethod
    def update(cls, accounts):
        return [account['uuid'] for account in accounts]
