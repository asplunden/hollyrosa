# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011 Martin Eliasson

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
from repoze.what.predicates import Any, is_user, has_permission
from formencode import validators

from hollyrosa.lib.base import BaseController
from hollyrosa.model import metadata,  booking,  holly_couch,  genUID,  get_visiting_groups,  get_visiting_groups_at_date,  get_visiting_groups_in_date_period,  get_visiting_groups_with_boknstatus,  get_visiting_group_names,  getBookingDays, getAllActivities
from sqlalchemy import and_
import datetime

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context



from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking
from hollyrosa.controllers.common import workflow_map,  DataContainer,  getRenderContent, computeCacheContent


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
    #@require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view(self, url):
        visiting_groups = get_visiting_groups() #DBSession.query(booking.VisitingGroup).order_by('fromdate').all()
        visiting_group_names = [x['name'] for x in visiting_groups] #DBSession.query(booking.VisitingGroup.name).all()
        v_group_map = self.makeVGroupMap(visiting_group_names)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())
        
        

    def makeVGroupMap(self, visiting_group_names):
        v_group_map = dict()
        
        visiting_group_names = get_visiting_group_names()
        
###        for b in DBSession.query(booking.Booking.visiting_group_name).all():
###            if b not in visiting_group_names:
###                v_group_map[b] = 1

        return v_group_map
        
        
    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'fromdate':validators.DateValidator(not_empty=False), 'todate':validators.DateValidator(not_empty=False)})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_date_range(self,  fromdate=None,  todate=None):
        visiting_groups = get_visiting_groups_in_date_period(fromdate,  todate) #DBSession.query(booking.VisitingGroup).filter(and_('todate <= \''+todate+'\'', 'fromdate >= \''+fromdate+'\'')).order_by('fromdate').all()        
        v_group_map = self.makeVGroupMap(None)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())

        
    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_all(self):
        visiting_groups = get_visiting_groups() #DBSession.query(booking.VisitingGroup).order_by('fromdate').all()
        v_group_map = self.makeVGroupMap(None)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'boknstatus':validators.String(not_empty=False)})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_boknstatus(self,  boknstatus=None):
        boknstatus=boknstatus[:4] # amateurish quick sanitation
        visiting_groups = get_visiting_groups_with_boknstatus(boknstatus) #DBSession.query(booking.VisitingGroup).join(booking.VistingGroupProperty).filter(and_('property=\'boknstatus\'', 'value=\''+boknstatus+'\'')).order_by('visiting_group_fromdate').all()
                
        visiting_group_names = [] #DBSession.query(booking.VisitingGroup.name).all()
        v_group_map = self.makeVGroupMap(visiting_group_names)        
        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())

        
    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'period':validators.String(not_empty=False)})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_period(self,  period=None):

        if period == '1an':
            visiting_groups = get_visiting_groups(from_date='2011-01-01',  to_date='2011-07-16') #DBSession.query(booking.VisitingGroup).filter('fromdate < \'2011-07-17\'').order_by('fromdate').all()
        elif period == '2an':
            visiting_groups = get_visiting_groups(from_date='2011-07-17',  to_date='2011-08-24') #DBSession.query(booking.VisitingGroup).filter('todate > \'2011-07-16\'', ).order_by('fromdate').all()

        else:
            visiting_groups = get_visiting_groups()# DBSession.query(booking.VisitingGroup).order_by('fromdate').all()
        
        visiting_group_names = visiting_group_names = [x['name'] for x in visiting_groups]  #DBSession.query(booking.VisitingGroup.name).all()
        v_group_map = self.makeVGroupMap(visiting_group_names)        
        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())


    @expose('hollyrosa.templates.visiting_group_view_all')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_today(self):
        at_date = datetime.datetime.today().strftime('%Y-%m-%d')
        visiting_groups = get_visiting_groups_at_date(at_date) #DBSession.query(booking.VisitingGroup).filter(and_('todate >= \''+at_date+'\'', 'fromdate <= \''+at_date+'\'')).order_by('fromdate').all()
        visiting_group_names = [x['name'] for x in visiting_groups]  #isiting_group_names = DBSession.query(booking.VisitingGroup.name).all()
        v_group_map = self.makeVGroupMap(visiting_group_names)        
        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())


    @expose('hollyrosa.templates.visiting_group_view_all')
    @validate(validators={'at_date':validators.DateValidator(not_empty=False)})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_at_date(self,  at_date=None):
        visiting_groups = get_visiting_groups_at_date(at_date) #DBSession.query(booking.VisitingGroup).filter(and_('todate >= \''+at_date+'\'', 'fromdate <= \''+at_date+'\'')).order_by('fromdate').all()
        visiting_group_names = [x['name'] for x in visiting_groups] #DBSession.query(booking.VisitingGroup.name).all()
        v_group_map = self.makeVGroupMap(visiting_group_names)        
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=v_group_map.keys())


    @expose("json")
    @validate(validators={'id':validators.UnicodeString})
    def show_visiting_group_data(self,  id=None,  **kw):
        
        properties=[]
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='')
            
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
            
        else:
            
            visiting_group = holly_couch[id] #DBSession.query(booking.VisitingGroup).filter('id='+str(id)).one()
            
            #...refactor make DataContainer from visiting group
            
            properties=[p for p in visiting_group['visiting_group_properties'].values()]
            
        return dict(visiting_group=visiting_group, properties=properties)
        
        
    @expose('hollyrosa.templates.show_visiting_group')
    @validate(validators={'id':validators.Int})
    #@require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def show_visiting_group(self,  id=None,  **kw):
        
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='')
            bookings=[]
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
            bookingS=[]
        else:
            visiting_group = holly_couch[str(id)]

            bookings = [] #DBSession.query(booking.Booking).filter('visiting_group_name=\'' + visiting_group.name + '\'').all()
        return dict(visiting_group=visiting_group, bookings=bookings, workflow_map=workflow_map,  getRenderContent=getRenderContent)


    @expose('hollyrosa.templates.edit_visiting_group')
    @validate(validators={'id':validators.Int})
    @require(Any(is_user('root'), has_permission('staff'), msg='Only staff members may change visiting group properties'))
    def edit_visiting_group(self,  id=None,  **kw):
        tmpl_context.form = create_edit_visiting_group_form
        
        new_empty_visiting_group_property = [DataContainer(property='spar',  value='0',  unit=u'spår',  description=u'antal deltagare 8 till 9 år'), 
                                             DataContainer(property='uppt',  value='0',  unit=u'uppt',  description=u'antal deltagare 10 till 11 år'), 
                                             DataContainer(property='aven',  value='0',  unit=u'aven',  description=u'antal deltagare 12 till 15 år'), 
                                             DataContainer(property='utm',  value='0',  unit=u'utm',  description=u'antal deltagare 16 till 18 år'),
                                             DataContainer(property='refnr',  value='',  unit=u'',  description=u'referensnummer'),
                                             DataContainer(property='boknstatus',  value='ny',  unit=u'',  description=u'bokningsstatus')]
 
 
        if None == id:
            visiting_group = DataContainer(name='',  id=None,  info='',  visiting_group_properties=new_empty_visiting_group_property)
        elif id=='':
            visiting_group = DataContainer(name='',  id=None,  info='')
        else:
            visiting_group_c = holly_couch[id] #DBSession.query(booking.VisitingGroup).filter('id='+str(id)).one()
            #cheat = DBSession.query(booking.VisitingGroup).filter('id=10').one()
            
            #...HERE MAKE OBJECT OF DICTIONARY OR IT WONT WORK WITH THE FORMS
            vgps = []
            for id,  vgp in visiting_group_c['visiting_group_properties'].items():
                vgpx = DataContainer(property=vgp['property'],  value=vgp['value'],  unit=vgp['unit'], description=vgp['description'],  from_date=vgp['from_date'],  to_date=vgp['to_date'])
                vgps.append(vgpx)
                
            visiting_group = DataContainer(name=visiting_group_c['name'],  id=visiting_group_c['_id'],  info=visiting_group_c['info'],  visiting_group_properties=vgps
                                           ,  contact_person=visiting_group_c['contact_person'],  contact_person_email=visiting_group_c['contact_person_email'],  contact_person_phone=visiting_group_c['contact_person_phone'], 
                                           boknr=visiting_group_c['boknr'],  boknstatus=visiting_group_c['boknstatus'],  camping_location=visiting_group_c['camping_location'],  from_date=visiting_group_c['from_date'], to_date=visiting_group_c['to_date'])
            
        return dict(visiting_group=visiting_group)
        
        

    @expose()
    @validate(create_edit_visiting_group_form, error_handler=edit_visiting_group)
    @require(Any(is_user('root'), has_permission('staff'), msg='Only staff members may change visiting group properties'))
    def save_visiting_group_properties(self,  id=None,  name='', info='',  from_date=None,  to_date=None,  contact_person='', contact_person_email='',  contact_person_phone='',  visiting_group_properties=None, camping_location='', boknr='', boknstatus=0):

        if len(info)>8192:
            raise IOError, "I appologize for this dirty method of blocking the db from getting a too big text chunk, but I cannot let this propagate to the db."

        if None == id:
            #visiting_group = booking.VisitingGroup()
            is_new = True
            visiting_group_c = dict(type='visiting_group')
            id_c = genUID()
        else:
            #visiting_group = DBSession.query(booking.VisitingGroup).filter('id='+ str(id)).one()
            id_c = str(id)
            visiting_group_c = holly_couch[id_c] #dict(type='visiting_group') # fix by lookup
            
            
            is_new= False
            
