# -*- coding: utf-8 -*-
"""
Copyright 2010-2015 Martin Eliasson

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




Documentation pointers:
http://turbogears.org/2.0/docs/toc.html
http://toscawidgets.org/documentation/tw.forms/tutorials/index.html#constructing-a-form
http://turbogears.org/2.0/docs/main/ToscaWidgets/forms.html

http://toscawidgets.org/documentation/tw.dynforms/tutorial.html
http://pylonsbook.com/en/1.1/working-with-forms-and-validators.html
http://turbogears.org/2.1/docs/modules/thirdparty/formencode_api.html
http://blog.vrplumber.com/index.php?/archives/2381-ToscaWidgets-JQuery-and-TinyMCE-Tutorialish-ly.html
http://turbogears.org/2.0/docs/main/Auth/Authorization.html#module-repoze.what.predicates

"""


from tg import expose, flash, require, url, request, redirect,  validate,  override_template

from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch, genUID
from hollyrosa.model.booking_couch import getBookingDays,  getAllBookingDays,  getSlotAndActivityIdOfBooking,  getBookingDayOfDate, getVisitingGroupsInDatePeriod,  dateRange2,  getBookingDayOfDateList,  getSlotRowSchemaOfActivity,  getActivityGroupNameAndIdList
from hollyrosa.model.booking_couch import getAllHistoryForBookings,  getAllActivities,  getAllActivityGroups,  getVisitingGroupsAtDate,  getUserNameMap,  getSchemaSlotActivityMap,  getAllVisitingGroups,  getActivityTitleMap
import datetime,  logging

log = logging.getLogger()

from formencode import validators



#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context

import tw.tinymce

from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_activity_form import create_edit_activity_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.edit_book_live_slot_form import  create_edit_book_live_slot_form
from hollyrosa.widgets.move_booking_form import  create_move_booking_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking

from hollyrosa.controllers.booking_history import remember_booking_change,  remember_schedule_booking,  remember_unschedule_booking,  remember_book_slot,  remember_booking_properties_change,  remember_new_booking_request,  remember_booking_request_change,  remember_delete_booking_request,  remember_block_slot, remember_unblock_slot,  remember_booking_move,  remember_ignore_booking_warning

from hollyrosa.controllers.common import workflow_map,  DataContainer,  getLoggedInUserId,  change_op_map,  getRenderContent, getRenderContentDict,  computeCacheContent,  has_level,  reFormatDate
from hollyrosa.controllers import common_couch
from hollyrosa.model import holly_couch

__all__ = ['BookingDay',  'Calendar']
    

    
def deleteBooking(holly_couch, booking_o):
    booking_o['booking_state'] = -100
    booking_o['booking_day_id'] = ''
    booking_o['slot_id'] = ''
    holly_couch[booking_o['_id']] = booking_o


def make_booking_day_activity_anchor(tmp_activity_id):
    return '#activity_row_id_' + tmp_activity_id


def getNextBookingDayId(holly_couch, booking_day):
    # TODO: relly needs refactoring
    this_date = booking_day['date'] # make date from string, but HOW?
    next_date = (datetime.datetime.strptime(this_date,'%Y-%m-%d') +  datetime.timedelta(1)).strftime('%Y-%m-%d')
    
    bdays = holly_couch.view('booking_day/all_booking_days', keys=[next_date], include_docs=True)
    bdays2 = [b for b in bdays]     
    return bdays2[0].value
    
    
