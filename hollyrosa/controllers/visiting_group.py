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

from tg import expose, flash, require, url, request, redirect,  validate
from formencode import validators
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, holly_couch
from hollyrosa.model.booking_couch import getAllActivities,  getAllVisitingGroups,  getVisitingGroupsAtDate,  getVisitingGroupsInDatePeriod,  getBookingsOfVisitingGroup,  getSchemaSlotActivityMap,  getVisitingGroupsByBoknstatus, getNotesForTarget, getBookingInfoNotesOfUsedActivities
from hollyrosa.model.booking_couch import getBookingDays,  getAllVisitingGroupsNameAmongBookings, getAllTags, getDocumentsByTag, getVisitingGroupOfVisitingGroupName, getTargetNumberOfNotesMap
import datetime

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context


from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking
from hollyrosa.controllers.common import workflow_map,  bokn_status_map,  bokn_status_options,  DataContainer,  getRenderContent, computeCacheContent,  has_level,  reFormatDate, getLoggedInUserId
from hollyrosa.controllers.booking_history import remember_tag_change


__all__ = ['VisitingGroup']


class VisitingGroupPropertyRow(object):
    def __init__(self,  id,  property_row):
        self.id= id
        self.property = property_row['property']
        self.unit =property_row['unit']
        self.value = property_row['value']
        self.description = property_row['description']
        self.from_date = property_row['from_date']
        self.to_date = property_row['to_date']
        #self._sa_instance_state = 0
    
    
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
    @validate(validators={'fromdate':validators.DateValidator(not_empty=False), 'todate':validators.DateValidator(not_empty=False)})
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_date_range(self,  fromdate=None,  todate=None):
        visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(holly_couch, fromdate,  todate)]
        v_group_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups,  from_date=fromdate,  to_date=todate)
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)

    
    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('erspl'), has_level('staff'),   msg='Only staff members and viewers may view visiting group properties'))
    def view_tags(self, tag):
        # TODO>: rename and maybe only return visiting groups docs ?
        visiting_groups = [v.doc for v in getDocumentsByTag(holly_couch, tag)] 
        remaining_visiting_groups_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups)
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=remaining_visiting_groups_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)

    
    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('erspl'), has_level('staff'),   msg='Only staff members and viewers may view visiting group properties'))
    def view_all(self):
        visiting_groups = [v.doc for v in getAllVisitingGroups(holly_couch)] 
        remaining_visiting_groups_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups)        
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=remaining_visiting_groups_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'boknstatus':validators.Int(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_boknstatus(self,  boknstatus=None):
        #boknstatus=boknstatus[:4] # amateurish quick sanitation
        #visiting_groups = get_visiting_groups_with_boknstatus(boknstatus) 
        visiting_groups =[v.doc for v in getVisitingGroupsByBoknstatus(holly_couch, boknstatus)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)  
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)

        
    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'period':validators.String(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_period(self,  period=None):

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
        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)])


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'at_date':validators.DateValidator(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_at_date(self,  at_date=None):
        visiting_groups = [v.doc for v in getVisitingGroupsAtDate(holly_couch, at_date)] 
        v_group_map = dict() #self.makeRemainingVisitingGroupsMap(visiting_groups,  from_date=at_date,  to_date=at_date)
        has_notes_map = getTargetNumberOfNotesMap(holly_couch) 
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys(), bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=[t.key for t in getAllTags(holly_couch)], has_notes_map=has_notes_map)


    @expose("json")
    @validate(validators={'id':validators.UnicodeString})
    def show_visiting_group_data(self,  id=None,  **kw):
        
        properties=[]
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='')
            
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
            
        else:
            
            visiting_group = holly_couch[id] 
            
            # TODO: refactor make DataContainer from visiting group
            
            properties=[p for p in visiting_group['visiting_group_properties'].values()]
            
        return dict(visiting_group=visiting_group, properties=properties)
        
        
    @expose('hollyrosa.templates.show_visiting_group')
    @validate(validators={'id':validators.Int})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def show_visiting_group(self,  id=None,  **kw):
        
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='')
            bookings=[]
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
            bookings=[]
        else:
            visiting_group = holly_couch[str(id)]

            # TODO: see below
            bookings = [] 
            notes = [n.doc for n in getNotesForTarget(holly_couch, id)]
        return dict(visiting_group=visiting_group, bookings=bookings, workflow_map=workflow_map,  getRenderContent=getRenderContent, bokn_status_map=bokn_status_map,  reFormatDate=reFormatDate, notes=notes)


    @expose('hollyrosa.templates.edit_visiting_group')
    @validate(validators={'id':validators.Int})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def edit_visiting_group(self,  id=None,  **kw):
        tmpl_context.form = create_edit_visiting_group_form
        
        new_empty_visiting_group_property = [DataContainer(property='spar',  value='0',  unit=u'spår',  description=u'antal deltagare 8 till 9 år'), 
                                             DataContainer(property='uppt',  value='0',  unit=u'uppt',  description=u'antal deltagare 10 till 11 år'), 
                                             DataContainer(property='aven',  value='0',  unit=u'aven',  description=u'antal deltagare 12 till 15 år'), 
                                             DataContainer(property='utm',  value='0',  unit=u'utm',  description=u'antal deltagare 16 till 18 år')]
 
 
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='',  visiting_group_properties=new_empty_visiting_group_property)
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
        else:
            visiting_group_c = holly_couch[id] 
