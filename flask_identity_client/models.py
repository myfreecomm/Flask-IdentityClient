# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from importlib import import_module
from flask import current_app as app

__all__ = ['get_service_account']


def get_service_account():
    aux = app.config['SERVICE_ACCOUNT'].split('.')
    modelname = aux[-1]
    modulename = '.'.join(aux[:-1])
    module = import_module(modulename)
    return getattr(module, modelname)
