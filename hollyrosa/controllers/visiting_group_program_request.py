# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012, 2013 Martin Eliasson

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

import datetime,logging, json

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
        vgpr['info'] = 'this is some info text'
        vgpr['contact_person'] = 'john doe'
        vgpr['from_date'] = '2012-06-01' 
        vgpr['to_date'] = '2012-06-06'
        
        #...construct the age group list. It's going to be a json document. Hard coded.
        #... if we are to partially load from database and check that we can process it, we do need to go from python to json. (and back)
        
        
        #vgpr['age_group_data'] = age_group_data
        
        #...construct a program request template. It's going to be a json document. Hard coded.
        
        return dict(visiting_group_program_request=vgpr)
        
        
        
    @expose('hollyrosa.templates.visiting_group_program_request_edit2')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def edit_request(self, visiting_group_id=''):     	
        visiting_group_o = holly_couch[str(visiting_group_id)] 
        visiting_group_o.program_request_info = visiting_group_o.get('program_request_info','message to program!')
        visiting_group_o.program_request_have_skippers = visiting_group_o.get('program_request_have_skippers',0)
        visiting_group_o.program_request_miniscout = visiting_group_o.get('program_request_miniscout',0)
        
        #...construct a program request template. It's going to be a json document. Hard coded.
        #...supply booking request if it exists
        
        age_group_data_raw = """{
	"identifier": "property",
	"items": [
		{
			"property": "barn",
			"unit": "smabarn",
			"age": "0-7",
			"age_group": "Smabarn",
			"value": 0,
			"from_date": "",
			"to_date": ""
		},
		{
			"property": "spar",
			"unit": "spar",
			"age": "8-9",
			"age_group": "Sparare",
			"value": 0,
			"from_date": "",
			"to_date": ""
		},
		{
			"property": "uppt",
			"unit": "uppt",
			"age": "10-11",
			"age_group": "Upptackare",
			"value": 0,
			"from_date": "",
			"to_date": ""
		},
		{
			"property": "aven",
			"unit": "aven",
			"age": "12-15",
			"age_group": "Aventyrare",
			"value": 0,
			"from_date": "",
			"to_date": ""
		},
		{
			"property": "utm",
			"unit": "utm",
			"age": "16-18",
			"age_group": "Utmanare",
			"value": 0,
			"from_date": "",
			"to_date": ""
		},
		{
			"property": "rover",
			"unit": "rover",
			"age": "18-25",
			"age_group": "Rover",
			"value": 0,
			"from_date": "",
			"to_date": ""
		},
		{
			"property": "led",
			"unit": "ledare",
			"age": "---",
			"age_group": "Ledare",
			"value": 0,
			"from_date": "",
			"to_date": ""
		}
	]
}"""
        age_group_data_tmp = json.loads(age_group_data_raw)
        for tmp_item in age_group_data_tmp['items']:
        	log.debug('TMP ITEM' + str( tmp_item ))
        	tmp_item['from_date'] = visiting_group_o['from_date']
        	tmp_item['to_date'] = visiting_group_o['to_date']
        
        age_group_data = json.dumps(age_group_data_tmp)
        visiting_group_o.program_request_age_group = visiting_group_o.get('program_request_age_group', age_group_data)
        
        program_request_data_dict = {'identifier': 'id', 'items': [ {'id':0, 'requested_date': visiting_group_o['from_date'], 'requested_time':'', 'requested_activity': '', 'age_sma':False, 'age_spar':False, 'age_uppt':False, 'age_aven':False, 'age_utm':False, 'age_rov':False, 'age_led':False, 'note':''} ]}
    
        
        
        program_request_data = json.dumps(program_request_data_dict)
        visiting_group_o.program_request = visiting_group_o.get('program_request', program_request_data)
        
        return dict(visiting_group_program_request=visiting_group_o)
        
    @expose('hollyrosa.templates.visiting_group_program_request_edit')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def view2(self):
        return dict(visiting_group_program_request=visiting_group_program_request)
        
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def update_visiting_group_program_request(self, program_request_info='', contact_person='', contact_person_email='', contact_person_phone='', vgroup_id='', program_request_input='', have_skippers=False, miniscout=False, ready_to_process=False, age_group_input='', saveButton='', submitButton=''):
        log.debug('update')
        log.debug(contact_person)
        log.debug(contact_person_email)
        log.debug(contact_person_phone)
        log.debug(program_request_info)
        log.debug(ready_to_process)

        #log.debug('program request:'+program_request_input)
        #log.debug('program_json: ' + str( json.loads(program_request_input) ) )
        
        #log.debug('age group:' + age_group_input)
        #log.debug('age_json: ' + str( json.loads(age_group_input) ) )
        
        
        visiting_group_o = holly_couch[str(vgroup_id)] 
        visiting_group_o['contact_person'] = contact_person
        visiting_group_o['program_request_info'] = program_request_info
        visiting_group_o['contact_person_email'] = contact_person_email
        visiting_group_o['contact_person_phone'] = contact_person_phone
        visiting_group_o['program_request_miniscout'] = miniscout
        visiting_group_o['program_request_have_skippers'] = have_skippers
        visiting_group_o['program_request_age_group'] = age_group_input
        visiting_group_o['program_request'] = program_request_input
        holly_couch[str(vgroup_id)] = visiting_group_o
        
        
              
        
        #...how can we convert age group data into the visiting group data?
        
        #...how can we covert the saved program request into a preliminary program request?
        #   the text is going to be according to the true/false of the matrix
        #   the comment is going to be about requested 23/1 FM
        #   the date is the age group time span, unless it's unreasonable. 
        #   the requested date is the date as indicated by the date choice, unless its unreasonable
        #
        # visiting group name, and dates are according to preliminary booking
        #
        # info is made into a note and added to the visiting group.
        #
        #