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
from hollyrosa.widgets.edit_vodb_group_form import create_edit_vodb_group_form
from tg import tmpl_context

import datetime,logging, json, time, types

log = logging.getLogger()

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId, reFormatDate

from hollyrosa.model.booking_couch import genUID, getBookingDayOfDate, getSchemaSlotActivityMap, getVisitingGroupByBoknr, getAllVisitingGroups, getTargetNumberOfNotesMap, getAllTags, getNotesForTarget
from hollyrosa.controllers.booking_history import remember_tag_change
from hollyrosa.controllers.common import workflow_map,  DataContainer,  getLoggedInUserId,  change_op_map,  getRenderContent, getRenderContentDict,  computeCacheContent,  has_level,  reFormatDate, bokn_status_map, make_object_of_vgdictionary
from hollyrosa.controllers.booking_history import remember_new_booking_request

from formencode import validators

__all__ = ['VODBGroup']


vodb_eat_times = [u'frukost',u'lunch',u'middag',u'kvällsfika']
vodb_eat_times_options = ['inne','ute','egen']
vodb_live_times_options = ['inne','ute','daytrip']
#vodb_live_cols = 

class VODBGroup(BaseController):
    
    #
    #...list all groups...Borrow from Visiting group.... need to refactor out commons
    #   thinking that all groups share some very basic common stuff. at least they should in the long run
    #
    #   think about what in the template should be different...
    

    @expose('hollyrosa.templates.vodb_group_view_all')
    @require(Any(is_user('erspl'), has_level('staff'), msg='Only staff members and viewers may view visiting group properties'))
    def view_all(self):
        visiting_groups = [v.doc for v in getAllVisitingGroups(holly_couch)] 
        remaining_visiting_groups_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=remaining_visiting_groups_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


  
    @expose('hollyrosa.templates.vodb_group_edit')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def edit_group_data(self, visiting_group_id=''):
        visiting_group_x = holly_couch[visiting_group_id]
        tmpl_context.form = create_edit_vodb_group_form
        
        #...construct the age group list. It's going to be a json document. Hard coded.
        #... if we are to partially load from database and check that we can process it, we do need to go from python to json. (and back)
        #...construct a program request template. It's going to be a json document. Hard coded.
        
        
        
        if not visiting_group_x.has_key('vodb_status'):
            visiting_group_x['vodb_status'] = 0
        
        for k in ['vodb_contact_name', 'vodb_contact_email', 'vodb_contact_phone', 'vodb_contact_address']:
            if not visiting_group_x.has_key(k):
                visiting_group_x[k] = ''
                
        visiting_group_o = make_object_of_vgdictionary(visiting_group_x)
         
        return dict(vodb_group=visiting_group_o, reFormatDate=reFormatDate, bokn_status_map=workflow_map)
        
        
    def dateGen(self, from_date, to_date):
        tmp_result = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        
        yield from_date
        delta = datetime.timedelta(1) #).strftime('%Y-%m-%d')        
        tmp_result_str = from_date        
        while tmp_result_str != to_date:
            tmp_result = tmp_result + delta
            tmp_result_str = tmp_result.strftime('%Y-%m-%d')
            yield tmp_result_str
        
    
        
    def make_empty_vodb_table(self, from_date, to_date, times, cols):
        """
        makes an empty table with all date-times for the live table
        """
    
        r1_items = list()
        #rid = lowest_rid
        for tmp_date in self.dateGen(from_date, to_date):
            for tmp_time in times:
                it = dict(date=tmp_date, time=tmp_time)
                it['rid'] = self.get_composite_key(it)
                for tmp_col in cols:
                    it[tmp_col] = 0
                    
                r1_items.append(it)
                #rid += 1

        return dict(identifier='rid', items=r1_items)
        
        
    def make_empty_vodb_live_table(self, from_date, to_date):
        return self.make_empty_vodb_table(from_date, to_date, [u'fm',u'em',u'kväll'], ['inne','ute','daytrip'])
        
    def make_empty_vodb_eat_table(self, from_date, to_date):
        return self.make_empty_vodb_table(from_date, to_date, vodb_eat_times, vodb_eat_times_options)
        

    
    
    def get_composite_key(self, row):
        # refactor out
        # store composite key and use it as rid and things will go much faster.
        d = dict()
        d[u'fm']=u'1'
        d[u'em']=u'2'
        d[u'kväll']=u'3'
        d[u'frukost'] = u'10'
        d[u'lunch'] = u'11'
        d[u'middag'] = u'12'
        d[u'kvällsfika'] = u'13'
        
        return row['date'] + u'_' +d[row['time']]
        
        
    def fn_cmp_composite_key(self, a, b):
        return cmp(self.get_composite_key(a), self.get_composite_key(b))
        
        
    # the expression del referrs to Data Eat Live. LED was too confusing so I choose DEL :)    
        
    @expose('hollyrosa.templates.vodb_group_edit_DEL_table')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def edit_group_DEL(self, visiting_group_id=''):
        visiting_group_o = holly_couch[visiting_group_id]
        tmpl_context.form = create_edit_vodb_group_form
        
        #...construct the age group list. It's going to be a json document. Hard coded.
        #... if we are to partially load from database and check that we can process it, we do need to go from python to json. (and back)
        #...construct a program request template. It's going to be a json document. Hard coded.
        
        
        if not visiting_group_o.has_key('vodb_status'):
            visiting_group_o['vodb_status'] = 0
        for k in ['vodb_contact_name', 'vodb_contact_email', 'vodb_contact_phone', 'vodb_contact_address']:
            if not visiting_group_o.has_key(k):
                visiting_group_o[k] = ''
        
        #...step 1 - create some random data just to show you know what it looks like
        # the real tricky part is to construct that merge part that does two things:
        # 1. we cant have rows with dates outside the range
        # 2. if we miss rows with certain dates, we should insert them
        live_data = visiting_group_o.get('vodb_live_table', dict(identifier='rid', items=[]))
        empty_vodb_live_table = self.make_empty_vodb_live_table(visiting_group_o['from_date'], visiting_group_o['to_date'])
        row_lookup = dict()
        for tmp_row in empty_vodb_live_table['items']:
            row_lookup[tmp_row['rid']] = tmp_row
        
        for tmp_row in live_data['items']:
            composite_key = tmp_row['rid']  ##self.get_composite_key(tmp_row) 
            if row_lookup.has_key(composite_key):
                del row_lookup[composite_key]
            
        for row_left in row_lookup.values():
            live_data['items'].append(row_left)
            
        #...re-sort the rows!
        live_data_items = live_data['items']
        live_data_items.sort(self.fn_cmp_composite_key)
        live_data['items'] = live_data_items

        # todo        
        # tags in yellow box
        # What do we do with tag data when a tag is deleted?
        # What do we do with tag data when a tag is added
        # Data for non existing tag, shouldnt it be shown anyway? 
        # Can we purge data that has no tag associated?
        #
        # When later saving all this, we should compute a cache content that can be used in future queries / views so we 
        # can start compute collected information
        #
        #
        # first of all, a general mega overview...
        #
        # we also soon will need som kind of subtyping
        
        
             
        eat_data = visiting_group_o.get('vodb_eat_table', dict(identifier='rid', items=[]))     
        empty_vodb_eat_table = self.make_empty_vodb_eat_table(visiting_group_o['from_date'], visiting_group_o['to_date'])
        row_lookup = dict()
        for tmp_row in empty_vodb_eat_table['items']:
            row_lookup[tmp_row['rid']] = tmp_row
        
        for tmp_row in eat_data['items']:
            composite_key = tmp_row['rid'] 
            if row_lookup.has_key(composite_key):
                del row_lookup[composite_key]
            
        for row_left in row_lookup.values():
            eat_data['items'].append(row_left)
            
        #...re-sort the rows!
        eat_data_items = eat_data['items']
        eat_data_items.sort(self.fn_cmp_composite_key)
        eat_data['items'] = eat_data_items
            
        
        
        #...fix the occu table
        occu_data = visiting_group_o.get('vodb_occu_table', dict(identifier='rid', items=[]))     
                
        all_current_vgroup_tags = dict()
        for tmp_key in visiting_group_o['tags']:
            all_current_vgroup_tags[tmp_key] = 1
            
        for tmp_row in occu_data['items']:
            for tmp_key in tmp_row.keys():
                if ((tmp_key != 'date') and (tmp_key != 'time')):
                    if not all_current_vgroup_tags.has_key(tmp_key):
                        all_current_vgroup_tags[tmp_key] = 1
        
        empty_vodb_occu_table = self.make_empty_vodb_table(visiting_group_o['from_date'], visiting_group_o['to_date'],[u'fm',u'em',u'kväll'], all_current_vgroup_tags.keys()) 
        
        row_lookup = dict()
        for tmp_row in empty_vodb_occu_table['items']:
            row_lookup[tmp_row['rid']] = tmp_row
        
        for tmp_row in occu_data['items']:
            composite_key = tmp_row['rid'] 
            if row_lookup.has_key(composite_key):
                del row_lookup[composite_key]
            
        for row_left in row_lookup.values():
            occu_data['items'].append(row_left)
            
        #...re-sort the rows!
        occu_data_items = occu_data['items']
        occu_data_items.sort(self.fn_cmp_composite_key)
        occu_data['items'] = occu_data_items
        
        
        
        
        
        visiting_group_o['vodb_live_table'] = json.dumps( live_data )
        visiting_group_o.vodb_eat_table = json.dumps( eat_data )
        visiting_group_o.vodb_occu_table = json.dumps( occu_data )
        
        
        #...we also must fix the occu_grid layout since its dynamic
        
        occu_layout_tags = json.dumps(visiting_group_o['tags'])
    
        
        
        
        
        return dict(vodb_group=visiting_group_o, occu_layout_tags=occu_layout_tags, reFormatDate=reFormatDate, bokn_status_map=workflow_map)
    
    
                    
    def vodb_table_property_substitution(self, rows, headers, properties):
        """
        WEE NEED TO TRIGGER THIS IF ANY PROPERTIES EVER CHANGE
        """
        for row in rows:
            for k in headers:
                #log.debug('headers:'+str(type(k)))
                original_value = row.get(k,0)
                log.debug('original value: ' + str(original_value))
                if type(original_value) == types.StringType or type(original_value) == types.UnicodeType:
                    log.debug('IS STRING TYPE')
                    for prop in properties.values():
                        log.debug(str(prop))
                        prop_prop = prop['property']
                        # todo: WARN IF DATE IS OUTSIDE RANGE
                        
                        new_value = original_value.replace(u'$'+prop_prop, prop['value']) 
                        
                        try:
                            new_value = int(new_value)
                        except ValueError:
                        	 pass
                        original_value = new_value # sadly no better idea
                        log.debug(str(original_value))                        
                        break
                        
                row[k] = original_value
        
    @expose()
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def update_group_tables(self, vgroup_id='', occu_table=None, eat_table=None, live_table=None, saveButton=''):
        # todo: accessor function making sure the type really is visiting_group
        visiting_group_o = holly_couch[vgroup_id] 
        
        if eat_table != None:
            vodb_eat_table = json.loads(eat_table)
            visiting_group_o['vodb_eat_table'] = vodb_eat_table
                        
            #...create cache content. Substitute properties and make sure we have at least zeros in all columns
            vodb_eat_computed = vodb_eat_table['items']            
            self.vodb_table_property_substitution(vodb_eat_computed, vodb_eat_times_options, visiting_group_o['visiting_group_properties'])
            
            visiting_group_o['vodb_eat_computed'] = vodb_eat_computed

        if live_table != None:
            vodb_live_table = json.loads(live_table)
            visiting_group_o['vodb_live_table'] = vodb_live_table
            vodb_live_computed = vodb_live_table['items']
            self.vodb_table_property_substitution(vodb_live_computed, vodb_live_times_options, visiting_group_o['visiting_group_properties'])
            visiting_group_o['vodb_live_computed'] = vodb_live_computed
              
            

        if occu_table != None:
            vodb_occu_table = json.loads(occu_table)
            visiting_group_o['vodb_occu_table'] = vodb_occu_table
            vodb_occu_computed = vodb_occu_table['items']
            visiting_group_o['vodb_occu_computed'] = vodb_occu_computed
            	        
        holly_couch[vgroup_id] = visiting_group_o
        return
        
        
        
    @expose('hollyrosa.templates.vodb_group_view')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def view_vodb_group(self, visiting_group_id=''):
        visiting_group_o = holly_couch[visiting_group_id]
        
        #...construct the age group list. It's going to be a json document. Hard coded.
        #... if we are to partially load from database and check that we can process it, we do need to go from python to json. (and back)
        #...construct a program request template. It's going to be a json document. Hard coded.
        notes = [n.doc for n in getNotesForTarget(holly_couch, visiting_group_id)]
        return dict(visiting_group=visiting_group_o, reFormatDate=reFormatDate, vodb_state_map=bokn_status_map, program_state_map=bokn_status_map, notes=notes)
        
        
        
    @expose('hollyrosa.templates.visiting_group_program_request_edit2')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), has_level('vgroup'), msg=u'Du måste vara inloggad för att få ändra i dina programönskemål'))    
    def edit_request(self, visiting_group_id=''):     	
        visiting_group_o = holly_couch[str(visiting_group_id)] 
        visiting_group_o.program_request_info = visiting_group_o.get('program_request_info','message to program!')
        visiting_group_o.program_request_have_skippers = visiting_group_o.get('program_request_have_skippers',0)
        visiting_group_o.program_request_miniscout = visiting_group_o.get('program_request_miniscout',0)
        
        #...construct a program request template. It's going to be a json document. Hard coded.
        #...supply booking request if it exists
        
        
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
        
        return dict(visiting_group_program_request=visiting_group_o, reFormatDate=reFormatDate, bokn_status_map=bokn_status_map)
        

        #
        # It would be a great step towards 2014 version with the improved 4-1 schedule view
        #
              
        #...raise...redirect referer...
        