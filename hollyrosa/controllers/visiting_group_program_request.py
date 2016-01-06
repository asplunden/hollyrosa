# -*- coding: utf-8 -*-
"""
Copyright 2010-2016 Martin Eliasson

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

import datetime,logging, json, time

log = logging.getLogger()

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId, reFormatDate,  sanitizeDate

from hollyrosa.model.booking_couch import genUID, getBookingDayOfDate, getSchemaSlotActivityMap, getVisitingGroupByBoknr
from hollyrosa.controllers.booking_history import remember_tag_change
from hollyrosa.controllers.common import workflow_map,  DataContainer,  getLoggedInUserId,  change_op_map,  getRenderContent, getRenderContentDict,  computeCacheContent,  has_level,  reFormatDate, bokn_status_map
from hollyrosa.controllers.booking_history import remember_new_booking_request
from hollyrosa.controllers import common_couch

from formencode import validators

__all__ = ['visiting_group_program_request']

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


validation_error_explanations = {}
validation_error_explanations['date_format'] = u"Det har blivit fel i formateringen av ett datum. Datum måste vara på formen YYYY-MM-DD. Det kan bero på att ett datum inte angivits, men troligare är det ett fel vi programmerare har gjort."
validation_error_explanations['date_range'] = u"Ett datum som angivits är inte innom rimliga gränser. Datumet kan exempelvis vara innan er grupp kommit till ön eller efter att den åkt hem igen."
validation_error_explanations['date_order'] = u"Ett datum-par, oftast från-datum och till-datum, är i fel kronologisk ordning. Det är lite orimligt att man åker hem innan man kommit ut till ön."
validation_error_explanations['req_fm_em'] = u"En rad bland bokningsförfrågningarna saknar val av tid på dagen (fm/em/kväll)"

def hasValidationErrors(vgroup):
    """This function is to be used from visiting group program request """
    if vgroup.has_key('validation_error_messages'):
        if len(vgroup['validation_error_messages']) != 0:
            return True
    return False
    

class ValidationErrorMessages(list):
    """This class is used in the external booking request to do custom validation of errors found in the rather complex data sent from the grids. 
    Typically, we have two dates and there are constraints on them."""
    
    def __init__(self):
        """The idea about explanations is to have a general explanation that can be used repeatedly but only shown once"""
        super(ValidationErrorMessages, self).__init__()
        self.explanations = dict()
    
    def report(self, section,  message,  problematic_value,  explanation_key):
        self.append(dict(section=section,  message=message,  problematic_value=problematic_value,  explanation_key=explanation_key))
        self.explanations[explanation_key] = validation_error_explanations[explanation_key]
    
    def hasErrors(self):
        return len(self) > 0
        


class VisitingGroupProgramRequest(BaseController):
    @expose()
    def login_vgroup(self, boknr=''):
        
        #lookup vgroup of boknr
        vgroup_list = getVisitingGroupByBoknr(holly_couch, boknr)
        if len(vgroup_list) == 0:
            flash(u"Det finns ingen grupp i systemet än med det bokningsnummer du angav.",'warning')
            raise redirect('/')
        else:
            raise redirect('edit_request', visiting_group_id=vgroup_list[0]['id'])
        return dict()
        
        
    @expose('hollyrosa.templates.visiting_group_program_request_edit2')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), has_level('vgroup'), msg=u'Du måste vara inloggad för att få ändra i dina programönskemål'))    
    def edit_request(self, visiting_group_id=''):     	
        visiting_group_o = holly_couch[str(visiting_group_id)] 
        visiting_group_o.program_request_info = visiting_group_o.get('program_request_info','message to program!')
        visiting_group_o.program_request_have_skippers = visiting_group_o.get('program_request_have_skippers',0)
        visiting_group_o.program_request_miniscout = visiting_group_o.get('program_request_miniscout',0)
        visiting_group_o.contact_person = visiting_group_o.get('contact_person','')
        visiting_group_o.contact_person_email = visiting_group_o.get('contact_person_email','')
        visiting_group_o.contact_person_phone = visiting_group_o.get('contact_person_phone','')

        #...construct a program request template. It's going to be a json document. Hard coded.
        #...supply booking request if it exists
        age_group_data_tmp = json.loads(age_group_data_raw)
        for tmp_item in age_group_data_tmp['items']:
            log.debug('TMP ITEM' + str( tmp_item ))
            tmp_item['from_date'] = visiting_group_o['from_date']
            tmp_item['to_date'] = visiting_group_o['to_date']
        
        age_group_data = json.dumps(age_group_data_tmp)
        visiting_group_o.program_request_age_group = visiting_group_o.get('program_request_age_group', age_group_data)
        
        program_request_data_dict = {'identifier': 'id', 'items': [{'id':str(i), 'requested_date': visiting_group_o['from_date'], 'requested_time':'', 'requested_activity': '', 'age_sma':False, 'age_spar':False, 'age_uppt':False, 'age_aven':False, 'age_utm':False, 'age_rov':False, 'age_led':False, 'note':''} for i in range(35)] }
    
        #program_request_data_dict = {'identifier': 'rid', 'items': []}
        
        program_request_data = json.dumps(program_request_data_dict)
        visiting_group_o.program_request = visiting_group_o.get('program_request', program_request_data)
        
        return dict(visiting_group_program_request=visiting_group_o, reFormatDate=reFormatDate, bokn_status_map=bokn_status_map,  hasValidationErrors=hasValidationErrors)
        
        
    @expose()
    @require(Any(has_level('pl'), has_level('vgroup'), msg=u'Du måste vara inloggad för att få spara programönskemål'))
    def update_visiting_group_program_request(self, program_request_info='', contact_person='', contact_person_email='', contact_person_phone='', vgroup_id='', program_request_input='', have_skippers=False, miniscout=False, ready_to_process=False, age_group_input='', saveButton='', submitButton=''):
        # TODO: once property data has changed, we somehow need to propagate that property data to all places where the properties are used BUT I dont think we really waht to propagate it unless we do some state-change,
        # we probably want to check the data before it is allowed to progress into other parts of the system.
        # TODO: We lost a lot of work, but our aim is to introduce the validation_error_messages list to contain all problems we have encountered.
        # what about making a subclassed list which can add speciealy formatted messages?
        # also, we should hav a comprehensive from-date-to-date checker
        #
        # dont forget to check for empty fm/em/evening
        # also common_couch code should be added
        #
        # make a validation_error_contect object that can be passed around and a date range checker and similar.
        # essentially we want to store section(1,2,3) property name and message. How to fix it.
        #
        #
        # 
        
        validation_error_messages = ValidationErrorMessages()
        
        visiting_group_id = str(vgroup_id)
        visiting_group_o = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
        
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
        
            #...iterate through age_group_data, items is a list of dicts...
            age_group_data = json.loads(age_group_input)
            age_group_data_items = age_group_data['items']
        
            #...We should process the properties of the submitted form, not the other way around
        
            for tmp_age_group in age_group_data_items:
                process_property = tmp_age_group['property']
                log.debug('processing property:' + process_property )

                tmp_vgroup_property = None
                property_found = False
                property_id = None
                for tmp_vgroup_property_id,  tmp_vgroup_property in visiting_group_o['visiting_group_properties'].items():
                    if tmp_vgroup_property['property'] == process_property:
                        property_found = True
                        property_id = tmp_vgroup_property
                        log.debug('*** property %ss match found, property_id=%s' % (process_property,  property_id))
                        break
            
                if property_found:
                    log.debug('old: ' + str(process_property) + '=' + str(tmp_vgroup_property['value']))
            
                    # TODO: maybe sanitize so value must be an int?
                    tmp_vgroup_property['value'] = tmp_age_group['value']
                    
                    #...check that dates are within valid ranges
                    ok_1,  tmp_vgroup_property['from_date'] = sanitizeDate(tmp_age_group['from_date'],  default_date=tmp_vgroup_property['from_date']  )
                    if not ok_1:
                        validation_error_messages.report('properties',  u'Från-datum som tillhör åldersgrupp %s har fel format.' % tmp_vgroup_property['property'], problematic_value=tmp_age_group['from_date'], explanation_key='date_format' )
                    ok_2,  tmp_vgroup_property['to_date'] = sanitizeDate(tmp_age_group['to_date'],  default_date=tmp_vgroup_property['to_date'] )
                    if not ok_2:
                        validation_error_messages.report('properties',  u'Till-datum som tillhör åldersgrupp %s har fel format.' % tmp_vgroup_property['property'], problematic_value=tmp_age_group['to_date'], explanation_key='date_format' )
                    ok_3 = (tmp_vgroup_property['to_date']  >=  tmp_vgroup_property['from_date'] )
                    if not ok_3:
                        validation_error_messages.report('properties',  u'Till-datum kan inte inträffa före från-datum, se datumen i åldersgruppen %s.' % tmp_vgroup_property['property'], problematic_value=tmp_age_group['from_date']  + ' - ' + tmp_age_group['from_date'], explanation_key='date_order' )
                    ok_4 = tmp_vgroup_property['from_date'] >= visiting_group_o['from_date']
                    if not ok_4:
                        validation_error_messages.report('properties',  u'Från-datum %s som tillhör åldersgrupp %s kan inte inträffa före från-datum %s för din grupp.' % (tmp_vgroup_property['from_date'],  tmp_vgroup_property['property'], visiting_group_o['from_date']), problematic_value=tmp_vgroup_property['from_date'],  explanation_key='date_range') 
                    ok_5 = tmp_vgroup_property['to_date'] <= visiting_group_o['to_date']
                    if not ok_5:
                        validation_error_messages.report('properties',  u'Till-datum %s som tillhör åldersgrupp %s kan inte inträffa efter från-datum %s för din grupp.' % (tmp_vgroup_property['to_date'],  tmp_vgroup_property['property'], visiting_group_o['to_date']), problematic_value=tmp_vgroup_property['to_date'],  explanation_key='date_range') 
                    
                    
                    
                    log.debug('new: ' + process_property + '=' + str(tmp_age_group['value']))
                    #visiting_group_o['visiting_group_properties'][property_id] = tmp_vgroup_property
                else: # property not found, new property
                    log.debug('property not found, what do we do?')
                
                    if 0 == tmp_age_group['value']:
                        log.debug('never mind, value is zero')
                    else:
                        #...we need to add an entry in the dict, first we need to know the lowest key number
                        lowest_key_number = 0
                        for tmp_key in visiting_group_o['visiting_group_properties'].keys():
                            if tmp_key > lowest_key_number:
                                lowest_key_number = int(tmp_key)
                        lowest_key_number +=1
                        
                        # TODO: Date sanitation here too
                        ok_6,  new_from_date = sanitizeDate(tmp_age_group['from_date'],  default_date=visiting_group_o['from_date'] )
                        if not ok_6:
                            validation_error_messages.report('properties',  u'Från-datum som tillhör åldersgrupp %s har fel format.' % tmp_vgroup_property['property'], problematic_value=tmp_age_group['from_date'], explanation_key='date_format' )
                        ok_7,  new_to_date = sanitizeDate(tmp_age_group['to_date'],  default_date=visiting_group_o['to_date'] )
                        if not ok_7:
                            validation_error_messages.report('properties',  u'Till-datum som tillhör åldersgrupp %s har fel format.' % tmp_vgroup_property['property'], problematic_value=tmp_age_group['to_date'], explanation_key='date_format' )
                            
                        ok_8 = (new_from_date <= new_to_date)
                        if not ok_8:
                            validation_error_messages.report('properties',  u'Till-datum kan inte inträffa före från-datum, se datumen i åldersgruppen %s.' % tmp_vgroup_property['property'], problematic_value=tmp_age_group['from_date']  + ' - ' + tmp_age_group['from_date'], explanation_key='date_order' )
                        ok_9 = tmp_age_group['from_date'] >= visiting_group_o['from_date']
                        if not ok_9:
                            validation_error_messages.report('properties',  u'Från-datum %s som tillhör åldersgrupp %s kan inte inträffa före från-datum %s för din grupp.' % (tmp_vgroup_property['from_date'],  tmp_vgroup_property['property'], visiting_group_o['from_date']), problematic_value=tmp_vgroup_property['from_date'],  explanation_key='date_range') 
                        ok_10 = tmp_age_group['to_date'] <= visiting_group_o['to_date']
                        if not ok_10:
                            validation_error_messages.report('properties',  u'Till-datum %s som tillhör åldersgrupp %s kan inte inträffa efter från-datum %s för din grupp.' % (tmp_vgroup_property['to_date'],  tmp_vgroup_property['property'], visiting_group_o['to_date']), problematic_value=tmp_vgroup_property['to_date'],  explanation_key='date_range') 
                    
                        new_property_row = {u'description': tmp_age_group['age_group'], u'value': tmp_age_group['value'], u'from_date': new_from_date, u'to_date': new_to_date, u'property': tmp_age_group['property'], u'unit': tmp_age_group['unit']}
                        x = visiting_group_o['visiting_group_properties']
                        x[str(lowest_key_number)] = new_property_row
                        visiting_group_o['visiting_group_properties'] = x
            
            visiting_group_o['validation_error_messages'] = validation_error_messages
            visiting_group_o['validation_error_explanations'] = validation_error_messages.explanations
            holly_couch[visiting_group_o['_id']] = visiting_group_o
        
        # TODO: We should have a two step process: first construct all bookings (make a list) and if it all is successfull and no validation errors, thats when we actually write them to the db.
        
        # for the program request , iterate through it
        if may_change_request_data and not validation_error_messages.hasErrors():
            if 'True' == ready_to_process:
                program_request_list = json.loads(program_request_input)
                for tmp_request in program_request_list['items']:
                    log.debug('found request...' + str(tmp_request))
                    request_for_age_groups = [x[4:] for x in ['age_sma','age_spar','age_uppt','age_aven','age_utm','age_rov','age_led'] if tmp_request[x]]
                    
                    if len(request_for_age_groups) > 0:
                        
                        #...TODO: sanitize requested_date and make sure it is in range
                        ok_r1, requested_date = sanitizeDate(tmp_request['requested_date'][:10],  default_date='')
                        if not ok_r1:
                            validation_error_messages.report('booking request',  u'Det angivna önskade datumet %s har fel format.' % tmp_request['requested_date'], problematic_value=tmp_request['requested_date'],  explanation_key='date_format')
                        if not ((requested_date >= visiting_group_o['from_date']) and (requested_date <= visiting_group_o['to_date'])):
                            validation_error_messages.report('booking request',  u'Det efterfrågade datumet %s är inte mellan din grupps från- och till- datum.' % tmp_request['requested_date'], problematic_value=tmp_request['requested_date'],  explanation_key='date_range')
                        # TODO: reuse the parsing of the date
                        requested_date_o = time.strptime(requested_date, "%Y-%m-%d" )
                        requested_time = tmp_request['requested_time']
                        requested_activity_id = tmp_request['requested_activity']
                        
                        no_activity_selected = ('' == requested_activity_id)
                        
                        # TODO: what if there is no requested activity?
                        # TODO: how do users choose not to which anything after they have made a request? I think we actually will need a NULL request and this is where we among other things check the null request.
                        
                        booking_day_o = getBookingDayOfDate(holly_couch, requested_date)
                        log.debug(booking_day_o)
                        day_schema_id = booking_day_o['day_schema_id']
                        
                        #...TODO day shema will probably always be the same so just query once per schema
                        schema_o = common_couch.getDaySchema(holly_couch,  day_schema_id)                        
                        
                        #...given fm/em/evening, look up the matching slot_id. Probably the schema will be needed (and maybe index 0,1,2,3...)
                        tmp_activity_row = schema_o['schema'][requested_activity_id]
                        
                        #...look through the list, lets say we have a time and we need the slot id matching that time
                        #   then the reasonable way is too look through all list entries being dicts and return slot id when time match found
                        activity_selection_map = dict()
                        activity_selection_map['activity.30'] = u'Storbåt'
                        
                        time_selection_lookup = dict(FM='10:00:00', EM='15:00:00', EVENING='20:00:00')
                        
                        #...EVENING should be called Kväll
                        #   It should be possible to book just 'any' water program
                        #   these maps with id-text transaltion should maybe be available in the templating engine
                        #   dont forget to give the date formatter to the templating engine
                        
                        time_selection_translator = dict(EVENING=u'kväll')
                        if validation_error_messages.hasErrors():
                            holly_couch[visiting_group_o['_id']] = visiting_group_o
                            raise redirect(request.referrer)
                            
                        for tmp_slot_info in tmp_activity_row[1:]:
                            if (tmp_slot_info['time_from'] < time_selection_lookup[requested_time]) and (tmp_slot_info['time_to'] > time_selection_lookup[requested_time]):
                                match_slot_id = tmp_slot_info['slot_id']
                                log.debug('match for slot_id: ' + match_slot_id)
                                
                                # lets create a booking!
                                # TODO: refactor the creation of a new booking
                                new_booking = dict(type='booking',  valid_from='',  valid_to='',  requested_date=requested_date, slot_id=match_slot_id, booking_day_id=booking_day_o['_id'],  subtype='program')
                                new_booking['visiting_group_id'] = str(vgroup_id)
                                new_booking['valid_from'] = visiting_group_o['from_date']
                                new_booking['valid_to'] = visiting_group_o['to_date']
                                new_booking['reuested_date'] = requested_date
                                new_booking['visiting_group_name'] = visiting_group_o['name']
                                new_booking['last_changed_by_id'] = getLoggedInUserId(request)
                                
                                activity_o = common_couch.getActivity(holly_couch, requested_activity_id)
                                
                                # TODO: the line below gts the properties wrong
                                content = u'%s (önskar %s %d/%d %s) %s' % ( ' '.join(['$$%s'%a for a in request_for_age_groups ]) ,activity_selection_map.get(requested_activity_id, activity_o['title']), int(time.strftime("%d", requested_date_o)),  int(time.strftime("%m", requested_date_o)), time_selection_translator.get(requested_time, requested_time), tmp_request['note'] )                                 
                                
                                new_booking['content'] = content
                                new_booking['cache_content'] = computeCacheContent(holly_couch[visiting_group_id], content)
                                new_booking['activity_id'] = requested_activity_id
            
                                
                                new_booking['booking_state'] = activity_o['default_booking_state']                                
                                
                                slot_map  = getSchemaSlotActivityMap(holly_couch, booking_day_o, subtype='program')
                                slot = slot_map[match_slot_id]
                                new_uid = genUID(type='booking')
                                
                                #...here we create the booking
                                holly_couch[new_uid] = new_booking
                                
                                #...remember the created booking
                                
                                remember_new_booking_request(holly_couch, booking=new_booking, changed_by=getLoggedInUserId(request))
                                break
                                
                visiting_group_o['boknstatus'] = 5 # TODO: use constant
                holly_couch[visiting_group_o['_id']] = visiting_group_o
        raise redirect(request.referrer)
