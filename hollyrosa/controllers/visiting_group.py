# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012, 2013, 2014 Martin Eliasson

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

from tg import expose, flash, require, url, request, redirect,  validate
from formencode import validators
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, holly_couch
from hollyrosa.model.booking_couch import getAllActivities,  getAllVisitingGroups,  getVisitingGroupsAtDate,  getVisitingGroupsInDatePeriod,  getBookingsOfVisitingGroup,  getSchemaSlotActivityMap,  getVisitingGroupsByBoknstatus, getNotesForTarget, getBookingInfoNotesOfUsedActivities
from hollyrosa.model.booking_couch import getBookingDays,  getAllVisitingGroupsNameAmongBookings, getAllTags, getDocumentsByTag, getVisitingGroupOfVisitingGroupName, getTargetNumberOfNotesMap, getVisitingGroupsByVodbState,  dateRange,  getActivityTitleMap,  getAllProgramLayerBucketTexts,  getProgramLayerBucketTextByDayAndTime
import datetime

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context


from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking
from hollyrosa.controllers.common import workflow_map,  bokn_status_map, bokn_status_options,  DataContainer,  getRenderContent, computeCacheContent,  has_level,  reFormatDate, getLoggedInUserId, makeVisitingGroupObjectOfVGDictionary, vodb_eat_times_options, vodb_live_times_options
from hollyrosa.controllers.visiting_group_common import populatePropertiesAndRemoveUnusedProperties,  updateBookingsCacheContentAfterPropertyChange,  updateVisitingGroupComputedSheets,  computeAllUsedVisitingGroupsTagsForTagSheet,  program_visiting_group_properties_template,  staff_visiting_group_properties_template,  course_visiting_group_properties_template
from hollyrosa.controllers.booking_history import remember_tag_change
from hollyrosa.controllers import common_couch

from tg import request, response
from tg.controllers import CUSTOM_CONTENT_TYPE

__all__ = ['VisitingGroup']


class VisitingGroupPropertyRow(object):
    """Used for supplying data to the properties row fields in edit visiting group and edit vodb group"""
    def __init__(self,  id,  property_row):
        self.id= id
        self.property = property_row['property']
        self.unit =property_row['unit']
        self.value = property_row['value']
        self.description = property_row['description']
        self.from_date = property_row['from_date']
        self.to_date = property_row['to_date']
    
    