#        visiting_group.name = name
#        visiting_group.info = info
#        visiting_group.fromdate = fromdate
#        visiting_group.todate = todate
#        visiting_group.contact_person = contact_person
#        visiting_group.contact_person_email = contact_person_email
#        visiting_group.contact_person_phone = contact_person_phone
#        visiting_group.boknr = boknr
#        visiting_group.boknstatus = boknstatus
#        visiting_group.camping_location = camping_location
#        
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
        
        
        
        
#        if is_new:
#            DBSession.add(visiting_group)
#            
        #...remove non-used params !!!! Make a dict and see which are used, remove the rest
        unused_params = {}
#        for k in visiting_group.visiting_group_property:
#            unused_params[str(k.id)] = k
        
        
        for param in visiting_group_properties:
            is_new_param = False
            if param['property'] != '' and param['property'] != None:
                if param['id'] == '':
                    raise IOError
                    is_new_param = True
                    new_param = booking.VistingGroupProperty()
                
                elif param['id'] == None:
                    is_new_param = True
                    new_param = booking.VistingGroupProperty()
                
                else:
                    new_param = DBSession.query(booking.VistingGroupProperty).filter('id='+ str(param['id'])).one()
                    
                    del unused_params[param['id']]
                    
                visiting_group_property_c[param['id']] = dict(property=param['property'],  value=param.get('value',''),  description=param.get('description',''),  unit=param.get('unit',''),  from_date=str(param['from_date']),  to_date=str(param['to_date']))
                
