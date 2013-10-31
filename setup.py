# coding: UTF-8
from distutils.core import setup
from os import path

readme = path.join(path.dirname(__file__), 'README')
if path.exists(readme):
    with open(readme) as fd:
        long_description = fd.read()

else:
    long_description = None


setup(
    name             = 'Flask-IdentityClient',
    version          = '0.4.2',
    license          = 'Copyright',
    platforms        = 'any',
    url              = 'https://github.com/myfreecomm/Flask-IdentityClient',
    download_url     = 'https://github.com/myfreecomm/Flask-IdentityClient/archive/next_release.zip',
    packages         = ['flask_identity_client'],
    author           = 'Rodrigo Cacilhas',
    author_email     = 'rodrigo.cacilhas@myfreecomm.com.br',
    description      = 'PassaporteWeb connection for Flask applications',
    long_description = long_description,
    install_requires = [
        'httplib2>=0.8',
        'requests>=1.2.3',
        'oauth2==1.5.211',
        'Flask>=0.10.1',
        'Flask-OAuth>=0.11',
    ],
    classifiers      = [
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
