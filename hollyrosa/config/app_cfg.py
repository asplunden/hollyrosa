# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in hollyrosa.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""
import logging,  sys
from tg.configuration import AppConfig

from zope.interface import implements
from repoze.who.interfaces import IAuthenticator, IMetadataProvider
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from repoze.who.middleware import PluggableAuthenticationMiddleware

import hollyrosa
from hollyrosa.model.booking_couch import getVisitingGroupByBoknr
from hollyrosa import model
from hollyrosa.lib import app_globals, helpers 
from hollyrosa.controllers.common import DataContainer
import hashlib

def validate_password(user, password):
    h = hashlib.sha256('gninyd') # salt
    h.update(password)
    c = h.hexdigest()
    return user['password'] == c


class CouchAuthenticatorPlugin(object):
    implements(IAuthenticator)
 
    # IAuthenticator
    def authenticate(self, environ, identity):
        if not ('login' in identity and 'password' in identity):
            return None
 
        login = identity.get('login')
        user = model.holly_couch.get('user.'+login)
        
        if user and validate_password(user, identity.get('password')):
            return identity['login']
        else:
            vgroup_list = getVisitingGroupByBoknr(model.holly_couch, login)
            if len(vgroup_list) > 0:
                #raise IOError, str(vgroup[0])
                vgroup = vgroup_list[0].doc
                if vgroup.has_key('password'):
                    #raise IOError, 'xxx'
                    if vgroup['password'] == identity.get('password'):
                        return identity['login']
           
        #...raise authentication error ???
        return None


class CouchUserMDPlugin(object):
    implements(IMetadataProvider)
    
    def add_metadata(self, environ, identity):
        ####user_data = {'user_name':identity['repoze.who.userid']}
        ###identity['user'] = db.users.find_one(user_data)
        user_name = identity['repoze.who.userid']
        user_doc = model.holly_couch.get('user.'+user_name)
        if user_doc:
            identity['user'] = user_doc
            identity['user_level'] = user_doc['level']
            identity['user_active'] = user_doc.get('active', False)
            return True
        else:
            vgroup_list = getVisitingGroupByBoknr(model.holly_couch, user_name)
            if len(vgroup_list) > 0:
                vgroup = vgroup_list[0].doc
            
                identity['user'] = vgroup # should we fabricate? 
                identity['user_level'] = "vgroup"
                return True
        return None 
               

class MyAppConfig(AppConfig):
    auth_backend = 'sqlalchemy' #this is a fake, but it's needed to enable
                                #auth middleware at least on TG2.0
 
    login_url = '/login'
    login_handler = '/login_handler'
    post_login_url = None
    logout_handler = '/logout_handler'
    post_logout_url = None
    login_counter_name = None
 
    def add_auth_middleware(self, app, skip_authentication):
        cookie_secret = base_config.get('auth_cookie_secret', 'hollyjhonson6g6')
        cookie_name = base_config.get('auth_cookie_name', 'hollyrosa_auth')
 
        who_args = {}
 
        form_plugin = FriendlyFormPlugin(self.login_url,
                              self.login_handler,
                              self.post_login_url,
                              self.logout_handler,
                              self.post_logout_url,
                              login_counter_name=self.login_counter_name, rememberer_name='cookie')
        challengers = [('form', form_plugin)]
 
        auth = CouchAuthenticatorPlugin()
        authenticators = [('couchauth', auth)]
 
        cookie = AuthTktCookiePlugin(cookie_secret, cookie_name)
 
        identifiers = [('cookie', cookie), ('form', form_plugin)]
 
        provider = CouchUserMDPlugin()
        mdproviders = [('couchprovider', provider)]
 
        from repoze.who.classifiers import default_request_classifier
        from repoze.who.classifiers import default_challenge_decider
        log_stream = None
 
        app = PluggableAuthenticationMiddleware(app,
                                          identifiers,
                                          authenticators,
                                          challengers,
                                          mdproviders,
                                          default_request_classifier,
                                          default_challenge_decider)
 
        return app




base_config = MyAppConfig()
base_config.renderers = []

base_config.package = hollyrosa

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = False
####base_config.model = hollyrosa.model
####base_config.DBSession = hollyrosa.model.DBSession


# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
base_config.sa_auth.cookie_secret = "ChangeME"

# Configure the authentication backend
####base_config.auth_backend = 'sqlalchemy'
####base_config.sa_auth.dbsession = model.DBSession
# what is the class you want to use to search for users in the database
####base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
####base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
####base_config.sa_auth.permission_class = model.Permission


# override this if you would like to provide a different who plugin for
# managing login and logout of your application
####base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
####base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
#####base_config.sa_auth.post_logout_url = '/post_logout'
