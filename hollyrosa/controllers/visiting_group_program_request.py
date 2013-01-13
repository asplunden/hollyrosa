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
        
        program_request_data_dict = {'identifier': 'id', 'items': [[{'id':0, 'requested_date': visiting_group_o['from_date'], 'requested_time':'', 'requested_activity': '', 'age_sma':False, 'age_spar':False, 'age_uppt':False, 'age_aven':False, 'age_utm':False, 'age_rov':False, 'age_led':False, 'note':''} for i in range(35)]] }
    
        
        
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
        log.debug(miniscout)
        log.debug(have_skippers)
        log.debug(ready_to_process)

        #log.debug('program request:'+program_request_input)
        #log.debug('program_json: ' + str( json.loads(program_request_input) ) )
        
        #log.debug('age group:' + age_group_input)
        #log.debug('age_json: ' + str( json.loads(age_group_input) ) )
        
        
        visiting_group_o = holly_couch[str(vgroup_id)]
        
        
        may_change_request_data = (0  == visiting_group_o['boknstatus'])
        visiting_group_o['contact_person'] = contact_person
        visiting_group_o['contact_person_email'] = contact_person_email
        visiting_group_o['contact_person_phone'] = contact_person_phone

        if may_change_request_data:    
            visiting_group_o['program_request_info'] = program_request_info
            visiting_group_o['program_request_miniscout'] = miniscout
            visiting_group_o['program_request_have_skippers'] = have_skippers
            visiting_group_o['program_request_age_group'] = age_group_input
            visiting_group_o['program_request'] = program_request_input
            
            #...SOME PROCESSING SHOULD ONLY BE DONE IF READY TO SHIP
            if 'on' == ready_to_process:
                visiting_group_o['boknstatus'] = 5 # todo: use constant
        
        
        #...load properties dict:
        log.debug(visiting_group_o['visiting_group_properties'])        
        
        #...iterate through age_group_data, items is a list of dicts...
        age_group_data = json.loads(age_group_input)
        age_group_data_items = age_group_data['items']
        
        #...WE should process the properties of the submitted form, not the other way around
        
        for tmp_vgroup_property in visiting_group_o['visiting_group_properties'].values():
            log.debug('processing property:' + str(tmp_vgroup_property['property']) )
            tmp_property_prop = tmp_vgroup_property['property']
            log.debug('old: ' + str(tmp_property_prop) + '=' + str(tmp_vgroup_property['value']))
            property_found = False
            for tmp_new_prop in age_group_data_items:
                if tmp_new_prop['property'] == tmp_property_prop:
                    property_found = True                    
                    break
                    #...IF we dont find it ?? and if value is null ?
            if property_found:
                tmp_vgroup_property['value'] = tmp_new_prop['value']
                log.debug('new: ' + str(tmp_property_prop) + '=' + str(tmp_vgroup_property['value']))
                #...ALSO MOVE DATES!
            else:
                log.debug('property not found, what do we do?')
                
                if 0 == tmp_new_prop['value']:
                    log.debug('never mind, value is zero')
                else:
                    #...we need to add an entry in the dict, first we need to know the lowest key number
                    lowest_key_number = 0
                    for tmp_key in visiting_group_o['visiting_group_properties'].keys():
                        if tmp_key > lowest_key_number:
                            lowest_key_number = tmp_key
                    lowest_key_number +=1
                            
                    new_property_row = {u'description': tmp_new_prop['age_group'], u'value': tmp_new_prop['value'], u'from_date': tmp_new_prop['from_date'], u'to_date': tmp_new_prop['to_date'], u'property': tmp_new_prop['property'], u'unit': tmp_new_prop['unit']}
                    visiting_group_o['visiting_group_properties'][lowest_key_number] = new_property_row
                
            # SAVE and make sure values are propagated
            
        
        # what do we do when the group finalizes its data (and what isnt alllowed after finalize. Its only state new that they can edit in. really.)
        #
        #
        # first, be ready to SANITIZE things like DATE RANGES 
        # 
        # for the program request , iterate through it
        #
        # for each entry create a new booking object. Cant be that hard, we now the valid_from and valid_to.
        # we have a reuested_date as well as note.
        # for each checkbox we know the propery , like age_spar is spar so write $$spar
        # 
        # $$spar + $$uppt (onskar <activity> <date> <time>) - SIMPLE!
        # 
        # just store list of booking requests to db and we are ready to schedule!
        #
        #
        # it would be really cool if I actually could put them in as preliminary bookings from the start. For that I need to look up slot_id and booking_day_id
        # booking_day_id can be looked up from date, and slot_id is trickier. first the schema of booking_day has to be found, 
        # then we need to look up the activity_id of activity and then we need to find slot_id as a function of time and activity_id. But if it can be done
        # it would be really really cool.
        #
        # It would be a great step towards 2014 version with the improved 4-1 schedule view
        #
              
        #...raise...redirect referer...
        