class VisitingGroup(BaseController):

    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view(self, url):
        visiting_groups = [x.doc for x in getAllVisitingGroups(holly_couch)]
        visiting_group_names = [x['name'] for x in visiting_groups] 
        v_group_map = dict() 
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(),  bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


    def makeRemainingVisitingGroupsMap(self, visiting_groups,  from_date='',  to_date=''):
        v_group_map = dict()
        all_existing_names = getAllVisitingGroupsNameAmongBookings(holly_couch, from_date=from_date,  to_date=to_date)
        exisiting_vgroup_names = [n['name'] for n in visiting_groups]
        for b in all_existing_names:
                if b not in exisiting_vgroup_names:
                    v_group_map[b] = 1

        return v_group_map
    

    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'from_date':validators.DateValidator(not_empty=False), 'to_date':validators.DateValidator(not_empty=False)})
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_date_range(self,  from_date=None,  to_date=None):
        visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(holly_couch, from_date,  to_date)]
        v_group_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups,  from_date=fromdate,  to_date=todate)
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)

    
    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('erspl'), has_level('staff'),   msg='Only staff members and viewers may view visiting group properties'))
    def view_tags(self, tag):
        # TODO: rename and maybe only return visiting groups docs ?
        visiting_groups = [v.doc for v in getDocumentsByTag(holly_couch, tag)] 
        remaining_visiting_groups_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups)
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=remaining_visiting_groups_map.keys(), bokn_status_map=bokn_status_map,  vodb_state_map=bokn_status_map,  program_state_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)

    
    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('erspl'), has_level('staff'),   msg='Only staff members and viewers may view visiting group properties'))
    def view_all(self):
        visiting_groups = [v.doc for v in getAllVisitingGroups(holly_couch)] 
        remaining_visiting_groups_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups)        
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=remaining_visiting_groups_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'program_state':validators.Int(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_program_state(self,  program_state=None):
        visiting_groups =[v.doc for v in getVisitingGroupsByBoknstatus(holly_couch, program_state)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)  
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=v_group_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'vodb_state':validators.Int(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_vodb_state(self,  vodb_state=None):
        visiting_groups =[v.doc for v in getVisitingGroupsByVodbState(holly_couch, vodb_state)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)  
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=v_group_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)

        
    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'period':validators.String(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_period(self,  period=None):

        # TODO: refactor so we only show visiting groups in time span given by daterange document.
        if period == '1an':
            from_date='2011-01-01'
            to_date='2011-07-16'
            
            visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(holly_couch, from_date,  to_date)]
        elif period == '2an':
            from_date='2011-07-17'  
            to_date='2011-08-24'
            visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(holly_couch, from_date,  to_date)]

        else:
            from_date=''
            to_date=''
            visiting_groups = [v.doc for v in getAllVisitingGroups(holly_couch, from_date,  to_date)]
        
        v_group_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups,  from_date=from_date,  to_date=to_date) 
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


    @expose("json")
    def get_unbound_visiting_group_names(self, from_date='', to_date=''):
        v_group_map = self.makeRemainingVisitingGroupsMap([],  from_date=from_date,  to_date=to_date) 
        return dict(names=v_group_map)    


    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_today(self):
        at_date = datetime.datetime.today().strftime('%Y-%m-%d')
        visiting_groups = [v.doc for v in getVisitingGroupsAtDate(holly_couch, at_date)] 
        v_group_map = self.makeRemainingVisitingGroupsMap(visiting_groups,  from_date=at_date,  to_date=at_date)        
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)         
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map, program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, has_notes_map=has_notes_map, reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)])


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'at_date':validators.DateValidator(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_at_date(self,  at_date=None):
        visiting_groups = [v.doc for v in getVisitingGroupsAtDate(holly_couch, at_date)] 
        v_group_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups,  from_date=at_date,  to_date=at_date)
        has_notes_map = getTargetNumberOfNotesMap(holly_couch) 
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map, program_state_map=bokn_status_map)


    @expose("json")
    @validate(validators={'id':validators.UnicodeString})
    def show_visiting_group_data(self,  id=None,  **kw):
        
        properties=[]
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='')
            
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
            
        else:
            visiting_group = common_couch.getVisitingGroup(holly_couch,  id) 
            
            properties=[p for p in visiting_group['visiting_group_properties'].values()]
            
        return dict(visiting_group=visiting_group, properties=properties)
        
        
    @expose('hollyrosa.templates.visiting_group_view')
    @validate(validators={'visiting_group_id':validators.UnicodeString})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def show_visiting_group(self,  visiting_group_id=None,  **kw):
        
        if None == visiting_group_id:
            visiting_group = DataContainer(name='', id=None,  info='')
            bookings=[]
            notes=[]
        elif visiting_group_id=='':
            visiting_group = DataContainer(name='', id=None,  info='')
            bookings=[]
            notes=[]
        else:
            visiting_group = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)

            # TODO: there is no composite view any more showing both bookings and visiting group data
            bookings = [] 
            notes = [n.doc for n in getNotesForTarget(holly_couch, visiting_group_id)]
        return dict(visiting_group=visiting_group, bookings=bookings, workflow_map=workflow_map,  getRenderContent=getRenderContent, program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, notes=notes)


    @expose('hollyrosa.templates.edit_visiting_group')
    @validate(validators={'visiting_group_id':validators.UnicodeString,  'subtype':validators.UnicodeString})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def edit_visiting_group(self,  visiting_group_id=None, subtype='',  **kw):
        tmpl_context.form = create_edit_visiting_group_form
        
        is_new = ((None == visiting_group_id) or ('' == visiting_group_id))
        if is_new:
            properties_template = dict()
            
            if subtype == 'program':
                properties_template = program_visiting_group_properties_template
                
            if subtype == 'staff':
                properties_template = staff_visiting_group_properties_template
                
            if subtype =='course':
                properties_template = course_visiting_group_properties_template
                
            visiting_group = DataContainer(name='',  id=None, _id=None,   info='',  visiting_group_properties=properties_template,  subtype=subtype,  contact_person='',  contact_person_email='',  contact_person_phone='',  boknr='')
        
        else:
            visiting_group_c = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
            if not visiting_group_c.has_key('subtype'):
                visiting_group_c['subtype'] = 'program'
            visiting_group = makeVisitingGroupObjectOfVGDictionary(visiting_group_c)
            
        return dict(visiting_group=visiting_group,  bokn_status_map=bokn_status_options,  is_new=is_new)


    @expose()
    @validate(create_edit_visiting_group_form, error_handler=edit_visiting_group)
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def save_visiting_group_properties(self,  _id=None,  name='', info='',  from_date=None,  to_date=None,  contact_person='', contact_person_email='',  contact_person_phone='',  visiting_group_properties=None, camping_location='', boknr='', password='',  subtype=''):
        id = _id
        is_new = ((None == id) or (id == ''))
        
        #...this is a hack so we can direct the id of the visiting group for special groups
        
        if not is_new:
            if 'visiting_group' not in id:
                is_new = True
                id_c = 'visiting_group.'+id
        else:
            id_c = genUID(type='visiting_group')
            
        if is_new:
            # TODO: make sure subtype is in one of
            if not subtype in ['program','course','staff']:
                tg.flash('error with subtype')
                raise redirect(request.referrer)
                
            visiting_group_c = dict(type='visiting_group',  subtype=subtype,  tags=[],  boknstatus=0,  vodbstatus=0)
            #...populate sheets and computed sheets?
            
        else:
            id_c = id
            visiting_group_c = holly_couch[id_c]
            
        #visiting_group_c['type'] = 'visiting_group'
        visiting_group_c['name'] = name
        visiting_group_c['info'] = info
        
        # TODO: sanitize dates. REFACTOR
        try:
            tmp_date = datetime.datetime.strptime(str(from_date),'%Y-%m-%d')
        except ValueError:
            tg.flash('error with from-date')
            raise redirect(request.referrer)
            
        visiting_group_c['from_date'] = str(from_date)
        
        try:
            tmp_date = datetime.datetime.strptime(str(to_date),'%Y-%m-%d')
        except ValueError:
            tg.flash('error with to-date')
            raise redirect(request.referrer)
        visiting_group_c['to_date'] = str(to_date)
        
        
        visiting_group_c['contact_person'] = contact_person
        visiting_group_c['contact_person_email'] = contact_person_email
        visiting_group_c['contact_person_phone'] = contact_person_phone
        
        # TODO: boknr maybe shouldnt be changeble if program or vodb state has passed by preliminary (10) ?
        
        visiting_group_c['boknr'] = boknr
        
        # TODO: password for group should be set in special page
        visiting_group_c['password'] = password
        
        visiting_group_c['camping_location'] = camping_location
        
        #...now we have to update all cached content, so we need all bookings that belong to this visiting group
        visiting_group_c['visiting_group_properties'] = populatePropertiesAndRemoveUnusedProperties(visiting_group_c,  visiting_group_properties)

        
        updateBookingsCacheContentAfterPropertyChange(holly_couch, visiting_group_c,  getLoggedInUserId(request))
        vodb_tag_times_tags = computeAllUsedVisitingGroupsTagsForTagSheet(visiting_group_c['tags'], visiting_group_c.get('vodb_tag_sheet',dict(items=[]))['items'])
        updateVisitingGroupComputedSheets(visiting_group_c, visiting_group_c['visiting_group_properties'], sheet_map=dict(vodb_eat_sheet=vodb_eat_times_options, vodb_live_sheet=vodb_live_times_options, vodb_tag_sheet=vodb_tag_times_tags))
        
        
        holly_couch[id_c] = visiting_group_c
        
        if visiting_group_c.has_key('_id'):
            raise redirect('/visiting_group/show_visiting_group?visiting_group_id='+visiting_group_c['_id'])
        raise redirect('/visiting_group/view_all')


    @validate(validators={'id':validators.Int})
    @require(Any(is_user('root'), has_level('pl'), msg='Only pl members may change visiting group properties'))
    def delete_visiting_group(self,  id=None):
        if None == id:
            pass
            
        raise redirect('/visiting_group/view_all')


    def fn_cmp_booking_date_list(self, a, b):
        if a[0].booking_day == None:
            if b[0].booking_day == None:
                return 0
            else:
                return -1

        elif b[0].booking_day == None:
            return 1

        return cmp(a[0].booking_day['date'], b[0].booking_day['date'])


    def fn_cmp_booking_timestamps(self, a, b):
        if a.booking_day == None:
            if b.booking_day == None:
                return 0
            else:
                return -1

        elif b.booking_day == None:
            return 1
      
        elif a.booking_day['date'] > b.booking_day['date']:
            return 1
        elif a.booking_day['date'] < b.booking_day['date']:
            return -1
        else:
            return cmp(a.slot['time_from'], b.slot['time_from'])
        
    def getSlotMapOfBookingDay(self,  booking_day_slot_map,  tmp_booking_day,  subtype='program'):
        
        # in the future, select between bookings subtype
        
        tmp_schema_id = tmp_booking_day['day_schema_id']
        
        if not booking_day_slot_map.has_key(tmp_schema_id):
            tmp_slot_map = getSchemaSlotActivityMap(holly_couch, tmp_booking_day, subtype=subtype)
            booking_day_slot_map[tmp_schema_id] = tmp_slot_map
        return booking_day_slot_map[tmp_schema_id]
        
        
    @expose('hollyrosa.templates.view_bookings_of_name')
    @validate(validators={"name":validators.UnicodeString(), "render_time":validators.UnicodeString(), "hide_comment":validators.Int(), "show_group":validators.Int()})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_bookings_of_name(self,  name=None, render_time='', hide_comment=0, show_group=0):
        # TODO: its now possible to get bookings on both name and id
        bookings = [b.doc for b in getBookingsOfVisitingGroup(holly_couch, name, '<- MATCHES NO GROUP ->')]
        
