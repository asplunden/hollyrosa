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
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID,  holly_couch
from hollyrosa.model.booking_couch import getAllScheduledBookings,  getAllUnscheduledBookings,  gelAllBookingsWithBookingState,  getActivityTitleMap,  getBookingDayInfoMap,  getUserNameMap,  getSchemaSlotActivityMap
from sqlalchemy import and_
import datetime

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context



from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking

from booking_history import  remember_workflow_state_change
from hollyrosa.controllers.common import workflow_map,  getLoggedInUserId,  has_level

from formencode import validators

__all__ = ['Workflow']

workflow_submenu = """<ul class="any_menu">
        <li><a href="overview">overview</a></li>
        <li><a href="view_preliminary">preliminary</a></li>
        <li><a href="view_nonapproved">non-approved</a></li>
        <li><a href="view_unscheduled">unscheduled</a></li>
        <li><a href="view_scheduled">scheduled</a></li>
        <li><a href="view_disapproved">dissapproved</a></li>
    </ul>"""

class Workflow(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
    
    
    @expose('hollyrosa.templates.workflow_overview')
    def overview(self):
        """Show an overview of all bookings"""
        scheduled_bookings = [b.doc for b in getAllScheduledBookings()]
        unscheduled_bookings = [b.doc for b in getAllUnscheduledBookings()]
        
        #...I need a map from booking_day_id to booking day date and from [booking_day_i, slot_id] to time.
        #   actually, I do thin couch could create such a view, it's just going to be very messy 
        # TODO: in the future we cant use a hard coded day schema, we will need one map for each day schema that exists.
        return dict(scheduled_bookings=scheduled_bookings,  unscheduled_bookings=unscheduled_bookings,  workflow_map=workflow_map,  activity_map=getActivityTitleMap(),  booking_date_map=getBookingDayInfoMap(),  user_name_map=getUserNameMap(), slot_map=getSchemaSlotActivityMap('day_schema.1'),  workflow_submenu=workflow_submenu)
        
        
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_nonapproved(self):
        #scheduled_bookings = DBSession.query(booking.Booking).filter(and_('booking_state < 20', 'booking_state > -100', 'booking_day_id is not NULL')).all()
        scheduled_bookings = [b.doc for b in gelAllBookingsWithBookingState([0,  10,  -10])] 
        return dict(scheduled_bookings=scheduled_bookings,  workflow_map=workflow_map, result_title='Unapproved scheduled bookings',  activity_map=getActivityTitleMap(), booking_date_map=getBookingDayInfoMap(), user_name_map=getUserNameMap(),  slot_map=getSchemaSlotActivityMap('day_schema.1'), workflow_submenu=workflow_submenu)
    
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_preliminary(self):
        scheduled_bookings = [b.doc for b in gelAllBookingsWithBookingState([0])] #DBSession.query(booking.Booking).filter(and_('booking_state < 10', 'booking_state > -100', 'booking_day_id is not NULL')).all()
        return dict(scheduled_bookings=scheduled_bookings,  workflow_map=workflow_map, result_title='Preliminary scheduled bookings',  activity_map=getActivityTitleMap(), booking_date_map=getBookingDayInfoMap(), user_name_map=getUserNameMap(), slot_map=getSchemaSlotActivityMap('day_schema.1'), workflow_submenu=workflow_submenu)
    
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_scheduled(self):
        scheduled_bookings = [b.doc for b in getAllScheduledBookings()] #DBSession.query(booking.Booking).filter(and_('booking_day_id is not NULL', 'booking_state > -100')).all()
        return dict(scheduled_bookings=scheduled_bookings,   workflow_map=workflow_map, result_title='Schedueld bookings',  activity_map=getActivityTitleMap(), booking_date_map=getBookingDayInfoMap(), user_name_map=getUserNameMap(), slot_map=getSchemaSlotActivityMap('day_schema.1'), workflow_submenu=workflow_submenu)
        
        
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_disapproved(self):
        scheduled_bookings = scheduled_bookings = [b.doc for b in gelAllBookingsWithBookingState([-10])]  #DBSession.query(booking.Booking).filter(and_('booking_state < 0', 'booking_state > -100', 'booking_day_id is not NULL')).all()
        return dict(scheduled_bookings=scheduled_bookings,   workflow_map=workflow_map, result_title='Disapproved bookings', activity_map=getActivityTitleMap(), booking_date_map=getBookingDayInfoMap(), user_name_map=getUserNameMap(), slot_map=getSchemaSlotActivityMap('day_schema.1'), workflow_submenu=workflow_submenu)
    
    
    @expose('hollyrosa.templates.workflow_view_unscheduled')
    def view_unscheduled(self):
        unscheduled_bookings = [b.doc for b in getAllUnscheduledBookings()] #DBSession.query(booking.Booking).filter(and_('booking_day_id is NULL','booking_state > -100')).all()
        return dict(unscheduled_bookings=unscheduled_bookings,  workflow_map=workflow_map, result_title='Unscheduled bookings', activity_map=getActivityTitleMap(), booking_date_map=getBookingDayInfoMap(), user_name_map=getUserNameMap(), slot_map=getSchemaSlotActivityMap('day_schema.1'), workflow_submenu=workflow_submenu)
    
    def do_set_state(self, booking_id,  booking_o,  state):
        
        #...only PL can set state=20 (approved) or -10 (disapproved)
        
        if state=='20' or state=='-10' or booking_o['booking_state'] == 20 or booking_o['booking_state']==-10:
            #ok = False
            #for group in getLoggedInUserId(request):
            #    if group.group_name == 'pl':
            #        ok = True
            ok = has_level('pl').check_authorization(request.environ)
            
            # TODO: fix
            
#            if not ok:
#                flash('Only PL can do that. %s' % request.referrer, 'warning')
#                raise redirect(request.referrer)
        activity = holly_couch[booking_o['activity_id']]
        booking_day = holly_couch[booking_o['booking_day_id']]
        remember_workflow_state_change(booking=booking_o,  state=state,  booking_day_date=booking_day['date'],  activity_title=activity['title'])
        booking_o['booking_state'] = state
        booking_o['ast_changed_by_id'] = getLoggedInUserId(request)
        holly_couch[booking_id] = booking_o

    @expose()
    @validate(validators={'booking_id':validators.UnicodeString(not_empty=True), 'state':validators.Int(not_empty=True), 'all':validators.Int(not_empty=False)})    
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def set_state(self,  booking_id=None,  state=0, all=0):
        if all == 0 or all==None:
            booking_o = holly_couch[booking_id] 
            self.do_set_state(booking_id,  booking_o, state)
        elif all == '1': # look for all bookings with same group
           booking_o = holly_couch[booking_id] 
           bookings = [ ] # Fix later DBSession.query(booking.Booking).filter(and_('visiting_group_id='+str(booking_o.visiting_group_id), 'activity_id='+str(booking_o.activity_id), 'booking_state > -100')).all()
           for new_b in bookings:
               if (new_b.content.strip() == booking_o.content.strip()) and (new_b.booking_day_id != None):
                   self.do_set_state(new_b._id,  new_b, state)
        else:
            pass        
        raise redirect(request.referrer)

       
    
