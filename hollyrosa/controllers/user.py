# -*- coding: utf-8 -*-
"""
Copyright 2010-2020 Martin Eliasson

This file is part of Hollyrosa

Hollyrosa is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Hollyrosa is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.

"""

import datetime, StringIO, time, hashlib, logging


from tg import expose, flash, require, url, request, redirect, validate, abort
from formencode import validators
from tg.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, getHollyCouch


#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context



from hollyrosa.widgets.change_password_form import create_change_password_form
from hollyrosa.widgets.edit_user_form import create_edit_user_form


from booking_history import  remember_workflow_state_change
from hollyrosa.controllers.common import workflow_map,  getLoggedInUser,  getRenderContent,  has_level, ensurePostRequest

from hollyrosa.model.booking_couch import getAllUsers, getAllActiveUsers
from hollyrosa.controllers.common_couch import getCouchDBDocument

log = logging.getLogger(__name__)
__all__ = ['User']



class User(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)


    @expose('hollyrosa.templates.tools.list_users')
    @validate(validators={'show_deactive':validators.StringBool(not_empty=False)})
    @require(Any(has_level('staff'), has_level('pl'), msg='Only staff and pl may look at user listings'))
    def show(self, show_deactive=False):
        """Show an overview of all users"""

        all_users = [h.doc for h in getAllActiveUsers(getHollyCouch(), show_deactive=show_deactive)]
        return dict(users=all_users)


    @expose('hollyrosa.templates.tools.edit_user')
    @require(Any(has_level('pl'),  msg='Only PL can edit users right now'))
    def edit(self, user_id=''):
        """edit user properties"""
        tmpl_context.form = create_edit_user_form
        user_o = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)
        user_o['user_id'] = user_o['_id']
        return dict(user=user_o)


    @expose('hollyrosa.templates.tools.edit_user')
    @require(Any(has_level('pl'),  msg='Only PL can create users right now'))
    def new(self, user_id=''):
        """New user"""
        #user_id = '' # safety measure since we get a user id from the user who requested a user creation
        tmpl_context.form = create_edit_user_form
        user_o = dict(type='user', level=[])
        return dict(user=user_o)


    @expose()
    @validate(validators={'id':validators.UnicodeString(not_empty=False), 'user_name':validators.UnicodeString(not_empty=True), 'display_name':validators.UnicodeString(not_empty=True)})
    @require(Any(has_level('pl'),  msg='Only PL can save user properties right now'))
    def save_user(self, user_id='', display_name='', user_name=''):
        log.info("save_user()")
        ensurePostRequest(request, __name__)
        """edit user properties"""
        if user_id != '':
            user_o = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)
        else:
            user_o = dict(type='user', active=True)
            user_id = 'user.'+user_name
        user_o['display_name'] = display_name
        user_o['user_name'] = user_name
        user_o['level'] = []

        getHollyCouch()[user_id] = user_o

        raise redirect('show')



    @expose()
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False), 'level':validators.UnicodeString(not_empty=True)})
    @require(Any(has_level('pl'),  msg='Only PL can change user levels for other users'))
    def set_level(self, user_id='', level=''):
        log.info("set_level()")
        ensurePostRequest(request, __name__)
        user_o = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)

        # Rules for setting levels.
        # TODO: refactor out
        level_map = dict()
        level_map['viewer'] = ['view']
        level_map['staff'] = ['view','staff']
        level_map['pl'] = ['view','staff','pl']

        user_o['level'] = level_map.get(level,[])
        getHollyCouch()[user_id] = user_o

        raise redirect(request.referrer)


    @expose()
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(has_level('pl'),  msg='Only PL can change user levels for other users'))
    def deactivate(self, user_id=''):
        log.info("deactivate()")
        ensurePostRequest(request, __name__)
        user_o = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)

        # Rules for setting levels.
        user_o['active'] = False
        getHollyCouch()[user_id] = user_o

        raise redirect(request.referrer)


    @expose()
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(has_level('pl'),  msg='Only PL can change user levels for other users'))
    def activate(self, user_id=''):
        log.info("activate()")
        ensurePostRequest(request, __name__)
        user_o = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)

        # Rules for setting levels.
        user_o['active'] = True
        getHollyCouch()[user_id] = user_o

        raise redirect(request.referrer)


    @expose('hollyrosa.templates.tools.change_password')
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(has_level('pl'),  msg='Only PL can change passwords'))
    def change_password(self, user_id):
        tmpl_context.form = create_change_password_form
        user_o = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)

        return dict(user=dict(user_id=user_id), user_name=user_o['user_name'])


    @expose()
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(has_level('pl'), msg='Only PL can change passwords'))
    def update_password(self, user_id, password, password2):
        log.info("update_password()")
        ensurePostRequest(request, __name__)
        if not password==password2:
            raise IOError, 'passwords must agree'

        s = getCouchDBDocument(getHollyCouch(), user_id, doc_type='user') #, doc_subtype=None)

        # todo make salt part of development.ini
        h = hashlib.sha256('gninyd') # salt # TODO: read from AppConfig / tg.config
        h.update(password)
        c = h.hexdigest()
        s['password'] = c
        getHollyCouch()[user_id] = s
        raise redirect('show')
