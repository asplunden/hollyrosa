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

import pylons
from tg import expose, flash, require, url, request, redirect,  validate
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch
from hollyrosa.widgets.edit_visiting_group_program_request_form import create_edit_visiting_group_program_request_form
from tg import tmpl_context

import datetime,logging

log = logging.getLogger()

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId

from hollyrosa.model.booking_couch import genUID 
from hollyrosa.controllers.booking_history import remember_tag_change
from formencode import validators

__all__ = ['visiting_group_program_request']


class VisitingGroupProgramRequest(BaseController):
    @expose('hollyrosa.templates.visiting_group_program_request_login')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))    
    def login(self):
        return dict()    
        
    
    @expose('hollyrosa.templates.visiting_group_program_request_edit')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def edit(self):
        tmpl_context.form = create_edit_visiting_group_program_request_form
        vgpr = dict()
        vgpr['name'] = 'test vgroup'
        return dict(visiting_group_program_request=vgpr)
        
        
    @expose('hollyrosa.templates.visiting_group_program_request_edit')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def view2(self):
        return dict(visiting_group_program_request=visiting_group_program_request)
        
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def update_visiting_group_program_request(self, info='', contact_person='', contact_person_email='', contact_person_phone='', program_request_div_input='', id='', age_group_div_input='', agegroup_store=''):
        log.debug('update')
        log.debug(info)
        log.debug(contact_person)
        log.debug(contact_person_email)
        log.debug(contact_person_phone)

        log.debug('program request:'+program_request_div_input)
        log.debug('age group:' + age_group_div_input)
        log.debug(agegroup_store)        