#                new_param.property = param['property']
#                new_param.value = param.get('value','')
#                new_param.description = param.get('description','')
#                new_param.unit = param.get('unit','')
#                new_param.fromdate = param['fromdate']
#                new_param.todate = param['todate']
#                
#                #...how to add param to visiting group?
#                new_param.visiting_group = visiting_group
#                
#                if is_new_param:
#                    DBSession.add(new_param)
                
#        for unused in unused_params.values():
#            DBSession.delete(unused)
        
        
        #...now we have to update all cached content, so we need all bookings that belong to this visiting group
        
        # IMPORTANT TO FIX LATER
#######        bookings = DBSession.query(booking.Booking).filter('visiting_group_name=\'' + name + '\'').all()
#######        for tmp_booking in bookings:
#######            tmp_booking.cache_content = computeCacheContent(DBSession, tmp_booking.content, tmp_booking.visiting_group.id)
#######        
        #...add visiting group properties
        #...differ between save and new! Visiting group properties should be something like a dict in the dict.
        #holly_couch.save({'type':'visiting_group',  'name':name}) # we need a better way to come up with unique ids!
        
        
        #holly_couch.save(visiting_group_c) # we need a better way to come up with unique ids!
        visiting_group_c['visiting_group_property'] = visiting_group_property_c
        holly_couch[id_c] = visiting_group_c
        
        raise redirect('/visiting_group/view_all')


    
    @expose()
    @validate(validators={'id':validators.Int})
    @require(Any(is_user('root'), has_permission('pl'), msg='Only staff members may change visiting group properties'))
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
        
        
    @expose('hollyrosa.templates.view_bookings_of_name')
    @validate(validators={"name":validators.UnicodeString()})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_bookings_of_name_old(self,  name=None):
        bookings = DBSession.query(booking.Booking).filter(and_('visiting_group_name=\'' + name + '\'', 'booking_state > -100')).all()

        #...the bookings should be ordered by booking day or requested date or nothing. In that order.
        
        

        visiting_group_id = None
        visiting_group = DBSession.query(booking.VisitingGroup).filter('name=\'' + name + '\'').all()
        if len(visiting_group) == 1:
            visiting_group_id = visiting_group[0].id
            
        return dict(bookings=bookings,  name=name,  workflow_map=workflow_map, visiting_group_id=visiting_group_id,  getRenderContent=getRenderContent)
        
    def fn_cmp_booking_date_list(self, a, b):
        if a[0].booking_day == None:
            if b[0].booking_day == None:
                return 0
            else:
                return -1

        elif b[0].booking_day == None:
            return 1

        return cmp(a[0].booking_day.date, b[0].booking_day.date)

    def fn_cmp_booking_timestamps(self, a, b):
        if a.booking_day == None:
            if b.booking_day == None:
                return 0
            else:
                return -1

        elif b.booking_day == None:
            return 1
      
        elif a.booking_day.date > b.booking_day.date:
            return 1
        elif a.booking_day.date < b.booking_day.date:
            return -1
        else:
            return cmp(a.slot['time_from'], b.slot['time_from'])


    def getVisitingGroupOfVisitingGroupName(self,  name):
        map_fun = """function(doc) {
        if (doc.type == 'visiting_group') {
            if (doc.name == '""" + name+  """')  {
                emit(doc._id, doc);
                }
            }
        }"""
        
        vgroups = []
        for x in holly_couch.query(map_fun):
            b = x.value
            vgroups.append(b)
        return vgroups
        

    @expose('hollyrosa.templates.view_bookings_of_name')
    @validate(validators={"name":validators.UnicodeString()})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_bookings_of_name(self,  name=None):
        #bookings = DBSession.query(booking.Booking).filter(and_('visiting_group_name=\'' + name + '\'', 'booking_state > -100')).all()

        #...the bookings should be ordered by booking day or requested date or nothing. In that order.
        # todo: refactor
        map_fun = """function(doc) {
        if (doc.type == 'booking') {
            if (doc.visiting_group_name == '""" + name+  """')  {
                if (doc.booking_state > -100) {
                    emit(doc._id, doc);
                    }
                }
            }
        }"""
        
        bookings = []
        for x in holly_couch.query(map_fun):
            b = x.value
            bookings.append(b)
        

        visiting_group_id = None
        #visiting_group = DBSession.query(booking.VisitingGroup).filter('name=\'' + name + '\'').all()
        visiting_group = self.getVisitingGroupOfVisitingGroupName(name)
        if len(visiting_group) == 1:
            visiting_group_id = visiting_group[0]['_id']
            

        #...now group all bookings in a dict mapping activity_id:content
        clustered_bookings = {}
        booking_days = getBookingDays(return_map=True)
        activities = dict()
        for x in getAllActivities():
            activities[x.key] = x.value
        
        
        for b in bookings:
            key = str(b['activity_id'])+':'+b['content']
            if None == b['booking_day_id']:
                key = 'N'+key

            #...we need to do this transfer because we need to add booking_day.date and slot time.
            #...HERE WE MUST NOW ONCE AGAIN GET SLOT FROM BOOKING DAY ID AND SLOT ID...
            tmp_booking_day = booking_days[b['booking_day_id']]
            tmp_schema = holly_couch[tmp_booking_day.day_schema_id]
            slot_o = None
            for tmp_activity,  tmp_slot_row in tmp_schema['schema'].items():
                for t in tmp_slot_row[1:]:
                    if t['slot_id'] == b['slot_id']:
                        slot_o = t
                        break
            
            
            
            b2 = DataContainer(booking_state=b['booking_state'],  cache_content=b['cache_content'],  content=b['content'] ,  activity=activities[b['activity_id']],  id=b['_id'],  booking_day=tmp_booking_day ,  slot_id=b['slot_id'] ,  slot=slot_o,  booking_day_id=b['booking_day_id'])
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
            
            
        return dict(clustered_bookings=clustered_bookings_list,  name=name,  workflow_map=workflow_map, visiting_group_id=visiting_group_id,  getRenderContent=getRenderContent)
        