#            visiting_group_c['from_date'] = datetime.datetime.strptime(visiting_group_c['from_date'],'%Y-%m-%d')
#            visiting_group_c['to_date'] = datetime.datetime.strptime(visiting_group_c['to_date'],'%Y-%m-%d')
            
            #...HERE MAKE OBJECT OF DICTIONARY OR IT WONT WORK WITH THE FORMS
            vgps = []
            for id,  vgp in visiting_group_c['visiting_group_properties'].items():
                try:
                    print 'vgp',vgp['to_date']
                    tmp_to_date = datetime.datetime.strptime(vgp['to_date'],'%Y-%m-%d')
                except ValueError:
                    tmp_to_date = None
                
                try:
                    tmp_from_date = datetime.datetime.strptime(vgp['from_date'],'%Y-%m-%d')
                except ValueError:
                    tmp_from_date = None
                
                
                vgpx = DataContainer(property=vgp['property'],  value=vgp['value'],  unit=vgp['unit'], description=vgp['description'],  from_date=tmp_from_date,  to_date=tmp_to_date,  id=str(id))
                vgps.append(vgpx)

            # TODO: DataContainerFromDictLikeObject(fields=)
            visiting_group = DataContainer(name=visiting_group_c['name'],  id=visiting_group_c['_id'],  info=visiting_group_c['info'],  visiting_group_properties=vgps
                                           ,  contact_person=visiting_group_c['contact_person'],  contact_person_email=visiting_group_c['contact_person_email'],  contact_person_phone=visiting_group_c['contact_person_phone'], 
                                           boknr=visiting_group_c['boknr'],  boknstatus=visiting_group_c['boknstatus'],  camping_location=visiting_group_c['camping_location'],  from_date=datetime.datetime.strptime(visiting_group_c['from_date'],'%Y-%m-%d'), to_date=datetime.datetime.strptime(visiting_group_c['to_date'], '%Y-%m-%d'))
            
        return dict(visiting_group=visiting_group,  bokn_status_map=bokn_status_options)
        
        

    @expose()
    @validate(create_edit_visiting_group_form, error_handler=edit_visiting_group)
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def save_visiting_group_properties(self,  id=None,  name='', info='',  from_date=None,  to_date=None,  contact_person='', contact_person_email='',  contact_person_phone='',  visiting_group_properties=None, camping_location='', boknr='', boknstatus=0):
        # TODO: does not work?
        if None == id or id == '':
            is_new = True
            visiting_group_c = dict(type='visiting_group')
            id_c = genUID(type='visiting_group')
        elif 'visiting_group' not in id:
            is_new = True
            visiting_group_c = dict(type='visiting_group')
            id_c = 'visiting_group.'+id
            
        else:
            id_c = id
            visiting_group_c = holly_couch[id_c]
            is_new= False
            
        visiting_group_c['type'] = 'visiting_group'
        visiting_group_c['name'] = name
        visiting_group_c['info'] = info
        visiting_group_c['from_date'] = str(from_date)
        visiting_group_c['to_date'] = str(to_date)
        visiting_group_c['contact_person'] = contact_person
        visiting_group_c['contact_person_email'] = contact_person_email
        visiting_group_c['contact_person_phone'] = contact_person_phone
        visiting_group_c['boknr'] = boknr
        visiting_group_c['boknstatus'] = boknstatus
        visiting_group_c['camping_location'] = camping_location
        
        visiting_group_property_c = dict()
       
            
        #...remove non-used params !!!! Make a dict and see which are used, remove the rest
        unused_params = {}
