# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = ['app']

#-----------------------------------------------------------------------
# Settings

DEBUG = False
TESTING = True
SECRET_KEY = b's17a!@M1uOv0cI_/$}@6uoJM(7,0y{Ci=N1:N3&>BG%&:V6+'
SERVICE_ACCOUNT = 'model_resource'

ENTRYPOINT = 'index'

PASSAPORTE_WEB = {
    'HOST': 'http://dhcp48.corp:8000',
    'SLUG': 'charging',
    'CONSUMER_TOKEN': '295KkblCDT',
    'CONSUMER_SECRET': 'EeAlpeFt6VteErylmwkCtLZ9qHtpomgG',
    'AUTH_API': 'accounts/api/auth/',
    'REGISTRATION_API': 'accounts/api/create/',
    'PROFILE_API': 'profile/api/info/',
    'REQUEST_TOKEN_PATH': 'sso/initiate/',
    'AUTHORIZATION_PATH': 'sso/authorize/',
    'ACCESS_TOKEN_PATH': 'sso/token/',
    'ACCESS_TOKEN_VALIDATION': 'oauth/1.0/api/resource_owner/',
    'FETCH_USER_DATA_PATH': 'sso/fetchuserdata/',
    'FETCH_ACCOUNTS': 'organizations/api/identities/{uuid}/accounts/',
    'LOGOUT_PATH': 'accounts/logout/',
}


#-----------------------------------------------------------------------
# Flask object

from flask import Flask
app = Flask(__name__)
app.config.from_object(__name__)

from identity_client.startup_funcs import user_required
@app.route('/')
def index():
    return user_required() or 'OK'


#-----------------------------------------------------------------------
# indentity_client blueprint

from identity_client.application import blueprint
app.register_blueprint(blueprint, url_prefix='/sso')
