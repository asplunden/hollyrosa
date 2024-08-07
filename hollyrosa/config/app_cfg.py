# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in authtest.

This file complements development/deployment.ini.

"""

import hashlib
import logging

import hollyrosa
from hollyrosa import model
from hollyrosa.model.booking_couch import getVisitingGroupByBoknr
from tg.configuration import AppConfig
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

base_config = AppConfig()
base_config.renderers = ['kajiki']

# True to prevent dispatcher from striping extensions
# For example /socket.io would be served by "socket_io"
# method instead of "socket".
base_config.disable_request_extensions = False

# Set None to disable escaping punctuation characters to "_"
# when dispatching methods.
# Set to a function to provide custom escaping.
base_config.dispatch_path_translator = True

base_config.prefer_toscawidgets2 = True

base_config.package = hollyrosa
base_config.custom_tw2_config['script_name'] = '/hollyrosa'  # hollyrosa in production, hollyrosa_test otherwise

# Enable json in expose
base_config.renderers.append('json')
# Enable genshi in expose to have a lingua franca
# for extensions and pluggable apps.
# You can remove this if you don't plan to use it.
# base_config.renderers.append('genshi')

# Set the default renderer
base_config.default_renderer = 'kajiki'
# Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = False
base_config.model = None
base_config.DBSession = None
# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
base_config.sa_auth.cookie_secret = "5e3d194a-4a6c-4969-9eda-9adfaae78bb4"
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = None
base_config[
    'flash.template'] = """<div class="notification is-$status $status" ><strong><p>$message</p></strong></div>"""

from tg.configuration.auth import TGAuthMetadata

def validate_password(user, password):
    password_hasher = PasswordHasher()

    if 'argon2_hash' in user:
        try:
            password_hasher.verify(user['argon2_hash'], password)
            return True
        except VerifyMismatchError:
            return False

    else:
        h = hashlib.sha256('gninyd'.encode('utf-8'))  # salt
        h.update(password.encode('utf-8'))
        c = h.hexdigest()
        return user['password'] == c

# This tells to TurboGears how to retrieve the data for your user
class ApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def authenticate(self, environ, identity):
        authlog = logging.getLogger('auth2')
        login = identity['login']
        supplied_login_name = identity['login']

        user = model.getHollyCouch().get('user.' + login)

        if not user:

            vgroup_list = getVisitingGroupByBoknr(model.getHollyCouch(), login)
            if len(vgroup_list) > 0:
                user = vgroup_list[0].doc

            else:
                login = None

        elif not validate_password(user, identity['password']):
            login = None

        if login is None:
            try:
                from urllib.parse import parse_qs, urlencode
            except ImportError:
                from urlparse import parse_qs
                from urllib import urlencode
            from tg.exceptions import HTTPFound

            params = parse_qs(environ['QUERY_STRING'])
            params.pop('password', None)  # Remove password in case it was there
            if user is None:
                params['failure'] = 'user-not-found'
                authlog.info('login failed - user-not-found %s' % supplied_login_name[:100])
            else:
                params['login'] = identity['login']
                params['failure'] = 'invalid-password'
                authlog.info('login failed - wrong password for %s' % supplied_login_name)

            # When authentication fails send user to login page.
            # TODO: change /hollyrosa
            environ['repoze.who.application'] = HTTPFound(
                location='?'.join(('/hollyrosa/login', urlencode(params, True)))
            )

        return login

    def get_user(self, identity, userid):
        user = model.getHollyCouch().get('user.' + userid)
        if user:
            identity['user_level'] = user['level']
            identity['user_active'] = user['active']
        else:
            vgroup_list = getVisitingGroupByBoknr(model.getHollyCouch(), userid)
            if len(vgroup_list) > 0:
                user = vgroup_list[0].doc
        return user

    def get_groups(self, identity, userid):
        return []  ## [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return []  # ] [p.permission_name for p in identity['user'].permissions]


base_config.sa_auth.dbsession = None

base_config.sa_auth.authmetadata = ApplicationAuthMetadata(base_config.sa_auth)

# In case ApplicationAuthMetadata didn't find the user discard the whole identity.
# This might happen if logged-in users are deleted.
base_config['identity.allow_missing_user'] = False

# You can use a different repoze.who Authenticator if you want to
# change the way users can login
# base_config.sa_auth.authenticators = [('myauth', SomeAuthenticator()]

# You can add more repoze.who metadata providers to fetch
# user metadata.
# Remember to set base_config.sa_auth.authmetadata to None
# to disable authmetadata and use only your own metadata providers
# base_config.sa_auth.mdproviders = [('myprovider', SomeMDProvider()]

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'
##try:
##    # Enable DebugBar if available, install tgext.debugbar to turn it on
##    from tgext.debugbar import enable_debugbar
##    enable_debugbar(base_config)
##except ImportError:
##    pass