#        for k in visiting_group.visiting_group_property:
#            unused_params[str(k.id)] = k
        
        used_param_ids = []
        if  visiting_group_c.has_key('visiting_group_properties'):
            used_param_ids = visiting_group_c['visiting_group_properties'].keys()
        
        for param in visiting_group_properties:
            is_new_param = False
            if param['property'] != '' and param['property'] != None:
                if param['id'] != '' and param['id'] != None:
                    visiting_group_property_c[param['id']] = dict(property=param['property'],  value=param.get('value',''),  description=param.get('description',''),  unit=param.get('unit',''),  from_date=str(param['from_date']),  to_date=str(param['to_date']))
                #what if the param has no id?
                else:
                    #...compute new unsued id
                    # TODO: these ids are not perfectly unique. It shouldnt matter since its the param name that is really used
                    
                    new_id_int = 1
                    while str(new_id_int) in used_param_ids:
                        new_id_int += 1
                    used_param_ids.append(str(new_id_int))
                    
                    visiting_group_property_c[str(new_id_int)] = dict(property=param['property'],  value=param.get('value',''),  description=param.get('description',''),  unit=param.get('unit',''),  from_date=str(param['from_date']),  to_date=str(param['to_date']))
                    
        # no need to delete old params, but we need to add to history how params are changed and what it affects
        
        #...now we have to update all cached content, so we need all bookings that belong to this visiting group
        
        visiting_group_c['visiting_group_properties'] = visiting_group_property_c
        
        # TODO: IMPORTANT TO FIX LATER
        bookings = getBookingsOfVisitingGroup(holly_couch, id_c,  None)
        for tmp in bookings:
            tmp_booking = tmp.doc
            #print 'tmp_booking',  tmp_booking
            new_content = computeCacheContent(visiting_group_c, tmp_booking['content'])
            if new_content != tmp_booking['cache_content'] :
            
                tmp_booking['cache_content'] = new_content
                tmp_booking['last_changed_by'] = getLoggedInUserId(request)
                
                # TODO: change booking status (from whatever, since the text has changed)
                
                
                # TODO: remember booking history change
                
                
                holly_couch[tmp_booking['_id']] = tmp_booking
            
        
        holly_couch[id_c] = visiting_group_c
        
        if visiting_group_c.has_key('_id'):
            raise redirect('/visiting_group/show_visiting_group?id='+visiting_group_c['_id'])
        raise redirect('/visiting_group/view_all')


    
    @expose()
    @validate(validators={'id':validators.Int})
    @require(Any(is_user('root'), has_level('pl'), msg='Only pl members may change visiting group properties'))
    def delete_visiting_group(self,  id=None):
        if None == id:
            pass
            #visiting_group = booking.VisitingGroup()
            
#        else:
#            visiting_group = DBSession.query(booking.VisitingGroup).filter('id='+ str(id)).one()
#            
#            
#        #...WARNING: bookings will remain. Perhaps a non-destructive delete instead?
#        DBSession.delete(visiting_group)
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
        

    @expose('hollyrosa.templates.view_bookings_of_name')
    @validate(validators={"name":validators.UnicodeString(), "render_time":validators.UnicodeString})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_bookings_of_name(self,  name=None, render_time=''):
        # TODO: its now possible to get bookings on both name and id
        bookings = [b.doc for b in getBookingsOfVisitingGroup(holly_couch, name, '<- MATCHES NO GROUP ->')]
        print 'view_bookings_of_name', bookings
        slot_map = getSchemaSlotActivityMap(holly_couch, 'day_schema.1') # TODO: load for each different schema used
        
        # TODO: make view. Its just so simple
        visiting_group_id = None
        visiting_group = [v.doc for v in getVisitingGroupOfVisitingGroupName(holly_couch, name)]
        if len(visiting_group) == 1:
            visiting_group_id = visiting_group[0]['_id']
            

        #...now group all bookings in a dict mapping activity_id:content
        clustered_bookings = {}
        booking_day_map = dict()
        for bd in getBookingDays(holly_couch):
            booking_day_map[bd.doc['_id']] = bd.doc
        
        activities = dict()
        used_activities_keys = dict()
        for x in getAllActivities(holly_couch):
            activities[x.key[1]] = x.doc
        
        
        for b in bookings: # TODO: There will be quite a few multiples if we search on both id and name!
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
                    #tmp_schema = holly_couch[tmp_booking_day.day_schema_id]
                    slot_id = b['slot_id']
                    slot_o = slot_map[slot_id]
            
            b2 = DataContainer(booking_state=b['booking_state'],  cache_content=b['cache_content'],  content=b['content'] ,  activity=activities[b['activity_id']],  id=b['_id'],  booking_day=tmp_booking_day ,  slot_id=slot_id ,  slot=slot_o,  booking_day_id=booking_day_id,  valid_from=b['valid_from'],  valid_to=b['valid_to'],  requested_date=b['requested_date'])
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
            
        booking_info_notes = [n.doc for n in getBookingInfoNotesOfUsedActivities(holly_couch, used_activities_keys.keys())]            
        return dict(clustered_bookings=clustered_bookings_list,  name=name,  workflow_map=workflow_map, visiting_group_id=visiting_group_id,  getRenderContent=getRenderContent,  formatDate=reFormatDate, booking_info_notes=booking_info_notes, render_time=render_time)