#        if len(bookings) > 0:
#            slot_map = getSchemaSlotActivityMap(holly_couch, bookings[0],  subtype='program') # TODO: load for each different schema used
#        else:
#            slot_map = []
        
        visiting_group_id = None
        visiting_group = [v.doc for v in getVisitingGroupOfVisitingGroupName(holly_couch, name)]
        if len(visiting_group) == 1:
            visiting_group_id = visiting_group[0]['_id']
            
            first_visiting_group = visiting_group[0]
            
        #...now group all bookings in a dict mapping activity_id:content
        clustered_bookings = {}
        booking_day_map = dict()
        booking_day_slot_map = dict()
        for bd in getBookingDays(holly_couch):
            booking_day_map[bd.doc['_id']] = bd.doc
            
            #...this is very time consuming, better list all slot map and build a map
            #booking_day_slot_map[bd.doc['_id']] = getSchemaSlotActivityMap(holly_couch, bd.doc, subtype='program') 
        
        activities = dict()
        used_activities_keys = dict()
        for x in getAllActivities(holly_couch):
            activities[x.key[1]] = x.doc
        
        
        for b in bookings: # TODO: There will be quite a few multiples if we search on both id and name!
            if hide_comment==1:
                tmp = b['cache_content'] 
                i = tmp.find('//')
                if i > 0:
                    b['cache_content'] = b['cache_content'][:i]
                         
            key = str(b['activity_id'])+':'+b['content']
            if None == b.get('booking_day_id',  None):
                key = 'N'+key

            #...we need to do this transfer because we need to add booking_day.date and slot time.
            #...HERE WE MUST NOW ONCE AGAIN GET SLOT FROM BOOKING DAY ID AND SLOT ID...
            booking_day_id = None
            slot_id = ''
            slot_o = None
            tmp_booking_day = None
            
            used_activities_keys[b['activity_id']] = 1
            used_activities_keys[activities[b['activity_id']]['activity_group_id']] = 1
                
            if b.has_key('booking_day_id'):
                booking_day_id = b['booking_day_id']
                if '' != booking_day_id:
                    tmp_booking_day = booking_day_map[booking_day_id]
                    slot_id = b['slot_id']
                    tmp_slot_map = self.getSlotMapOfBookingDay(booking_day_slot_map,  tmp_booking_day)
                    slot_o = tmp_slot_map[slot_id]
            
            b2 = DataContainer(booking_state=b['booking_state'],  cache_content=b['cache_content'],  content=b['content'] ,  activity=activities[b['activity_id']],  id=b['_id'],  booking_day=tmp_booking_day ,  slot_id=slot_id ,  slot=slot_o,  booking_day_id=booking_day_id,  valid_from=b.get('valid_from',''),  valid_to=b.get('valid_to',''),  requested_date=b.get('requested_date',''))
            if clustered_bookings.has_key(key):
                bl = clustered_bookings[key]
                bl.append(b2)
            else:
                bl = list()
                bl.append(b2)
                clustered_bookings[key] = bl 

        clustered_bookings_list = clustered_bookings.values()
        clustered_bookings_list.sort(self.fn_cmp_booking_date_list)
        for bl in clustered_bookings_list:
            bl.sort(self.fn_cmp_booking_timestamps)
        
        if True: #show_group==1:    
            booking_info_notes = [n.doc for n in getBookingInfoNotesOfUsedActivities(holly_couch, used_activities_keys.keys())]            
        else:
            booking_info_notes = []
        return dict(clustered_bookings=clustered_bookings_list,  name=name,  workflow_map=workflow_map, visiting_group_id=visiting_group_id,  getRenderContent=getRenderContent,  formatDate=reFormatDate, booking_info_notes=booking_info_notes, render_time=render_time, visiting_group=first_visiting_group, bokn_status_map=bokn_status_map, notes = [n.doc for n in getNotesForTarget(holly_couch, visiting_group_id)], show_group=show_group)


    @expose(content_type=CUSTOM_CONTENT_TYPE)
    @validate(validators={"visiting_group_id":validators.UnicodeString(), "doc_id":validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('pl'), has_level('staff'), msg='Only staff members may view visiting group attachments'))   
    def download_attachment(self, visiting_group_id, doc_id):
        response.content_type='x-application/download'
        response.headerlist.append(('Content-Disposition','attachment;filename=%s' % doc_id))        
                
        return holly_couch.get_attachment(visiting_group_id, doc_id).read()
    
    
