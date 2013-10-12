# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint
from . import __name__ as module_name

__all__ = ['blueprint']


blueprint = Blueprint(module_name, module_name)