class Calendar(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
        

    @expose('hollyrosa.templates.calendar_overview')
    def overview_all(self):
        """Show an overview of all booking days"""
        return dict(booking_days=[b.doc for b in getAllBookingDays(holly_couch)])


    @expose('hollyrosa.templates.calendar_overview')
    def overview(self):
        """Show an overview of all booking days"""
        today = datetime.date.today().strftime('%Y-%m-%d')
        return dict(booking_days=[b.doc for b in getBookingDays(holly_couch, from_date=today)])
    

    @expose('hollyrosa.templates.calendar_upcoming')
    def upcoming(self):
        """Show an overview of all booking days"""
        today_date_str = datetime.date.today().strftime('%Y-%m-%d')
        
        end_date_str = (datetime.date.today()+datetime.timedelta(5)).strftime('%Y-%m-%d')

        #today_date_str = '2012-08-01'
        #end_date_str = '2012-08-04'
        
        booking_days = getBookingDays(holly_couch, from_date=today_date_str,  to_date=end_date_str) 


        vgroups = getVisitingGroupsInDatePeriod(holly_couch, today_date_str,  end_date_str) # TODO: fix view later.  get_visiting_groups(from_date=today_date_str,  to_date=end_date_str)

        group_info = dict()
        bdays = list()
        for tmp in booking_days:
            b_day = tmp.doc
            tmp_date_today_str = b_day['date']             
            bdays.append(b_day)
            
            group_info[tmp_date_today_str] = dict(arrives=[v.doc for v in vgroups if v.doc.get('from_date','') == tmp_date_today_str], leaves=[v.doc for v in vgroups if v.doc.get('to_date','') == tmp_date_today_str], stays=[v.doc for v in vgroups if v.doc.get('to_date','') > tmp_date_today_str and v.doc.get('from_date','') < tmp_date_today_str])

        return dict(booking_days=bdays, group_info=group_info)
        
        
    @expose('hollyrosa.templates.booking_day_properties')
    @validate(validators={'id':validators.Int(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booking day properties'))
    def edit_booking_day(self,  id=None,  **kw):
        booking_day = common_couch.getBookingDay(holly_couch, id)
        if not booking_day.has_key('title'):
            booking_day['title'] = ''
        tmpl_context.form = create_edit_booking_day_form
        return dict(booking_day=booking_day,  usage='edit')
        
        
    @validate(create_edit_booking_day_form, error_handler=edit_booking_day)      
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booking day properties'))
    def save_booking_day_properties(self,  _id=None,  note='', title='', num_program_crew_members=0,  num_fladan_crew_members=0):
        
        booking_day_c = common_couch.getBookingDay(holly_couch, _id)
        booking_day_c['note'] = note
        booking_day_c['title'] = title
        booking_day_c['num_program_crew_members'] = num_program_crew_members
        booking_day_c['num_fladan_crew_members'] = num_fladan_crew_members
        holly_couch[_id]=booking_day_c
        
        raise redirect('/booking/day?day_id='+str(_id))
        

        
class BookingDay(BaseController):
    """
    The fallback controller for hollyrosa.
    
    By default, the final controller tried to fulfill the request
    when no other routes match. It may be used to display a template
    when all else fails, e.g.::
    
        def view(self, url):
            return render('/%s' % url)
    
    Or if you're using Mako and want to explicitly send a 404 (Not
    Found) response code when the requested template doesn't exist::
    
        import mako.exceptions
        
        def view(self, url):
            try:
                return render('/%s' % url)
            except mako.exceptions.TopLevelLookupException:
                abort(404)
    
    """
    
    
    def getAllDays(self):
        # TODO maybe stop caching and have a tuned view instead?
        try:
            tmp = self._all_days
        except AttributeError:
            all_days_c = getAllBookingDays(holly_couch)
            self._all_days = [DataContainer(id=d.key,  date=d.value) for d in all_days_c]
            tmp = self._all_days
       
        return tmp
        
        
    def getActivitySlotPositionsMap(self,  day_schema):
        """what do we map?"""
        try:
            tmp = self._activity_slot_position_map
        except AttributeError:
            self._activity_slot_position_map = day_schema['schema']
            tmp = self._activity_slot_position_map
            
        return tmp
        
    
    def fn_cmp_slot_row(self,  a,  b):
        return cmp(a.zorder,  b.zorder)
        
        
    def getActivitiesMap(self,  activities):
        """given a view from couchdb of activities, make a map/dict"""
        activities_map = dict()
        for a in activities:
            activities_map[a.doc['_id']] = a.doc
        return activities_map


    def make_slot_rows__of_day_schema(self,  day_schema,  activities_map,  dates):
        if not isinstance(dates,  list):
            dates = [dates]
        
        slot_row_schema = day_schema['schema']
        booking_days = [x.doc for x in getBookingDayOfDateList(holly_couch,  dates)]
        slot_rows = list()
        
        for tmp_activity_id, tmp_slots in slot_row_schema.items():
            tmp_activity = activities_map[tmp_activity_id]
            
            tmp_row = DataContainer(activity_id=tmp_activity_id,  zorder=tmp_slots[0]['zorder'] , title=tmp_activity['title'],  activity_group_id=tmp_activity['activity_group_id'],  bg_color=tmp_activity['bg_color'],  capacity=tmp_activity['capacity'])
            
            tmp_row.slot_row_position = []
            for tmp_day in booking_days: #te in dates:
                tmp_date = tmp_day['date']
                bdayid = tmp_day['_id']
                for s in tmp_slots[1:]:
                    tmp_row.slot_row_position.append( DataContainer(id=str(s['slot_id']),  time_from=s['time_from'],  time_to=s['time_to'],  duration=s['duration'],  date=tmp_date,  booking_day_id=bdayid) ) 
                
            slot_rows.append(tmp_row)
        
        slot_rows.sort(self.fn_cmp_slot_row)
        return slot_rows


    def getNonDeletedBookingsForBookingDay(self, holly_couch, day_id):
        # TODO refactor out view
        bookings_c = holly_couch.view('booking_day/non_deleted_bookings_of_booking_day',  keys=[day_id])
            
        # TODO: optimize away this dict thing
        bookings = dict()
        for x in bookings_c:
            b = x.value
            new_booking = DataContainer(id=b['_id'],  content=b['content'],  cache_content=b['cache_content'],  
                                        booking_state=b['booking_state'],  visiting_group_id=b['visiting_group_id'],  
                                        visiting_group_name=b['visiting_group_name'],  valid_from=b.get('valid_from', ''),  valid_to=b.get('valid_to', ''),  requested_date=b.get('requested_date', ''),  last_changed_by_id=b['last_changed_by_id'],  slot_id=b['slot_id'])
            ns = bookings.get(new_booking.slot_id, list())
            ns.append(new_booking)
            bookings[new_booking.slot_id] = ns
            
        return bookings
        

    def getNonDeletedLiveBookingsForBookingDay(self, holly_couch, start_date,  end_date):
        # TODO refactor out view
        # this is a modified copy of getNonDeletedBookingsForBookingDay
        bookings_c = holly_couch.view('booking_day_live/non_deleted_live_bookings_of_booking_day',  startkey=[start_date, ''],  endkey=[end_date, 'zzzzzzzzz'])
            
        # TODO: optimize away this dict thing
        bookings = dict()
        for x in bookings_c:
            b = x.value
            new_booking = DataContainer(id=b['_id'],  content=b['content'],  cache_content=b['cache_content'],  
                                        booking_state=b['booking_state'],  visiting_group_id=b['visiting_group_id'],  
                                        visiting_group_name=b['visiting_group_name'],  valid_from=b.get('valid_from', ''),  valid_to=b.get('valid_to', ''),  requested_date=b.get('requested_date', ''),  last_changed_by_id=b['last_changed_by_id'],  
                                        slot_id=x.key[1],  date=x.key[0])
            ns = bookings.get(new_booking.slot_id, list())
            ns.append(new_booking)
            bookings[new_booking.slot_id] = ns
            
        return bookings
        
    def getSlotStateOfBookingDayIdAndSlotId(self, holly_couch, booking_day_id,  slot_id):
        return [s for s in holly_couch.view('booking_day/slot_states',keys=[[booking_day_id, slot_id]],include_docs=True)]
        
        
    def getSlotBlockingsForBookingDay(self, holly_couch, day_id):
        # todo refactor
        blockings_map = dict()
        for x in holly_couch.view("booking_day/slot_state_of_booking_day",  keys=[day_id]):
            b = x.value
            # TODO: replace hack later. slot_id. and slot. 
            blockings_map[b['slot_id']] = DataContainer(level=b['level'],  booking_day_id=b['booking_day_id'],  slot_id=b['slot_id'])
            
        return blockings_map
        
        
    def getUnscheduledBookingsForToday(self, holly_couch, date,  activity_map):
        # need to convert 2011-10-01 to something like Fri Aug 05 2011
        # TODO: refactor
        tmp_date = datetime.datetime.strptime(date, "%Y-%m-%d" )
        tmp_date_f = tmp_date.strftime("%a %b %d %Y")
        
        unscheduled_bookings_c= holly_couch.view('booking_day/unscheduled_bookings_by_date',  keys=[tmp_date_f],  descending=True) 
        
        unscheduled_bookings = list()
        for x in unscheduled_bookings_c:
            
            b = x.value
            a_id = b['activity_id']
            a = activity_map[a_id]
            
            new_booking = DataContainer(id=b['_id'],  content=b['content'],  cache_content=b['cache_content'],  
                                        booking_state=b['booking_state'],  visiting_group_id=b['visiting_group_id'],  
                                        visiting_group_name=b['visiting_group_name'],  valid_from=b['valid_from'],  valid_to=b['valid_to'],  requested_date=b['requested_date'],  last_changed_by_id=b['last_changed_by_id'],  slot_id=b['slot_id'],  activity_title=a['title'],  activity_group_id=a['activity_group_id'],  activity_id=a_id)
            unscheduled_bookings.append(new_booking)
        
        return unscheduled_bookings
        
        
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
        
        
    #@expose
    def getSumNumberOfRequiredCrewMembers(self,  slots,  slot_rows):
        """compute required number of program crew members, fladan crew members"""
        crew_count = dict()
        crew_count['program_count'] = 0
        crew_count['fladan_count'] = 0
        
        for x in slots:
            ac = x.slot_row_position.slot_row.activity
            if 4 == ac.activity_group_id:
                crew_count['fladan_count'] += ac.guides_per_slot
            else:
                crew_count['program_count'] += ac.guides_per_slot
        
        #...now we can also compute roughly the number of guids per slot row:
        for x in slot_rows:
            ac = x.activity
            if 4 == ac.activity_group_id:
                crew_count['fladan_count'] += ac.guides_per_day
            else:
                crew_count['program_count'] += ac.guides_per_day
                
        return crew_count
        
        
    @expose('hollyrosa.templates.booking_day')
    @validate(validators={'day_id':validators.Int(not_empty=False), 'day':validators.DateValidator(not_empty=False)})
    def day(self,  day=None,  day_id=None):
        """Show a complete booking day"""
        
        # TODO: we really need to get only the slot rows related to our booking day schema or things will go wrong at some point when we have more than one schema to work with.
        
        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
        activities_map = self.getActivitiesMap(getAllActivities(holly_couch))
        
        if day_id != None:
            booking_day_o = common_couch.getBookingDay(holly_couch, day_id)
            
        elif day=='today':
    
            booking_day_o = getBookingDayOfDate(holly_couch, today_sql_date)
            day_id = booking_day_o['_id']
            
        else:
            booking_day_o = getBookingDayOfDate(holly_couch, str(day))
            day_id = booking_day_o['_id']
        
        #  TODO: fix row below
        booking_day_o['id'] = day_id
        
        day_schema_id = booking_day_o['day_schema_id']
        day_schema = common_couch.getDaySchema(holly_couch,  day_schema_id)#holly_couch[day_schema_id]
        
        slot_rows = self.make_slot_rows__of_day_schema(day_schema,  activities_map,  dates=[booking_day_o['date']])
        
        
        #...first, get booking_day for today
        new_bookings = self.getNonDeletedBookingsForBookingDay(holly_couch, day_id)
        
        #...we need a mapping from activity to a list / tupple slot_row_position
        #
        #   the new version should be a list of rows. Each row is either a DataContainer or a dict (basically the same...)
        #    We need to know activity name, color, id and group (which we get from the activities) and we need a list of slot positions
        activity_slot_position_map = self.getActivitySlotPositionsMap(day_schema) 
        
        #...find all unscheduled bookings
        showing_sql_date = str(booking_day_o['date'])
        unscheduled_bookings = self.getUnscheduledBookingsForToday(holly_couch, showing_sql_date,  activities_map)
        
        #...compute all blockings, create a dict mapping slot_row_position_id to actual state
        blockings_map = self.getSlotBlockingsForBookingDay(holly_couch, day_id)
        days = self.getAllDays()

        ##activity_groups = [DataContainer(id=d.value['_id'],  title=d.value['title']) for d in getAllActivityGroups(holly_couch)] 
        activity_groups = getActivityGroupNameAndIdList(holly_couch,  day_schema)
        return dict(booking_day=booking_day_o,  slot_rows=slot_rows,  bookings=new_bookings,  unscheduled_bookings=unscheduled_bookings,  activity_slot_position_map=activity_slot_position_map,  blockings_map=blockings_map,  workflow_map=workflow_map,  days=days,  getRenderContent=getRenderContent,  activity_groups=activity_groups, reFormatDate = reFormatDate)
    
    
    @expose('hollyrosa.templates.live_day')
    @validate(validators={'day_id':validators.Int(not_empty=False), 'day':validators.DateValidator(not_empty=False), 'schema_type':validators.UnicodeString(not_empty=False)})
    def live(self, day=None, day_id=None, schema_type='room'):
        """Show a complete booking day"""
        
        if schema_type=='funk':
            schema_type='staff'
        
        # TODO: we really need to get only the slot rows related to our booking day schema or things will go wrong at some point when we have more than one schema to work with.
        
        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
        activities_map = self.getActivitiesMap(getAllActivities(holly_couch))
        
        if day_id != None:
            booking_day_o = common_couch.getBookingDay(holly_couch, day_id)
            
        elif day=='today':
    
            booking_day_o = getBookingDayOfDate(holly_couch, today_sql_date)
            day_id = booking_day_o['_id']
            
        else:
            booking_day_o = getBookingDayOfDate(holly_couch, str(day))
            day_id = booking_day_o['_id']
        
        #  TODO: fix row below
        booking_day_o['id'] = day_id
        
        #...trying to find all days, lets say seven days after the indicated day
        first_date = booking_day_o['date']
        dates = dateRange2(first_date,  7)
        headers = []
        for tmp_date in dates:
            headers.append('FM (%s)' % tmp_date)
            headers.append('EM (%s)' % tmp_date)
        
        #...we also need a list of booking days in order to fill in all slots
        booking_o_list = []
        for tmp_date in dates:
            booking_o_list.append(getBookingDayOfDate(holly_couch, str(tmp_date)))
        
        #...we have to assume all days belong to the same day schema, otherwise, we really shouldnt display that day
        schema_id = booking_day_o[schema_type+'_schema_id']
        schema = common_couch.getDaySchema(holly_couch,  schema_id)
        schema_type = schema['subtype']
        title_hint = schema['title_hint']
        
        slot_rows = self.make_slot_rows__of_day_schema(schema,  activities_map,  dates=dates)
        #...first, get booking_day for today
        all_bookings = dict()
        all_blockings = dict()

        for tmp_date in dates:
            # TODO: ...too many lookups here
            tmp_booking_day_o = getBookingDayOfDate(holly_couch, tmp_date)
            tmp_day_id = tmp_booking_day_o['_id']
            tmp_bookings = self.getNonDeletedLiveBookingsForBookingDay(holly_couch,  tmp_date,  tmp_date)  #self.getNonDeletedBookingsForBookingDay(holly_couch, tmp_day_id)
            tmp_blockings = self.getSlotBlockingsForBookingDay(holly_couch, tmp_day_id)
            for k,  v in tmp_bookings.items():
                new_k = (str(tmp_date),  str(k)) # change to day id later
                all_bookings[new_k] = v
            for k,  v in tmp_blockings.items():
                new_k = (str(tmp_date),  str(k)) # change to day id later
                all_blockings[new_k] = v

        # TODO: need a map for bookings that not only looks at slot_id but also on date. Thats a combined key.
        
        #...we need a mapping from activity to a list / tupple slot_row_position
        #
        #   the new version should be a list of rows. Each row is either a DataContainer or a dict (basically the same...)
        #    We need to know activity name, color, id and group (which we get from the activities) and we need a list of slot positions
        activity_slot_position_map = self.getActivitySlotPositionsMap(schema) 
        
        #...find all unscheduled bookings
        showing_sql_date = str(booking_day_o['date'])
        
        # TODO need to show for the whole date range
        unscheduled_bookings = self.getUnscheduledBookingsForToday(holly_couch, showing_sql_date,  activities_map)
        
        #...compute all blockings, create a dict mapping slot_row_position_id to actual state
        # TODO need to show blockings for whole date range

        days = self.getAllDays()

        ##activity_groups = [DataContainer(id=d.value['_id'],  title=d.value['title']) for d in getAllActivityGroups(holly_couch)] 
        activity_groups = getActivityGroupNameAndIdList(holly_couch,  schema)
        return dict(booking_day=booking_day_o,  slot_rows=slot_rows,  bookings=all_bookings,  unscheduled_bookings=unscheduled_bookings,  activity_slot_position_map=activity_slot_position_map,  blockings_map=all_blockings,  workflow_map=workflow_map,  days=days,  getRenderContent=getRenderContent,  activity_groups=activity_groups, headers=headers, reFormatDate = reFormatDate, title_hint=title_hint, schema_type=schema_type)
    


    @expose('hollyrosa.templates.booking_day_fladan')
    @validate(validators={'day_id':validators.UnicodeString(not_empty=False), 'day':validators.DateValidator(not_empty=False), 'ag':validators.UnicodeString(not_empty=False)})
    def fladan_day(self,  day=None,  day_id=None, ag=''):
        """Show a complete booking day"""
        
        # TODO: move to common
        workflow_img_mapping = {}
        workflow_img_mapping['0'] = 'sheep.png'
        workflow_img_mapping['10'] = 'paper_to_sign.png'
        workflow_img_mapping['20'] = 'check_mark.png'
        workflow_img_mapping['-10'] = 'alert.png'
        workflow_img_mapping['-100'] = 'alert.png'
        workflow_img_mapping['unscheduled'] = 'alert.png'
        
        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")


        activities_map = self.getActivitiesMap(getAllActivities(holly_couch))
        
        if day_id != None and day_id != '':
            booking_day_o = getBookingDay(holly_couch, day_id)
                
        else:
            the_day = str(day)
            booking_day_o = getBookingDayOfDate(holly_couch, the_day)
            day_id = booking_day_o['_id']
        
        #  TODO: fix row below
        booking_day_o['id'] = day_id
        
        day_schema_id = booking_day_o['day_schema_id']
        day_schema = common_couch.getCouchDBDocument(holly_couch,  day_schema_id, 'day_schema') #holly_couch[day_schema_id]
        
        if ag != '':
            tmp_ag = common_couch.getCouchDBDocument(holly_couch,  ag, 'activity_group')
            ag_title = tmp_ag['title'] #holly_couch[ag]['title']
            slot_rows = [sr for sr in self.make_slot_rows__of_day_schema(day_schema,  activities_map, booking_day_o['date']) if sr.activity_group_id == ag]
        else:
            ag_title = 'All'  
            slot_rows = self.make_slot_rows__of_day_schema(day_schema,  activities_map, booking_day_o['date'])

        activity_slot_position_map = self.getActivitySlotPositionsMap(day_schema) 

        new_bookings = self.getNonDeletedBookingsForBookingDay(holly_couch, day_id)    
        blockings_map = self.getSlotBlockingsForBookingDay(holly_couch, day_id)
                        
        return dict(booking_day=booking_day_o,  slot_rows=slot_rows,  bookings=new_bookings,  activity_slot_position_map=activity_slot_position_map,  blockings_map=blockings_map,  workflow_map=workflow_map, activity_group=ag,  workflow_img_mapping=workflow_img_mapping, ag_title=ag_title, reFormatDate=reFormatDate)



        
    @expose()
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL may delete a booking request'))
    @validate(validators={'return_to_day_id':validators.UnicodeString(not_empty=True), 'booking_id':validators.UnicodeString(not_empty=True)})
    def delete_booking(self,  return_to_day_id=None,  booking_id=None):
        tmp_booking = common_couch.getBooking(holly_couch, booking_id) #holly_couch[booking_id]
        tmp_activity_id = tmp_booking['activity_id']
        remember_delete_booking_request(holly_couch, booking=tmp_booking, changed_by='',  activity_title=common_couch.getActivity(holly_couch,  tmp_activity_id)['title'])
        deleteBooking(holly_couch, tmp_booking)
        raise redirect('/booking/day?day_id='+str(return_to_day_id) + make_booking_day_activity_anchor(tmp_activity_id)) 
        

    def getBookingDayDate(self, booking_day_id):
        return common_couch.getBookingDay(holly_couch, booking_day_id)['date']#holly_couch[old_booking_day_id]['date']
        
    @validate(create_validate_unschedule_booking)
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may unschedule booking request'))
    def unschedule_booking(self,  return_to_day_id=None,  booking_id=None):
        b = common_couch.getBooking(holly_couch,  booking_id) 
        b['last_changed_by_id'] = getLoggedInUserId(request)
        b['booking_state'] = 0
        old_booking_day_id = b['booking_day_id']
        old_slot_id = b['slot_id']
        b['booking_day_id'] = ''
        b['slot_id'] = ''
        
        #...fix if valid_from , valid_to and requested date is None
        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
        try:
            datetime.datetime.strptime(b['valid_from'],  "%Y-%m-%d")
        except ValueError:
            #vgroup = holly_couch[b]
            date = self.getBookingDayDate( old_booking_day_id) #holly_couch[old_booking_day_id]['date']
            b['valid_from'] = date
        except TypeError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['valid_from'] = date
        except KeyError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['valid_from'] = date
            
        try:
            datetime.datetime.strptime(b['valid_to'],  "%Y-%m-%d")
        except ValueError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['valid_to'] = date
        except TypeError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['valid_to'] = date
        except KeyError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['valid_to'] = date
            
        try:
            datetime.datetime.strptime(b['requested_date'],  "%Y-%m-%d")
        except ValueError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['requested_date'] = date
        except TypeError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['requested_date'] = date
        except KeyError:
            date = self.getBookingDayDate( old_booking_day_id) 
            b['requested_date'] = date
            
        b['hide_warn_on_suspect_booking']  = False # TODO: refactor
        
        # TODO: refactor and safen
        holly_couch[b['_id']] = b
        
        booking_day = common_couch.getBookingDay(holly_couch,  old_booking_day_id)
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype='program')
        slot = slot_map[old_slot_id]
        activity = common_couch.getActivity(holly_couch,  b['activity_id'])
        
        remember_unschedule_booking(holly_couch, booking=b, slot_row_position=slot, booking_day=booking_day,  changed_by='',  activity=activity)

        raise redirect('day?day_id='+return_to_day_id + make_booking_day_activity_anchor(b['activity_id']))
        
        
    @validate(create_validate_schedule_booking)
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may schedule booking request'))
    def schedule_booking(self,  return_to_day_id=None,  booking_id=None,  booking_day_id=None,  slot_row_position_id=None):
        b = common_couch.getBooking(holly_couch,  booking_id)
        b['last_changed_by_id'] = getLoggedInUserId(request)
        b['booking_day_id'] = booking_day_id
        b['slot_id'] = slot_row_position_id
        b['hide_warn_on_suspect_booking'] = False
        activity = common_couch.getActivity(holly_couch,  b['activity_id'])
        # TODO: check that activity ids match
        b['booking_state'] = activity['default_booking_state']
        
        # TODO: check save
        holly_couch[b['_id']] = b
        booking_day = common_couch.getBookingDay(holly_couch,  b['booking_day_id'])
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype='program')
        slot = slot_map[slot_row_position_id]
        
        #...TODO: have all lookuped data in some local ctx that can be passed on to all helper functions so we dont have to do a lot of re-lookups
        remember_schedule_booking(holly_couch, booking=b, slot_row_position=slot, booking_day=booking_day,  activity=activity)
        
        if return_to_day_id == None:
            return_to_day_id = booking_day_id
        raise redirect('day?day_id='+return_to_day_id + make_booking_day_activity_anchor(b['activity_id']))
        
        
    @expose('hollyrosa.templates.edit_booked_booking')
    @validate(validators={'booking_day_id':validators.UnicodeString(not_empty=True), 'slot_id':validators.UnicodeString(not_empty=True), 'subtype':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may book a slot'))
    def book_slot(self,  booking_day_id=None,  slot_id=None, subtype='program'):
        tmpl_context.form = create_edit_book_slot_form
         
        #...find booking day and booking row
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        
        tmp_visiting_groups = getVisitingGroupsAtDate(holly_couch, booking_day['date']) 
        visiting_groups = [(e.doc['_id'],  e.doc['name']) for e in tmp_visiting_groups] 
        
        #...find out activity of slot_id for booking_day
#        schema = holly_couch[booking_day['day_schema_id']]
#        
#        activity_id = None
#        for tmp_activity_id,  tmp_slot_row in schema['schema'].items():
#            for tmp_slot in tmp_slot_row[1:]:
#                if tmp_slot['slot_id'] == slot_position_id:
#                    activity_id = tmp_activity_id
#                    slot = tmp_slot
#                    break
        slot_map= getSchemaSlotActivityMap(holly_couch, booking_day,  subtype='program')
        slot = slot_map[slot_id]        
        activity = common_couch.getActivity(holly_couch,  slot['activity_id']) 
        booking_o = DataContainer(content='', visiting_group_name='',  valid_from=None,  valid_to=None,  requested_date=None,  return_to_day_id=booking_day_id,  activity_id=slot['activity_id'], id=None,  activity=activity,  booking_day_id=booking_day_id,  slot_id=slot_id)
        
        return dict(booking_day=booking_day, booking=booking_o, visiting_groups=visiting_groups, edit_this_visiting_group=0,  slot_position=slot)


    def getEndSlotIdOptions(self,  living_schema_id,  activity_id):
        slot_row_schema = getSlotRowSchemaOfActivity(holly_couch,  living_schema_id,  activity_id) 
         
        end_slot_id_options = []
        
        print 'SLOT_ROW_SCHEMA',  slot_row_schema
        for t in slot_row_schema:
            print 'ITER 1'
            for slot in t.value[1:]:
                print 'SLOT',  slot 
                end_slot_id_options.append((slot['slot_id'],  slot['title']))
        return end_slot_id_options
        
        
    @expose('hollyrosa.templates.edit_booked_live_booking')
    @validate(validators={'booking_day_id':validators.UnicodeString(not_empty=True), 'slot_id':validators.UnicodeString(not_empty=True), 'subtype':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may book a slot'))
    def book_live_slot(self,  booking_day_id=None,  slot_id=None, subtype='live'):
        tmpl_context.form = create_edit_book_live_slot_form
         
        #...find booking day and booking row
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        
        #...TODO: only list visiting groups that lives indoors. That means they have a non-zero entry in the live sheet in the indoor column.
        tmp_visiting_groups = getVisitingGroupsAtDate(holly_couch, booking_day['date']) 
        visiting_groups = [(e.doc['_id'],  e.doc['name']) for e in tmp_visiting_groups] 
        
        #...find out activity of slot_id for booking_day
        slot_map= getSchemaSlotActivityMap(holly_couch, booking_day,  subtype=subtype)
        slot = slot_map[slot_id]
        activity = common_couch.getActivity(holly_couch,  slot['activity_id'])
       
        #...TODO: also extract the whole slot_row from the schema and remove the first entry. This will be needed for the date range to work correctly
        booking_o = DataContainer(content='', visiting_group_name='',  valid_from=None,  valid_to=None,  requested_date=None,  return_to_day_id=booking_day_id,  activity_id=slot['activity_id'], id=None,  activity=activity,  booking_day_id=booking_day_id,  slot_id=slot_id, booking_id=None)
    
        #...get schema from subtype
        schema_id_name_map = dict(live='room_schema_id', funk='funk_schema_id')
        schema_id = schema_id_name_map[subtype]
        
        schema_o = booking_day[schema_id] 
        end_slot_id_options = self.getEndSlotIdOptions(schema_o,  slot['activity_id'])
        return dict(booking_day=booking_day, booking=booking_o, visiting_groups=visiting_groups, edit_this_visiting_group=0,  slot_position=slot,  end_slot_id_options=end_slot_id_options)
        


    @expose('hollyrosa.templates.booking_view')
    @validate(validators={'booking_id':validators.UnicodeString(not_empty=True), 'return_to_day_id':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    def view_booked_booking(self,  return_to_day_id=None,  booking_id=None):
       
        #...find booking day and booking row
        booking_o = common_couch.getBooking(holly_couch,  booking_id) 
        booking_o.return_to_day_id = return_to_day_id
        activity_id = booking_o['activity_id']
        
        booking_day_id = None
        booking_day = None
        slot_position = None
        
        if booking_o.has_key('booking_day_id'):
            booking_day_id = booking_o['booking_day_id']
            if '' != booking_day_id:
                booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id) 
            
                slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype='program')
                slot_id = booking_o['slot_id']
                slot_position = slot_map[slot_id]
        
        activity = common_couch.getActivity(holly_couch,  activity_id) 
        history = [h.doc for h in getAllHistoryForBookings(holly_couch, [booking_id])]
        user_name_map = getUserNameMap(holly_couch)
        
        end_slot = None
        if booking_o.has_key('booking_end_slot_id'):
            end_slot = slot_map[booking_o['booking_end_slot_id']]
            
        
        return dict(booking_day=booking_day,  slot_position=slot_position, booking=booking_o,  workflow_map=workflow_map,  history=history,  change_op_map=change_op_map,  getRenderContent=getRenderContentDict,  activity=activity, formatDate=reFormatDate,  user_name_map=user_name_map,  end_slot=end_slot)
        
        
    @expose('hollyrosa.templates.edit_booked_booking')
    @validate(validators={'id':validators.UnicodeString(not_empty=True), 'return_to_day':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    def edit_booked_booking(self,  return_to_day_id=None,  booking_id=None,  **kw):
        
        #...find booking day and booking row
        booking_o = common_couch.getBooking(holly_couch,  booking_id)
        if booking_o['subtype'] == 'program':
            tmpl_context.form = create_edit_book_slot_form
        elif booking_o['subtype'] == 'live':
            tmpl_context.form = create_edit_book_live_slot_form
            # TODO: find out how to express this
            template = 'genshi:hollyrosa.templates.edit_booked_live_booking'
            override_template(self.edit_booked_booking, template) 
            
            
        booking_o['return_to_day_id'] = return_to_day_id
        
        booking_day_id = booking_o['booking_day_id']
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        slot_id = booking_o['slot_id']
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype=booking_o['subtype'])
        slot_position = slot_map[slot_id]
        activity_id = booking_o['activity_id']
        activity = common_couch.getActivity(holly_couch,  activity_id)
        booking_ = DataContainer(activity_id=activity_id, slot_id=slot_id, activity=activity,  id=booking_o['_id'] , booking_id=booking_o['_id'],  visiting_group_name=booking_o['visiting_group_name'],  visiting_group_id=booking_o['visiting_group_id'],  content=booking_o['content'], booking_date=booking_o.get('booking_date', '2013-07-01'), booking_end_date=booking_o.get('booking_end_date', '2013-07-24'), booking_end_slot_id=booking_o.get('booking_end_slot_id', ''),  return_to_day_id=return_to_day_id, booking_day_id=return_to_day_id )
        
        tmp_visiting_groups = getVisitingGroupsAtDate(holly_couch, booking_day['date']) 
        visiting_groups = [(e.doc['_id'],  e.doc['name']) for e in tmp_visiting_groups]  
        
        end_slot_id_options = self.getEndSlotIdOptions(booking_day['room_schema_id'],  slot_position['activity_id'])
        #end_slot_id_options = booking_o['slot_schema_row']
        return dict(booking_day=booking_day, slot_position=slot_position, booking=booking_,  visiting_groups=visiting_groups, edit_this_visiting_group=booking_o['visiting_group_id'],  activity=activity,  end_slot_id_options=end_slot_id_options,  living_schema_id=booking_day['room_schema_id'])
        
    
    # TODO is the error handler right?
    @validate(create_edit_book_live_slot_form, error_handler=edit_booked_booking)      
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked live booking properties'))
    def save_booked_live_booking_properties(self,  booking_id=None,  content=None,  visiting_group_name=None,  visiting_group_id=None,  activity_id=None,  return_to_day_id=None, slot_id=None,  booking_day_id=None,  booking_date=None,  booking_end_date=None,  booking_end_slot_id=None,  block_after_book=False ):
        tmp_activity_id = self.save_booked_booking_properties_helper(booking_id,  content,  visiting_group_name,  visiting_group_id,  activity_id,  return_to_day_id, slot_id,  booking_day_id,  booking_date=booking_date,  block_after_book=block_after_book,  subtype='live',  booking_end_date=booking_end_date,  booking_end_slot_id=booking_end_slot_id)
        raise redirect('live?day_id='+str(return_to_day_id) + make_booking_day_activity_anchor(tmp_activity_id))
    
    @validate(create_edit_book_slot_form, error_handler=edit_booked_booking) 
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    def save_booked_booking_properties(self,  id=None,  content=None,  visiting_group_name=None,  visiting_group_id=None,  activity_id=None,  return_to_day_id=None, slot_id=None,  booking_day_id=None,  block_after_book=False ):
        tmp_activity_id = self.save_booked_booking_properties_helper(id,  content,  visiting_group_name,  visiting_group_id,  activity_id,  return_to_day_id, slot_id,  booking_day_id,  block_after_book=block_after_book,  subtype='program')
        raise redirect('day?day_id='+str(return_to_day_id) + make_booking_day_activity_anchor(tmp_activity_id))
        
    def save_booked_booking_properties_helper(self,  id=None,  content=None,  visiting_group_name=None,  visiting_group_id=None,  activity_id=None,  return_to_day_id=None, slot_id=None,  booking_day_id=None,  booking_date=None,  block_after_book=False,  subtype='program',  booking_end_date='',  booking_end_slot_id=''):
        is_new = (None == id or '' == id) 
        #...id can be None if a new slot is booked
        booking_day = None
        
        #...there is a big difference on how booking_day_id is handled.
        #   for a programe booking, booking day id decides the date but on room bookings (live) it's the oposite.
        #   booking_date determines booking_day_id
        
        if is_new:
            old_booking = common_couch.createEmptyProgramBooking(subtype=subtype)
            
            if subtype == 'live':
                #...look up booking day by date
                booking_day = getBookingDayOfDate(holly_couch,  booking_date.strftime('%Y-%m-%d'))
                booking_day_id = booking_day['_id']
            else:
                booking_day = holly_couch[ booking_day_id ]
    
            old_booking['slot_id'] = slot_id
            old_booking['booking_day_id'] = booking_day_id
                
                
            if visiting_group_id !=None:
                vgroup = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
                old_booking['valid_from'] = vgroup['from_date']
                old_booking['valid_to'] = vgroup['to_date']
        else: # saving to existing booking
            old_booking = common_couch.getBooking(holly_couch,  id)
            
            if subtype == 'live':
                #...change booking_day_id according to booking date
                booking_day = getBookingDayOfDate(holly_couch,  booking_date.strftime('%Y-%m-%d'))
                booking_day_id = booking_day['_id']
                old_booking['slot_id'] = slot_id
                old_booking['booking_day_id'] = booking_day_id
            elif subtype == 'program':
                booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
            
        #...common for both new and existing bookings as well as program and room bookings
        old_visiting_group_name = old_booking.get('visiting_group_name', '')
        old_booking['visiting_group_name'] = visiting_group_name
        old_booking['visiting_group_id'] = visiting_group_id
        old_booking['last_changed_by_id'] = getLoggedInUserId(request)
        old_booking['content'] = content
        old_booking['cache_content'] = computeCacheContent(common_couch.getVisitingGroup(holly_couch,  visiting_group_id), content)
        
            
        #...make sure activity is set
        if (None != activity_id) or (''==activity_id):
            log.warn("activity is not set, using fallback method")
            tmp_activity_id = activity_id
            old_booking['activity_id'] = activity_id
        else:
            old_booking['activity'] = old_booking['slot_id'].activity_id # again we need to lookup activity
            tmp_activity_id = None
            
        activity = common_couch.getActivity(holly_couch,  tmp_activity_id)
        
        #...again we need to look up activity
        old_booking['booking_state'] = activity['default_booking_state']
        
        if is_new:
            ## shouldnt be necessary: booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
            slot_map  = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype=subtype)
            slot = slot_map[slot_id]
            new_uid = genUID(type='booking')            
            
            #...if subtype is live, then set dates and end-dates
            if subtype == 'live':
                old_booking['booking_date'] = booking_date.strftime('%Y-%m-%d') #booking_day['date']
                old_booking['booking_end_date'] = booking_end_date.strftime('%Y-%m-%d')
                old_booking['booking_end_slot_id'] = booking_end_slot_id
                old_booking['slot_id'] = slot_id # we dont change booking_date and slot_id on program bookings. They use the schedule method instead.
                tmp_schema_id = booking_day['room_schema_id']
                slot_row_schema_of_activity = getSlotRowSchemaOfActivity(holly_couch,  tmp_schema_id,  tmp_activity_id)
                slot_row_schema_of_activity = list(slot_row_schema_of_activity)[0].value[1:]
                old_booking['slot_schema_row'] = slot_row_schema_of_activity
            
            holly_couch[new_uid] = old_booking
            id = new_uid
            remember_book_slot(holly_couch, booking_id=new_uid, booking=old_booking,  slot_row_position=slot, booking_day=booking_day,  activity_title=activity['title'])
            
        else: # booking is not new.
            # shouldnt be necessary: booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
            slot_map  = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype=subtype)
            slot = slot_map[slot_id]
            
            if subtype == 'live':
                old_booking['slot_id'] = slot_id
                old_booking['booking_date'] = booking_day['date']
                old_booking['booking_end_date'] = booking_end_date.strftime('%Y-%m-%d')
                old_booking['booking_end_slot_id'] = booking_end_slot_id
                tmp_schema_id = booking_day['room_schema_id']
                slot_row_schema_of_activity = getSlotRowSchemaOfActivity(holly_couch,  tmp_schema_id,  tmp_activity_id)
                slot_row_schema_of_activity = list(slot_row_schema_of_activity)[0].value[1:]
                old_booking['slot_schema_row'] = slot_row_schema_of_activity
                
            #...TODO: update this remeber thing significantly
            remember_booking_properties_change(holly_couch, booking=old_booking, slot_row_position=slot, booking_day=booking_day,  old_visiting_group_name=old_visiting_group_name,  new_visiting_group_name=visiting_group_name, new_content='',  activity_title=activity['title'])
            
            holly_couch[id] = old_booking
        
        
        
        #...block after book?
        if block_after_book:
            self.block_slot_helper(holly_couch, booking_day_id,  slot_row_position_id)
        
        return tmp_activity_id
    
        
    @expose('hollyrosa.templates.view_activity')
    @validate(validators={'activity_id':validators.Int(not_empty=True)})
    def view_activity(self,  activity_id=None):
        activity = common_couch.getActivity(holly_couch, activity_id)
        
        #...replace missing fields with empty string
        for tmp_field in ['print_on_demand_link','external_link','internal_link','guides_per_slot','guides_per_day','equipment_needed','education_needed']:
            if not activity.has_key(tmp_field):
                activity[tmp_field] = ''
        return dict(activity=activity)
        
    
    @expose('hollyrosa.templates.edit_activity')
    @validate(validators={'activity_id':validators.Int(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change activity information'))
    def edit_activity(self, activity_id=None,  **kw):
        tmpl_context.form = create_edit_activity_form
        activity_groups = list()
        for x in getAllActivityGroups(holly_couch):
            activity_groups.append((x.value['_id'], x.value['title']))
            
        if None == activity_id:
            activity = DataContainer(id=None,  title='',  info='')
        elif id=='':
            activity = DataContainer(id=None,  title='', info='')
        else:
            try:
                activity = common_couch.getActivity(holly_couch,  activity_id) 
                activity['id'] = activity_id 
            except:
                activity = DataContainer(id=activity_id,  title='', info='', default_booking_state=0)
                
        return dict(activity=activity,  activity_group=activity_groups,  activity_groups=activity_groups)
        
        
    @validate(create_edit_activity_form, error_handler=edit_activity)      
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change activity properties'))
    def save_activity_properties(self,  id=None,  title=None,  external_link='', internal_link='',  print_on_demand_link='',  description='', tags='', capacity=0,  default_booking_state=0,  activity_group_id=1,  gps_lat=0,  gps_long=0,  equipment_needed=False, education_needed=False,  certificate_needed=False,  bg_color='', guides_per_slot=0,  guides_per_day=0 ):
        is_new = None == id or '' == id 
        if is_new:
            activity = dict(type='activity')
            id = genUID(type='activity')
            
        else:
            activity = common_couch.getActivity(holly_couch,  id)
                
        activity['title'] = title
        activity['description'] = description
        activity['external_link'] = external_link
        activity['internal_link'] = internal_link
        activity['print_on_demand_link'] = print_on_demand_link
        activity['tags'] = tags
        activity['capacity'] = capacity
#        #activity.default_booking_state=default_booking_state
        activity['activity_group_id'] = activity_group_id
#        activity.gps_lat = gps_lat
 #       activity.gps_long = gps_long
        activity['equipment_needed'] = equipment_needed
        activity['education_needed'] = education_needed
        activity['certificate_needed'] = certificate_needed
        activity['bg_color'] = bg_color
        activity['guides_per_slot'] = guides_per_slot
        activity['guides_per_day'] = guides_per_day
        
        holly_couch[id] = activity    
        raise redirect('/booking/view_activity',  activity_id=id)
     
        
    @expose('hollyrosa.templates.request_new_booking')
    @validate(validators={'return_to_day_id':validators.UnicodeString(not_empty=False), 'booking_id':validators.UnicodeString(not_empty=True), 'visiting_group_id':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change a booking'))
    def edit_booking(self,  return_to_day_id=None,  booking_id=None, visiting_group_id='', **kw):
        tmpl_context.form = create_edit_new_booking_request_form
        edit_this_visiting_group = 0
        
        activities = [(a.doc['_id'],  a.doc['title'] ) for a in getAllActivities(holly_couch)]
        if return_to_day_id == None: 
            visiting_groups = [(e.doc['_id'],  e.doc['name']) for e in getAllVisitingGroups(holly_couch)]
        else:
            booking_day_o = common_couch.getBookingDay(holly_couch,  return_to_day_id)
            visiting_groups = [(e.doc['_id'],  e.doc['name']) for e in getVisitingGroupsAtDate(holly_couch, booking_day_o['date'])]
            
        tmp_visiting_group = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
        
        
        #...patch since this is the way we will be called if validator for new will fail
        if (visiting_group_id != '') and (visiting_group_id != None):
            booking_o = DataContainer(id='', content='', visiting_group_id = visiting_group_id, visiting_group_name=tmp_visiting_group['name'])
            edit_this_visiting_group = 0 #visiting_group_id
        elif booking_id=='' or booking_id==None:
            booking_o = DataContainer(id='', content='')
        else:
            b = common_couch.getBooking(holly_couch,  booking_id)
            booking_o = DataContainer(id=b['_id'], content=b['content'], visiting_group_id=b['visiting_group_id'], valid_from=b['valid_from'], valid_to=b['valid_to'], requested_date=b['requested_date'], activity_id=b['activity_id'], visiting_group_name=b['visiting_group_name'])  
    
        # TODO: We still need to add some reasonable sorting on the activities abd the visiting groups
        
        if return_to_day_id != None and return_to_day_id != '':
            booking_o.requested_date = booking_day_o['date']
        booking_o.return_to_day_id = return_to_day_id
        return dict(visiting_groups=visiting_groups,  activities=activities, booking=booking_o,  edit_this_visiting_group=edit_this_visiting_group)
        
        
    @expose('hollyrosa.templates.move_booking')
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change a booking'))
    @validate(validators={'return_to_day_id':validators.UnicodeString(not_empty=False), 'booking_id':validators.UnicodeString(not_empty=False)})
    def move_booking(self,  return_to_day_id=None,  booking_id=None,  **kw):
        tmpl_context.form = create_move_booking_form
        activities = [(a.doc['_id'],  a.doc['title'] ) for a in getAllActivities(holly_couch)]
        
        #...patch since this is the way we will be called if validator for new will fail
        booking_o = common_couch.getBooking(holly_couch,  booking_id)
        booking_o.return_to_day_id = return_to_day_id
        activity_id,  slot_o = getSlotAndActivityIdOfBooking(holly_couch, booking_o,  booking_o['subtype'])
        activity_o = common_couch.getActivity(holly_couch,  booking_o['activity_id'])
        booking_day = common_couch.getBookingDay(holly_couch,  booking_o['booking_day_id'])
        booking_ = DataContainer(activity_id=activity_id,  content=booking_o['content'],  cache_content=booking_o['cache_content'],  visiting_group_name=booking_o['visiting_group_name'],  id=booking_o['_id'],  return_to_day_id=return_to_day_id)
        return dict(activities=activities, booking=booking_,  activity=activity_o,  booking_day=booking_day,  slot=slot_o,  getRenderContent=getRenderContent)
        
        
    @validate(create_move_booking_form, error_handler=move_booking)      
    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change activity properties'))
    def save_move_booking(self,  id=None,  activity_id=None,  return_to_day_id=None,  **kw):
        booking_o = common_couch.getBooking(holly_couch,  id)
        old_activity_id = booking_o['activity_id']

        
        #...slot row position must be changed, so we need to find slot row of activity and then slot row position with aproximately the same time span
        old_slot_id = booking_o['slot_id']
        #old_activity_id,  old_slot = getSlotAndActivityIdOfBooking(new_booking)
        booking_day_id = booking_o['booking_day_id']
        booking_day_o = common_couch.getBookingDay(holly_couch,  booking_day_id)
        
        # TODO read schema from booking_day
        if booking_o['subtype'] == 'program':
            schema_o = common_couch.getDaySchema(holly_couch,  booking_day_o['day_schema_id'])
        elif booking_o['subtype'] == 'live':
             schema_o = common_couch.getDaySchema(holly_couch,  booking_day_o['room_schema_id'])
             
        #...iterate thrue the schema first time looking for slot_id_position and activity
        the_schema = schema_o['schema']
        
        old_end_slot_id = booking_o.get('booking_end_slot_id', '')
        #...first, find the index of the slot id
        #...try match slot_id
        old_end_slot_index = None
        for tmp_activity_id,  tmp_activity_row in the_schema.items():
            tmp_slot_index = 1
            for tmp_slot in tmp_activity_row[1:]:
                if tmp_slot['slot_id'] == old_slot_id:
                    #...we got a match
                    old_activity_id_according_to_slot_id = tmp_activity_id
                    old_slot = tmp_slot
                    old_slot_index = tmp_slot_index
                elif tmp_slot['slot_id'] == old_end_slot_id:
                    old_end_slot_index = tmp_slot_index
                tmp_slot_index += 1
        
        #...now, find the 
        tmp_new_slot_row = the_schema[activity_id]
        new_slot = tmp_new_slot_row[old_slot_index]
        new_slot_id = new_slot['slot_id']
        
        new_end_slot_id = None
        if old_end_slot_index != None:
            new_end_slot = tmp_new_slot_row[old_end_slot_index]
            new_end_slot_id = new_end_slot['slot_id']
            
        #TODO: also need to change slot_schema_row as well as well as start and end slot id's
        old_slot_row_schema_of_activity = getSlotRowSchemaOfActivity(holly_couch,  schema_o['_id'],  old_activity_id)
        old_slot_row_schema_of_activity = list(old_slot_row_schema_of_activity)[0].value[1:]
     
        slot_row_schema_of_activity = getSlotRowSchemaOfActivity(holly_couch,  schema_o['_id'],  activity_id)
        slot_row_schema_of_activity = list(slot_row_schema_of_activity)[0].value[1:]
     

        booking_o['slot_schema_row'] = slot_row_schema_of_activity
        
        #TODO need to move slot_id and end_slot_id as well as slot_schema
        
        #new_slot_row = DBSession.query(booking.SlotRow).filter('activity_id='+str(activity_id)).one()
        #for tmp_slot_row_position in new_slot_row.slot_row_position:
         #   
         #   # TODO: too hackish below
         #   if tmp_slot_row_position.time_from == old_slot_row_position.time_from:
         #       new_booking.slot_row_position = tmp_slot_row_position
        
        #...it's not perfectly normalized that we also need to change activity id
        booking_o['activity_id'] = activity_id
        booking_o['slot_id'] = new_slot_id
        booking_o['booking_end_slot_id'] = new_end_slot_id
        holly_couch[booking_o['_id']] = booking_o
        
        activity_title_map = getActivityTitleMap(holly_couch)
        
        # TODO: remember move booking
        # TODO: problem is taht if move is done on a booking of type live we end up in the rong place...
        if  booking_o.get('subtype','program') == 'program':
            return_path = 'day'
        else:
            return_path = 'live'
        remember_booking_move(holly_couch, booking=booking_o,  booking_day=booking_day_o,  old_activity_title=activity_title_map[old_activity_id],  new_activity_title=activity_title_map[activity_id])
        
        raise redirect('/booking/'+return_path+'?day_id='+str(return_to_day_id)) 
        
        
    @validate(create_edit_new_booking_request_form, error_handler=edit_booking) 
    @require(Any(is_user('root'), has_level('view'), has_level('staff'), has_level('pl'),  msg='Only viewers, staff and PL can submitt a new booking request'))
    @expose()
    def save_new_booking_request(self, content='',  activity_id=None,  visiting_group_name='',  visiting_group_select=None,  valid_from=None,  valid_to=None,  requested_date=None,  visiting_group_id=None,  id=None,  return_to_day_id=None):
        is_new= ((id ==None) or (id==''))
        
        if is_new:
            new_booking = common_couch.createEmptyProgramBooking() # dict(type='booking',  subtype='program',  booking_day_id='', slot_id='') 
        else:
            new_booking = common_couch.getBooking(holly_couch,  id)
            tmp_activity = common_couch.getActivity(holly_couch,  new_booking['activity_id'])
            old_booking = DataContainer(activity=tmp_activity, activity_id=new_booking['activity_id'], visiting_group_name=new_booking['visiting_group_name'], visiting_group_id=new_booking['visiting_group_id'],  valid_from=new_booking['valid_from'],  valid_to=new_booking['valid_to'],  requested_date=new_booking['requested_date'],  content=new_booking['content'],  id=new_booking['_id'])
            
        if is_new:
            new_booking['booking_state'] = 0
        else:
           # DEPENDS ON WHAT HAS CHANGED. Maybe content change isnt enough to change state?
           new_booking['booking_state'] = 0
            
        new_booking['content'] = content
        
        new_booking['visiting_group_id'] = visiting_group_id
        
        new_booking['cache_content'] = computeCacheContent(common_couch.getVisitingGroup(holly_couch,  visiting_group_id),  content)
        
        
        new_booking['activity_id'] = activity_id
        new_booking['visiting_group_name'] = visiting_group_name
        new_booking['last_changed_by_id'] = getLoggedInUserId(request)
        

        #...todo add dates, but only after form validation
        new_booking['requested_date'] = str(requested_date)
        new_booking['valid_from'] = str(valid_from)
        new_booking['valid_to'] = str(valid_to)
        #new_booking['timestamp'] = 
        #raise IOError,  "%s %s %s" % (str(requested_date),  str(valid_from),  str(valid_to))
        
        if is_new:
            holly_couch[genUID(type='booking')] = new_booking
            remember_new_booking_request(holly_couch, new_booking)
        else:
            holly_couch[id] = new_booking

            remember_booking_request_change(holly_couch, old_booking=old_booking,  new_booking=new_booking)
            
        if return_to_day_id != None:
            if return_to_day_id != '':
                raise redirect('/booking/day?day_id='+str(return_to_day_id)) 
        if is_new:
            raise redirect('/visiting_group/view_all#vgroupid_'+str(visiting_group_id))
        raise redirect('/calendar/overview')
        
    
    @expose()
    @validate(validators={'return_to_day_id':validators.UnicodeString(not_empty=False), 'booking_id':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can block or unblock slots'))
    def prolong(self,  return_to_day_id=None, booking_id=None):
        # TODO: one of the problems with prolong that just must be sloved is what do we do if the day shema is different for the day after?
        
        #...first, find the slot to prolong to
        old_booking = common_couch.getBooking(holly_couch,  booking_id) # move into model
        booking_day_id = old_booking['booking_day_id']
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        day_schema_id = booking_day['day_schema_id']
        day_schema = common_couch.getDaySchema(holly_couch,  day_schema_id)
        old_slot_id = old_booking['slot_id']
        schema = day_schema['schema']

        #... TODO: find the slot and slot index. FACTOR OUT COMPARE MOVE BOOKING
        for tmp_activity_id,  tmp_activity_row in schema.items():
            tmp_slot_index = 1
            for tmp_slot in tmp_activity_row[1:]:
                if tmp_slot['slot_id'] == old_slot_id:
                    old_activity_id = tmp_activity_id
                    old_slot = tmp_slot
                    old_slot_index = tmp_slot_index
                    old_slot_row = tmp_activity_row
                    break
                tmp_slot_index += 1
        
        activity = common_couch.getActivity(holly_couch,  old_activity_id)
        
        if (old_slot_index+1) >= len(old_slot_row):
            flash('last slot')
            
            new_booking_day_id = getNextBookingDayId(holly_couch, booking_day)
            #new_booking_slot_row_position_id = slot_row_positions[0].id
            new_slot_id = old_slot_row[1]['slot_id']
        else:
            
#            i = 0
#            last_slrp = None
#            for slrp in slot_row_positions:
#                if last_slrp ==  old_booking.slot_row_position_id:
#                    break
#                last_slrp = slrp.id 
#            new_booking_slot_row_position_id = slrp.id
            new_slot_id = old_slot_row[old_slot_index+1]['slot_id']
            new_booking_day_id = booking_day_id
        
        #...then figure out if the slot to prolong to is blocked
        
        #todo: figure out if slot is blocked
        
        new_booking_slot_row_position_states = self.getSlotStateOfBookingDayIdAndSlotId(holly_couch, new_booking_day_id,  new_slot_id)
        
        #...if it isn't blocked, then book that slot.
        if len(new_booking_slot_row_position_states) == 0:

            #...find the booking
        
            new_booking = common_couch.createEmptyProgramBooking() #dict(type='booking')
            for k, v in old_booking.items():
                new_booking[k] = v
            
            new_booking['last_changed_by_id'] = getLoggedInUserId(request)
            new_booking['slot_id'] = new_slot_id
            new_booking['booking_day_id'] = new_booking_day_id
                               
                               #content=old_booking['content'],  cache_content=old_booking['cache_content'], activity_id=old_booking['activity_id'],  visiting_group_name=old_booking['visiting_group_name'] , 
                              # =, visiting_group_id=old_booking['visiting_group_id'] ,  requested_date=old_booking.get()['requested_date'], valid_from=old_booking['valid_from'], 
                             #  valid_to=old_booking['valid_to'] , booking_day_id=new_booking_day_id,  slot_id=new_slot_id )
            new_booking['booking_state'] = activity['default_booking_state']
            
            
            holly_couch[genUID(type='booking')] = new_booking
            remember_new_booking_request(holly_couch, new_booking)
        else:
            flash('wont prolong since next slot is blocked',  'warning')
            redirect('/booking/day?day_id='+str(booking_day_id)) 
            
        # TODO: remember prolong
            
        raise redirect('/booking/day?day_id='+str(new_booking['booking_day_id']) + make_booking_day_activity_anchor(new_booking['activity_id'])) 


    def getActivityIdOfBooking(self, holly_couch, booking_day_id,  slot_id, subtype='program'):
        """
        try to find activity given booking day and slot_id
        
        We need to find booking day, then schema, in schema there are rows per activity. Somewhere in that schema is the answer.
        """
        # TODO: refactor, should be able to use existing view
        booking_day_o = common_couch.getBookingDay(holly_couch,  booking_day_id)
        schema_name_map = dict(program='day_schema_id', live='room_schema_id', room='room_schema_id', funk='funk_schema_id')
        schema_name = booking_day_o[schema_name_map[subtype]]
        schema_o = common_couch.getDaySchema(holly_couch,  schema_name)
        
        #...iterate thrue the schema
        for tmp_activity_id,  tmp_activity_row in schema_o['schema'].items():
            for tmp_slot in tmp_activity_row[1:]:
                if tmp_slot['slot_id'] == slot_id:
                    return tmp_activity_id
                    
        # TODO: I dont think it is unreasonable that each schema has a lookuptable slot_id -> activity that is updated if the schema is updated.
        

    def block_slot_helper(self, holly_couch, booking_day_id,  slot_id,  level = 1, subtype='program'):
        slot_state = dict(slot_id=slot_id,  booking_day_id=booking_day_id, level=level,  type='slot_state')
        holly_couch[genUID(type='slot_state')] = slot_state 
        # TODO: set state variable when it has been introduced
        
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype=subtype)
        slot = slot_map[slot_id]
        remember_block_slot(holly_couch, slot_row_position=slot, booking_day=booking_day,  level=level,  changed_by=getLoggedInUserId(request),  activity_title=common_couch.getActivity(holly_couch,  slot['activity_id'] )['title'])
        
        
    @expose()
    @validate(validators={'booking_day_id':validators.UnicodeString(not_empty=True), 'slot_id':validators.UnicodeString(not_empty=True), 'level':validators.UnicodeString(not_empty=True), 'subtype':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can block or unblock slots'))
    def block_slot(self, booking_day_id=None,  slot_id=None,  level = 1, subtype='program'):
        self.block_slot_helper(holly_couch, booking_day_id, slot_id, level=level)
        activity_id = self.getActivityIdOfBooking(holly_couch, booking_day_id,  slot_id, subtype=subtype)
        if subtype == 'program':
            raise redirect('day?day_id='+booking_day_id + make_booking_day_activity_anchor(activity_id))
        raise redirect('live?day_id='+booking_day_id+'&schema_type='+subtype + make_booking_day_activity_anchor(activity_id))
    

    @expose()
    @validate(validators={'booking_day_id':validators.UnicodeString(not_empty=True), 'slot_id':validators.UnicodeString(not_empty=True), 'subtype':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can block or unblock slots'))
    def unblock_slot(self, booking_day_id=None,  slot_id=None, subtype='program'):
        
        # todo: set state variable when it has been introduced
        tmp_slot_state_ids = self.getSlotStateOfBookingDayIdAndSlotId(holly_couch,  booking_day_id,  slot_id)
        for tmp_slot_state_id in tmp_slot_state_ids:
            # TODO: optimize this, we shoud get the docs through the query above
            deleteme = common_couch.getSlotState(holly_couch,  tmp_slot_state_id.id)
            holly_couch.delete(deleteme)
        
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype=subtype)
        slot = slot_map[slot_id]
        activity_id = slot['activity_id']
        remember_unblock_slot(holly_couch, slot_row_position=slot, booking_day=booking_day,  changed_by=getLoggedInUserId(request),  level=0,  activity_title=common_couch.getActivity(holly_couch,  activity_id)['title'])

        if subtype == 'program':
            raise redirect('day?day_id='+booking_day_id + make_booking_day_activity_anchor(activity_id))
        raise redirect('live?day_id='+booking_day_id+'&schema_type='+subtype + make_booking_day_activity_anchor(activity_id))
    

    @expose('hollyrosa.templates.edit_multi_book')
    @validate(validators={'booking_id':validators.UnicodeString(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may use multibook functionality'))
    def multi_book(self,  booking_id=None,  **kw):
        booking_o = common_couch.getBooking(holly_couch,  booking_id)
        booking_day_id = booking_o['booking_day_id']
        booking_day = common_couch.getBookingDay(holly_couch,  booking_day_id)
        day_schema_id = booking_day['day_schema_id']
        day_schema = common_couch.getDaySchema(holly_couch,  day_schema_id)
         
        booking_days = [b.doc for b in getAllBookingDays(holly_couch)] 
        activity_id = booking_o['activity_id']
        activities_map = self.getActivitiesMap(getAllActivities(holly_couch))
        
        slot_rows = self.make_slot_rows__of_day_schema(day_schema,  activities_map, booking_day['date'])
        
        slot_row = [s for s in slot_rows if s.activity_id == activity_id][0]
        
        
        bookings = {}
        
        for tmp_booking_day in booking_days:
            bookings[tmp_booking_day.id] = {}
        
        slot_ids = [sp.id for sp in slot_row.slot_row_position]
        #for tmp_slot_row_position in slot_row.slot_row_position:
        bookings_of_slot_position = [b.doc for b in holly_couch.view('booking_day/slot_id_of_booking', keys=slot_ids ,include_docs=True)] 
            
        for tmp_booking in bookings_of_slot_position:
            #if None == tmp_slot_row_position.id:
            #    raise IOError,  "None not expected"
            if None == tmp_booking.id:
                raise IOError,  "None not expected"
            
            if None != tmp_booking['booking_day_id']:
                    
                if not bookings[tmp_booking['booking_day_id']].has_key(tmp_booking['slot_id']):
                    bookings[tmp_booking['booking_day_id']][tmp_booking['slot_id']] = []
                bookings[tmp_booking['booking_day_id']][tmp_booking['slot_id']].append(tmp_booking)
        
        
        blockings = [st.doc for st in holly_couch.view('booking_day/slot_state_of_slot_id', keys=slot_ids ,include_docs=True)] 
        blockings_map = dict()
        for b in blockings:
            tmp_booking_day_id = b['booking_day_id']
            blockings_map[str(tmp_booking_day_id)+':'''+ str(b['slot_id'])] = b
            
        return dict(booking=booking_o, booking_days=booking_days, booking_day=None, slot_row=slot_row,  blockings_map=blockings_map,  bookings=bookings, activities_map=activities_map, getRenderContent=getRenderContentDict)  

        
    @expose("json")
    @validate(validators={'booking_day_id':validators.Int(not_empty=True), 'slot_row_position_id':validators.Int(not_empty=True), 'activity_id':validators.Int(not_empty=True), 'content':validators.UnicodeString(not_empty=False), 'visiting_group_id_id':validators.Int(not_empty=True), 'block_after_book':validators.Bool(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    def create_booking_async(self,  booking_day_id=0,  slot_row_position_id=0,  activity_id=0,  content='', block_after_book=False,  visiting_group_id=None):
                
        #...TODO refactor to isBlocked
        slot_row_position_states = [b.doc for  b in holly_couch.view('booking_day/slot_state_of_slot_id_and_booking_day_id', keys=[booking_day_id, slot_row_position_id])]
        
        if 0 < len(slot_row_position_states):
            return dict(error_msg="slot blocked, wont book")
            
        else:
            vgroup = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
            new_id = genUID(type='booking')
            new_booking = common_couch.createEmptyProgramBooking() #dict(type='booking', booking_state=0, content=content, cache_content=computeCacheContent(vgroup, content))
            new_booking['booking_state']  =0
            new_booking['content'] =content
            new_booking['cache_content'] =computeCacheContent(vgroup, content)
            new_booking['activity_id'] = activity_id
            new_booking['last_changed_by_id'] = getLoggedInUserId(request)
            new_booking['visiting_group_id'] = visiting_group_id 
            new_booking['visiting_group_name'] = vgroup['name']
            
            # TODO: add dates, but only after form validation
            #new_booking.requested_date = old_booking.requested_date
            #new_booking.valid_from = old_booking.valid_from
            #new_booking.valid_to = old_booking.valid_to
                
            new_booking['booking_day_id'] = booking_day_id
            new_booking['slot_id'] = slot_row_position_id
            
            holly_couch[new_id] = new_booking
                
            remember_new_booking_request(holly_couch, new_booking)
            slot_row_position_state = 0
            if block_after_book:
                self.block_slot_helper(holly_couch, booking_day_id, slot_row_position_id, level=1)
                slot_row_position_state = 1
                
        return dict(text="hello",  booking_day_id=booking_day_id,  slot_row_position_id=slot_row_position_id, booking=new_booking,  visiting_group_name=vgroup['name'], success=True, slot_row_position_state=slot_row_position_state)

        
    @expose("json")
    @validate(validators={'delete_req_booking_id':validators.UnicodeString(not_empty=True), 'activity_id':validators.Int(not_empty=True), 'visiting_group_id_id':validators.Int(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    def delete_booking_async(self,  delete_req_booking_id=0,  activity_id=0,  visiting_group_id=None):
        vgroup = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
        booking_o = common_couch.getBooking(holly_couch, delete_req_booking_id)
        remember_delete_booking_request(holly_couch, booking_o)
        deleteBooking(holly_couch, booking_o)

        return dict(text="hello", delete_req_booking_id=delete_req_booking_id, visiting_group_name=vgroup['name'], success=True)
        
        
        
    @expose("json")
    @validate(validators={'booking_id':validators.UnicodeString(not_empty=True)})
    @require(Any(is_user('root'), has_level('pl'), msg='Only pl members may change booked booking properties'))
    def ignore_booking_warning_async(self, booking_id=''):
        booking_o = common_couch.getBooking(holly_couch,  booking_id)
        ##remember_delete_booking_request(holly_couch, booking_o)
        ##deleteBooking(holly_couch, booking_o)
        booking_o['hide_warn_on_suspect_booking'] = True
        holly_couch[booking_id] = booking_o
        tmp_activity = common_couch.getActivity(holly_couch,  booking_o['activity_id'])
        booking_day= common_couch.getBookingDay(holly_couch,  booking_o['booking_day_id'])        
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype='program')
        slot = slot_map[booking_o['slot_id']]
         
        
        remember_ignore_booking_warning(holly_couch, booking=booking_o, slot_row_position=slot, booking_day=booking_day,  changed_by=getLoggedInUserId(request),  activity=tmp_activity)
        
        return dict(booking_id=booking_id)
        
        
    @expose("json")
    @validate(validators={'delete_req_booking_id':validators.Int(not_empty=True), 'activity_id':validators.Int(not_empty=True), 'visiting_group_id_id':validators.Int(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    def unschedule_booking_async(self,  delete_req_booking_id=0,  activity_id=0,  visiting_group_id=None):
        vgroup = common_couch.getVisitingGroup(holly_couch,  visiting_group_id)
        booking_o = common_couch.getBooking(holly_couch,  delete_req_booking_id)
        booking_o.last_changed_by_id = getLoggedInUserId(request)
        booking_day = common_couch.getBookingDay(holly_couch,  booking_o['booking_day_id'])
        old_slot_id = booking_o['slot_id']
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day,  subtype='program')
        slot = slot_map[old_slot_id]
        activity = common_couch.getActivity(holly_couch,  booking_o['activity_id'])
        remember_unschedule_booking(holly_couch, booking=booking_o, slot_row_position=slot, booking_day=booking_day,  changed_by='', activity=activity)
        booking_o['booking_state'] = 0
        booking_o['booking_day_id'] = None
        booking_o['slot_row_position_id'] = None
        holly_couch[booking_o['_id']] = booking_o
        
        return dict(text="hello",  delete_req_booking_id=delete_req_booking_id, visiting_group_name=vgroup['name'], success=True)
        
