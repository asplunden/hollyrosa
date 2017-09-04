# -*- coding: utf-8 -*-
"""
Copyright 2010-2017 Martin Eliasson

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

from tg import expose, flash, require, url, request, redirect, validate
from tg.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, holly_couch
from hollyrosa.model.booking_couch import getAllScheduledBookings,  getAllUnscheduledBookings,  gelAllBookingsWithBookingState,  getActivityTitleMap,  getBookingDayInfoMap,  getUserNameMap,  getSchemaSlotActivityMap, getAllSimilarBookings
from hollyrosa.controllers.common import ensurePostRequest

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context

from booking_history import  remember_workflow_state_change
from hollyrosa.controllers.common import workflow_map,  getLoggedInUserId,  has_level

from formencode import validators
from hollyrosa.controllers.activity import ensurePostRequest

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
        scheduled_bookings = [b.doc for b in getAllScheduledBookings(holly_couch)]
        unscheduled_bookings = [b.doc for b in getAllUnscheduledBookings(holly_couch)]
        
        #...I need a map from booking_day_id to booking day date and from [booking_day_i, slot_id] to time.
        #   actually, I do thin couch could create such a view, it's just going to be very messy 
        # TODO: in the future we cant use a hard coded day schema, we will need one map for each day schema that exists.
        return dict(scheduled_bookings=scheduled_bookings,  unscheduled_bookings=unscheduled_bookings,  workflow_map=workflow_map,  activity_map=getActivityTitleMap(holly_couch),  booking_date_map=getBookingDayInfoMap(holly_couch),  user_name_map=getUserNameMap(holly_couch), slot_map=getSchemaSlotActivityMap(holly_couch, 'day_schema.1'),  workflow_submenu=workflow_submenu)
        
        
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_nonapproved(self):
        scheduled_bookings = [b.doc for b in gelAllBookingsWithBookingState(holly_couch, [0,  10,  -10])] 
        return dict(scheduled_bookings=scheduled_bookings,  workflow_map=workflow_map, result_title='Unapproved scheduled bookings',  activity_map=getActivityTitleMap(holly_couch), booking_date_map=getBookingDayInfoMap(holly_couch), user_name_map=getUserNameMap(holly_couch),  slot_map=getSchemaSlotActivityMap(holly_couch, 'day_schema.1'), workflow_submenu=workflow_submenu)
    
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_preliminary(self):
        scheduled_bookings = [b.doc for b in gelAllBookingsWithBookingState(holly_couch, [0])] 
        return dict(scheduled_bookings=scheduled_bookings,  workflow_map=workflow_map, result_title='Preliminary scheduled bookings',  activity_map=getActivityTitleMap(holly_couch), booking_date_map=getBookingDayInfoMap(holly_couch), user_name_map=getUserNameMap(holly_couch), slot_map=getSchemaSlotActivityMap(holly_couch, 'day_schema.1'), workflow_submenu=workflow_submenu)
    
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_scheduled(self):
        scheduled_bookings = [b.doc for b in getAllScheduledBookings(holly_couch)] 
        return dict(scheduled_bookings=scheduled_bookings, workflow_map=workflow_map, result_title='Schedueld bookings',  activity_map=getActivityTitleMap(holly_couch), booking_date_map=getBookingDayInfoMap(holly_couch), user_name_map=getUserNameMap(holly_couch), slot_map=getSchemaSlotActivityMap(holly_couch, 'day_schema.1'), workflow_submenu=workflow_submenu)
        
        
    @expose('hollyrosa.templates.workflow_view_scheduled')
    def view_disapproved(self):
        scheduled_bookings = scheduled_bookings = [b.doc for b in gelAllBookingsWithBookingState(holly_couch, [-10])]
        return dict(scheduled_bookings=scheduled_bookings,   workflow_map=workflow_map, result_title='Disapproved bookings', activity_map=getActivityTitleMap(holly_couch), booking_date_map=getBookingDayInfoMap(holly_couch), user_name_map=getUserNameMap(holly_couch), slot_map=getSchemaSlotActivityMap(holly_couch, 'day_schema.1'), workflow_submenu=workflow_submenu)
    
    
    @expose('hollyrosa.templates.workflow_view_unscheduled')
    def view_unscheduled(self):
        unscheduled_bookings = [b.doc for b in getAllUnscheduledBookings(holly_couch)] 
        return dict(unscheduled_bookings=unscheduled_bookings,  workflow_map=workflow_map, result_title='Unscheduled bookings', activity_map=getActivityTitleMap(holly_couch), booking_date_map=getBookingDayInfoMap(holly_couch), user_name_map=getUserNameMap(holly_couch), slot_map=getSchemaSlotActivityMap(holly_couch, 'day_schema.1'), workflow_submenu=workflow_submenu)
    
    def do_set_state(self, holly_couch, booking_id,  booking_o,  state):
        
        #...only PL can set state=20 (approved) or -10 (disapproved)
        
        if state=='20' or state=='-10' or booking_o['booking_state'] == 20 or booking_o['booking_state']==-10:
            ok = has_level('pl').check_authorization(request.environ)
            
            # TODO: fix
            
#            if not ok:
#                flash('Only PL can do that. %s' % request.referrer, 'warning')
#                raise redirect(request.referrer)
        activity = holly_couch[booking_o['activity_id']]
        booking_day = holly_couch[booking_o['booking_day_id']]
        
        booking_o['booking_state'] = state
        booking_o['last_changed_by_id'] = getLoggedInUserId(request)
        
        holly_couch[booking_id] = booking_o
        remember_workflow_state_change(holly_couch, booking=booking_o, state=state,  booking_day_date=booking_day['date'],  activity_title=activity['title'])

    @expose()
    @validate(validators={'booking_id':validators.UnicodeString(not_empty=True), 'state':validators.Int(not_empty=True), 'all':validators.Int(not_empty=False)})    
    @require(Any(has_level('staff'), has_level('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def set_state(self, booking_id=None,  state=0, all=0):
        ensurePostRequest(request, __name__)
        if all == 0 or all==None:
            booking_o = holly_couch[booking_id] 
            self.do_set_state(holly_couch, booking_id,  booking_o, state)
        elif all == 1: # look for all bookings with same group
            booking_o = holly_couch[booking_id] 
            bookings = [b.doc for b in getAllSimilarBookings(holly_couch, [booking_o['visiting_group_id'], booking_o['activity_id']]) ] # TODO: Fix later DBSession.query(booking.Booking).filter(and_('visiting_group_id='+str(booking_o.visiting_group_id), 'activity_id='+str(booking_o.activity_id), 'booking_state > -100')).all()
            for new_b in bookings:
                if (new_b['content'].strip() == booking_o['content'].strip()) and (new_b['booking_day_id'] != None):
                    self.do_set_state(holly_couch, new_b['_id'],  new_b, state)
        else:
            pass
            
        
        if 'booking/day' in request.referrer:
            raise redirect(request.referrer + '#activity_row_id_' + booking_o['activity_id'])
            
        raise redirect(request.referrer)

       
    
