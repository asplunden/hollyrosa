# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012 Martin Eliasson

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

#import pylons
from tg import expose, flash, require, url, request, redirect,  validate
from formencode import validators
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, holly_couch
from hollyrosa.widgets.change_password_form import create_change_password_form
from hollyrosa.widgets.edit_user_form import create_edit_user_form

import datetime,  StringIO,  time

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context
import hashlib

from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking

from booking_history import  remember_workflow_state_change
from hollyrosa.controllers.common import workflow_map,  getLoggedInUser,  getRenderContent,  has_level

from hollyrosa.model.booking_couch import getAllUsers

__all__ = ['User']

workflow_submenu = """<ul class="any_menu">
        <li><a href="overview">overview</a></li>
        <li><a href="view_nonapproved">non-approved</a></li>
        <li><a href="view_unscheduled">unscheduled</a></li>
        <li><a href="view_scheduled">scheduled</a></li>
        <li><a href="view_disapproved">dissapproved</a></li>
    </ul>"""

class User(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
    
    
    @expose('hollyrosa.templates.list_users')
    @require(Any(has_level('pl'),  msg='Only PL can take a look at booking statistics'))
    def show(self):
        """Show an overview of all users"""
        all_users = [h.doc for h in getAllUsers(holly_couch)]
        return dict(users=all_users)
        

    @expose('hollyrosa.templates.edit_user')
    @require(Any(has_level('pl'),  msg='Only PL can edit users right now'))
    def edit(self, user_id=''):
        """edit user properties"""
        tmpl_context.form = create_edit_user_form        
        user_o = holly_couch[user_id]
        levels = ['viewer','staff','pl'] # todo: make parameter, perhaps in db
        return dict(user=user_o, levels=levels)

         
    @expose()   
    @validate(validators={'_id':validators.UnicodeString(not_empty=False), 'user_name':validators.UnicodeString(not_empty=True), 'display_name':validators.UnicodeString(not_empty=True)})
    @require(Any(has_level('pl'),  msg='Only PL can save user properties right now'))
    def save_user(self, _id='', display_name='', user_name='', level=''):
        """edit user properties""" 
        if _id != '':
            user_o = holly_couch[_id]
        else:
            user_o = dict(type='user', level=['viewer','staff'])
            _id = 'user.'+user_name
        user_o['display_name'] = display_name
        user_o['user_name'] = user_name
        
        holly_couch[_id] = user_o
        
#       levels = ['viewer','staff','pl'] # todo: make parameter, perhaps in db
        raise redirect('show')
    
    
        
    @expose('hollyrosa.templates.change_password')
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('pl'),  msg='Only PL can change passwords'))    
    def change_password(self, user_id):
        tmpl_context.form = create_change_password_form
        user_o = holly_couch[user_id]
        
        if not user_o['type'] == 'user':
            raise IOError, 'document must be of type user'
            
        return dict(user=dict(user_id=user_id), user_name=user_o['user_name'])
    
        
    @expose()
    @validate(validators={'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can change passwords'))
    def update_password(self, user_id, password, password2):
        
        if not password==password2:
            raise IOError, 'passwords must agree'
 
 
        s = holly_couch[user_id]
        if not s['type'] == 'user':
            raise IOError, 'document must be of type user'

        h = hashlib.sha256('gninyd') # salt
        h.update(password)
        c = h.hexdigest()
        s['password'] = c
        holly_couch[user_id] = s
        raise redirect('/')


    