#    @expose()
#    @require(Any(is_user('root'), has_level('pl'), has_level('staff'), msg='Only staff members may upload visiting group attachments'))   
#    def upload_attachment(self, vgrpid, file=''):
#        doc = holly_couch[vgrpid]
#        
#        file = request.POST['file']
#
#        holly_couch.put_attachment(doc, file.file, filename=file.filename)
#        raise redirect(request.referrer)
    
    
    @expose('hollyrosa.templates.edit_visiting_group_vodb_data')
    @validate(validators={"id":validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def edit_vodb_data(self, id):
        vgroup = common_couch.getVisitingGroup(holly_couch,  id)
        return dict(visiting_group=vgroup)
    
    
    def do_set_program_state(self, holly_couch, visiting_group_id,  visiting_group_o,  state):
        visiting_group_o['boknstatus'] = state
        holly_couch[visiting_group_id] = visiting_group_o
        
        #..TODO: remember state change
                
        # TODO: only PL can set state=20 (approved) or -10 (disapproved)
        
        ##if state=='20' or state=='-10' or booking_o['booking_state'] == 20 or booking_o['booking_state']==-10:
            #ok = False
            #for group in getLoggedInUserId(request):
            #    if group.group_name == 'pl':
            #        ok = True
            ##ok = has_level('pl').check_authorization(request.environ)
            
            # TODO: fix
            
#            if not ok:
#                flash('Only PL can do that. %s' % request.referrer, 'warning')
#                raise redirect(request.referrer)
        ##activity = holly_couch[booking_o['activity_id']]
        ##booking_day = holly_couch[booking_o['booking_day_id']]
        
        ##booking_o['booking_state'] = state
        ##booking_o['last_changed_by_id'] = getLoggedInUserId(request)
        
        ##holly_couch[booking_id] = booking_o
        ##remember_workflow_state_change(holly_couch, booking=booking_o, state=state,  booking_day_date=booking_day['date'],  activity_title=activity['title'])

    def do_set_vodb_state(self, holly_couch, visiting_group_id, visiting_group_o, state):
        visiting_group_o['vodbstatus'] = state
        holly_couch[visiting_group_id] = visiting_group_o


    @expose()
    @validate(validators={'visiting_group_id':validators.UnicodeString(not_empty=True), 'state':validators.Int(not_empty=True)})    
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def set_program_state(self, visiting_group_id=None,  state=0):
        visiting_group_o = common_couch.getVisitingGroup(holly_couch,  visiting_group_id) 
        self.do_set_program_state(holly_couch, visiting_group_id,  visiting_group_o, int(state))            
        raise redirect(request.referrer)


    @expose()
    @validate(validators={'visiting_group_id':validators.UnicodeString(not_empty=True), 'state':validators.Int(not_empty=True)})    
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def set_vodb_state(self, visiting_group_id=None,  state=0):
        visiting_group_o = common_couch.getVisitingGroup(holly_couch,  visiting_group_id) 
        self.do_set_vodb_state(holly_couch, visiting_group_id,  visiting_group_o, int(state))            
        raise redirect(request.referrer)


    @expose('hollyrosa.templates.program_booking_layers')
    @validate(validators={"visiting_group_id":validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def layers(self, visiting_group_id):
        vgroup = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
        return dict(visiting_group=vgroup,  notes=[],  tags=[],  reFormatDate=reFormatDate)


    @expose("json")
    @validate(validators={"visiting_group_id":validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def program_layer_get_days(self, visiting_group_id ):
        print '****************** program layer get days', visiting_group_id
        
        # I need to construct the mapping (given a pre selected schema for now...) 
        #
        # booking_day_id:slot_id:layer_id -> datetime_layer_id
        #
        # This map is constructed from a day schema. Each activity has slots, these slots have time associated with them. 
        #
        # We also need a list of booking days for the given group, we could use the first boking day and guess the schema. That would be a short cut but a necessary one.
        #
        
        visiting_group = holly_couch[visiting_group_id]
        
        date_range = dateRange(visiting_group['from_date'], visiting_group['to_date'])
        
        booking_days = [bd.doc for bd in getBookingDays(holly_couch,  visiting_group['from_date'], visiting_group['to_date'])]
        
        # TODO dangerous below, we can have diffreent schemas for different days
        first_booking_day=booking_days[0]
        
        schema_id = first_booking_day['day_schema_id']
        
        schema_doc = holly_couch[schema_id]
        schema = schema_doc['schema']
        
        # if we assume the same layout for every slot row, we can get first row in schema and use it as template
        any_slot_row_in_schema = schema[schema.keys()[0]][1:] # skip first part, now we have four time-slots that can be used
        
        #...create temporary mapping title-> id, in the future, this should be based on time rather on the title (which can be dangerous)
        time_id_mapping = dict(FM='fm',  EM='em')
        time_id_mapping[u'Kväll'] = 'eve'
        time_id_mapping['After hours'] = 'afh'
        
        #...it would be best if we now could clean out the slot_id from the mapping
        generalized_slot_row = []
        layer_times = []
        for tmp_slot_row in any_slot_row_in_schema:
            tmp_item = {}
            for k, v in tmp_slot_row.items():
                if k != 'slot_id':
                    tmp_item[k] = v
                if k == 'title':
                    layer_times.append(dict(title=v,  symbol=time_id_mapping[v]))
            generalized_slot_row.append(tmp_item)
        
        datetime_map = []
       
        #...iterate through schema and find FM EM etc
        
        # iterate through schema and find the slot_id maping. 
        
        layer_days = []
        for d in booking_days:
            tmp_item = dict(booking_day_id=d['_id'],  date=d['date'])
            layer_days.append(tmp_item)
        
        #...
        program_layers = visiting_group.get('layers',  [])
        
        #...I need to build this mapping from booking_day_id:slot_id:layer_id to datetime bucket
        #   so iterate through all schema rows and look at time, 
        #
        # One thing I need to consider serriousely is how th handle layers. Is it a property of bookings within a bucket (essentially the visiting group id of the booking itself),
        #   if so, I dont need to complicate the layer thing too much,
        slot_id_time_map = {}
        for tmp_activity_id,  tmp_activity_row in schema.items():
            for tmp_slot in tmp_activity_row[1:]:
                tmp_time = tmp_slot['title']
                slot_id_time_map[tmp_slot['slot_id']] = time_id_mapping[tmp_time]
                
        # TODO return activity title map
        activity_title_map = getActivityTitleMap(holly_couch)
        
        
        
        return dict(layer_time=layer_times,  layer_days=layer_days,  slot_id_time_map=slot_id_time_map,  visiting_group_id=visiting_group_id,  activity_title_map=activity_title_map,  program_layers=program_layers)
        
    @expose("json")
    #@validate(validators={"visiting_group_id":validators.UnicodeString(),  "layer_title":validators.UnicodeString(),  "layer_colour":validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def program_layer_get_bookings(self, visiting_group_id,  layer_title='',  layer_colour='#fff' ):
        print '******* program_layer_get_bookings',  layer_title,  layer_colour
        visiting_group=holly_couch[visiting_group_id]
        bookings = []
        for tmp in getBookingsOfVisitingGroup(holly_couch, visiting_group['name'], '<- MATCHES NO GROUP ->'):
            tmp_doc = tmp.doc
            tmp_doc['layer_title']=layer_title
            tmp_doc['layer_colour'] = layer_colour
            bookings.append(tmp_doc)
        
        bucket_texts = []
        for tmp in getAllProgramLayerBucketTexts(holly_couch,  visiting_group_id):
            tmp_doc = tmp.doc
            tmp_doc['layer_title']=visiting_group['name']
            tmp_doc['layer_colour'] = layer_colour
            bucket_texts.append(tmp_doc)
        
        return dict(bookings=bookings,  bucket_texts=bucket_texts)
        
        
    
    @expose("json")
    def program_layer_edit_text(self,  visiting_group_id, layer_text_id=''):
        is_new = (layer_text_id=='')
        
        if is_new:
            text_doc = DataContainer(text='',  title='', program_layer_text_id='',  state=0)
        else:
            text_doc = holly_couch[layer_text_id]
            
        return dict(layer_text=text_doc)
        
        
    @expose("json")
    def program_layer_save_bucket_text(self,  visiting_group_id='', booking_day_id='',  bucket_time='', program_layer_text_id='',  text='',  title=''):
        #is_new = (program_layer_text_id=='')
        
        text_doc = None
        bucket_texts = getProgramLayerBucketTextByDayAndTime(holly_couch,  visiting_group_id,  booking_day_id,  bucket_time)
        for b in bucket_texts:
            text_doc = b.doc
            break
        
        is_new = (None == text_doc)
        
        
        if is_new:
            id = genUID(type='program_layer_text')
            
            #...if slot_id is none, we need to figure out slot_id of bucket_time OR we simply save bucket_time
            
            text_doc = dict(type='program_layer_text',  subtype='bucket_text',  status=0,  booking_day_id=booking_day_id, bucket_time=bucket_time )
            #...populate sheets and computed sheets?
            
            text_doc['text'] = text
            text_doc['title'] = title
            text_doc['visiting_group_id'] = visiting_group_id
            holly_couch[id] = text_doc
        else:
            #text_doc = holly_couch[layer_text_id]
            
            
            text_doc['text'] = text
            text_doc['title'] = title
            holly_couch[text_doc['_id']] = text_doc
            # TODO call it bucket text or layer text ?
            
        visiting_group=holly_couch[visiting_group_id]
        text_doc['layer_title']=visiting_group['name']
        text_doc['layer_colour'] = "#fff"
        return dict(bucket_text=text_doc) 


    @expose("json")
    def program_layer_get_bucket_text(self,  visiting_group_id='',  booking_day_id='',  bucket_time=''):
        #load matching doc from hllyrosa  visiting_group,id, booking_day_id, bucket_time
        
        bucket_texts = getProgramLayerBucketTextByDayAndTime(holly_couch,  visiting_group_id,  booking_day_id,  bucket_time)
        
        doc = dict(type='program_layer_text',  subtype='bucket_text',  status=0, booking_day_id=booking_day_id, bucket_time=bucket_time,  text='',  title='' ,  visiting_group_id=visiting_group_id)
        for b in bucket_texts:
            doc = b.doc
            break
        
        bucket_text = doc
        #...repeat
        visiting_group=holly_couch[visiting_group_id]
        bucket_text['layer_title']=visiting_group['name']
        bucket_text['layer_colour'] = "#fff"
        return dict(bucket_text=bucket_text)
