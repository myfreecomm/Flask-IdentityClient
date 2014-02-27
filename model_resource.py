# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask_identity_client import signals

__all__ = ['ServiceAccount']


class ServiceAccount(object):

    @classmethod
    def update(cls, user_data):
        accounts = user_data.get('accounts')
        return (account['uuid'] for account in accounts)


@signals.update_service_account.connect
def update(sender, user_data, callback):
    callback(ServiceAccount.update(user_data))
