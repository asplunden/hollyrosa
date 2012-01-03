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

import time
from repoze.what.predicates import Any, is_user, has_permission
from formencode import validators
from tg import expose, flash, require, url, request, redirect,  validate
from hollyrosa.lib.base import BaseController
from hollyrosa.model import DBSession, metadata,  booking,  holly_couch
from sqlalchemy import and_
import datetime,  types
from hollyrosa.controllers.common import workflow_map,  getFormatedDate,  getLoggedInDisplayName,  change_op_map,  change_op_lookup

__all__ = ['History']





def remember_booking_change(booking_id=None,  booking_day_id=None,  change_op=None,  change_text='',  changed_by='',  booking_content=''):
    """
    For a better view of booking history, its better we have an enum (int) telling what kind of change we have:
    * schedule
    *unschedule
    *book_slot
    *new_booking_request
    *delete_booking_request
    *booking_properties_change
    *booking_request_change
    *booking_state_change
    *block_soft
    *block_hard
    *unblock
    *workflow_state_change
    """
    
    bh = booking.BookingHistory()
    
    if type(change_op) ==types.StringType:
        change_op = change_op_lookup[change_op]
    bh.change_op = change_op
    bh.booking_content=booking_content
    bh.change = change_text
    bh.changed_by = getLoggedInDisplayName(request) #.identity.get('user', dummy_identity).display_name)
    bh.timestamp = datetime.datetime.now()
    bh.booking_id = booking_id
    bh.booking_day_id = booking_day_id
    DBSession.add(bh)
    
def remember_schedule_booking(booking=None, slot_row_position=None, booking_day=None,  changed_by=''):
    """Trapper booking for HSS scheduled wedneday january 10 19:10 to 21:15"""
    text = '%s booking for %s scheduled %s between %s and %s' %(slot_row_position.slot_row.activity.title, booking.visiting_group_name,  getFormatedDate(booking_day.date),  slot_row_position.time_from.strftime('%H:%M'),  slot_row_position.time_to.strftime('%H:%M'))
    
    remember_booking_change(booking_id=booking.id,  change_op=1,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day.id)


def remember_unschedule_booking(booking=None, slot_row_position=None, booking_day=None,  changed_by=''):
    """Trapper booking for HSS scheduled wedneday january 10 19:10 to 21:15"""
    if booking.slot_row_position != None:
        text = '%s booking for %s unscheduled. Was scheduled for %s between %s and %s' %(slot_row_position.slot_row.activity.title, booking.visiting_group_name,  getFormatedDate(booking_day.date),  slot_row_position.time_from.strftime('%H:%M'),  slot_row_position.time_to.strftime('%H:%M'))
    else:
        text = 'WARN: no slot_row_position for unscheduled booking. Cannot determine the time of unscheduling or activity but group was %s and bookingdate %s.' %(booking.visiting_group_name,  getFormatedDate(booking_day.date))
    remember_booking_change(booking_id=booking.id,  change_op=2,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day.id)


def remember_book_slot(booking=None, slot_row_position=None, booking_day=None,  changed_by=''):
    """Trapper booked for HSS wedneday january 10 19:10 to 21:15"""
    text = '%s slot booked for %s %s between %s and %s' %(slot_row_position.slot_row.activity.title, booking.visiting_group_name,  getFormatedDate(booking_day.date),  slot_row_position.time_from.strftime('%H:%M'),  slot_row_position.time_to.strftime('%H:%M'))
    
    remember_booking_change(booking_id=booking.id,  change_op=3,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day.id)
    
    
def remember_booking_properties_change(booking=None, slot_row_position=None, booking_day=None,  old_visiting_group_name='',  new_visiting_group_name='', new_content='', changed_by=''):
    """Trapper booked for HSS wedneday january 10 19:10 to 21:15"""
    text = '%s booking for %s properties changed to %s, slot on %s between %s and %s' %(slot_row_position.slot_row.activity.title, old_visiting_group_name,  new_visiting_group_name,  getFormatedDate(booking_day.date),  slot_row_position.time_from.strftime('%H:%M'),  slot_row_position.time_to.strftime('%H:%M'))
    
    remember_booking_change(booking_id=booking.id,  change_op=7,  change_text=text,  changed_by=changed_by, booking_day_id=booking_day.id)
    

def remember_new_booking_request(booking=None, changed_by=''):
    """Trapper requested for HSS wedneday january 10 to friday januari 12"""
    text = '%s requested for %s %s to %s' %(booking.activity.title, booking.visiting_group_name,  getFormatedDate(booking.valid_from),  getFormatedDate(booking.valid_to))
    
    remember_booking_change(booking_id=booking.id,  change_op=4,  change_text=text,  changed_by=changed_by)
    
    
def remember_delete_booking_request(booking=None, changed_by=''):
    """deleted Trapper requested for HSS wedneday january 10 to friday januari 12"""
    text = 'deleted %s requested for %s %s to %s' %(booking.activity.title, booking.visiting_group_name, getFormatedDate(booking.valid_from), getFormatedDate(booking.valid_to))
    remember_booking_change(booking_id=booking.id,  change_op=6,  change_text=text,  changed_by=changed_by)
    

def remember_booking_request_change(old_booking=None, new_booking=None, changed_by=''):
    """Change Trapper requested for HSS wedneday january 10 to friday januari 12 . Changed to """
    text = 'Change %s requested for %s %s to %s. Changed to %s requested for %s %s to %s.' %(old_booking.activity.title, old_booking.visiting_group_name,  getFormatedDate(old_booking.valid_from),  getFormatedDate(old_booking.valid_to),  new_booking.activity.title, new_booking.visiting_group_name,  getFormatedDate(new_booking.valid_from),  getFormatedDate(new_booking.valid_to))
    
    remember_booking_change(booking_id=old_booking.id,  change_op=5,  change_text=text,  changed_by=changed_by)
    
    
def remember_block_slot(slot_row_position=None, booking_day=None,  level=0,  changed_by=''):
    """Ekohuset slot blocked on level 4 wedneday january 10 between 09:00 and 12:00"""
    text = '%s slot blocked on level %d %s between %s and %s' %(slot_row_position.slot_row.activity.title, level,  getFormatedDate(booking_day.date),  slot_row_position.time_from.strftime('%H:%M'),  slot_row_position.time_to.strftime('%H:%M'))
    
    remember_booking_change(booking_id=None,  change_op=9,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day.id)
    
    
def remember_unblock_slot(slot_row_position=None, booking_day=None,  level=0,  changed_by=''):
    """Ekohuset slot unblocked from level 4 wedneday january 10 between 09:00 and 12:00"""
    text = '%s slot unblocked from level %d %s between %s and %s' %(slot_row_position.slot_row.activity.title, level,  booking_day.date.strftime('%A %B %d'),  slot_row_position.time_from.strftime('%H:%M'),  slot_row_position.time_to.strftime('%H:%M'))
    
    remember_booking_change(booking_id=None,  change_op=11,  change_text=text,  changed_by=changed_by, booking_day_id=booking_day.id)
    
    
def remember_workflow_state_change(booking=None, state=None, changed_by=''):
    """Workflow state changed for Trapper booking for HSS wedneday january 10 .State changed from pending to approved"""
    text = 'Workflow state changed for %s booking for %s %s. State changed from %s to %s.' %(booking.activity.title, booking.visiting_group_name,  getFormatedDate(booking.booking_day.date),  workflow_map[booking.booking_state], workflow_map[int(state)])
    
    remember_booking_change(booking_id=booking.id,  change_op=12,  change_text=text,  changed_by=changed_by)


def remember_visiting_group_properties_change(booking=None, visiting_group=None, changed_by=''):
    """how do we figure out the booking properties change and all bookings it will affect?"""

    text = 'Visiting group properties saved/changed for %s' % visiting_group.visiting_group_name

    remember_booking_change(booking_id=booking.id,  change_op=14,  change_text=text,  changed_by=changed_by)


class History(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    def fnCmpTimestamp(self,  a,  b):
        return cmp(b.key,  a.key)
        
        
    def getBookingHistory(self,  limit=25):
        map_fun = '''function(doc) {
        if (doc.type == 'booking_history') {
            emit(doc.timestamp, doc);
        }}'''
    
        booking_history = holly_couch.query(map_fun)
        all = [h for h in booking_history]
        all.sort(self.fnCmpTimestamp)
        return [a.value for a in all][:25]
        
    @expose('hollyrosa.templates.history_show')
    @validate(validators={'visiting_group_id':validators.Int(not_empty=False), 'user_id':validators.Int(not_empty=False)})
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view history'))
    def show(self, visiting_group_id=None, user_id=None):
        for_group_name = ''
        if visiting_group_id != None:
            history = DBSession.query(booking.BookingHistory).join(booking.Booking).join(booking.VisitingGroup).filter('visiting_group_id='+str(visiting_group_id)).order_by('timestamp desc')
            vgroup = DBSession.query(booking.VisitingGroup).filter('id='+str(visiting_group_id)).one() 
            for_group_name = vgroup.name
        elif user_id != None:

            history = DBSession.query(booking.BookingHistory).join(booking.Booking).filter('last_changed_by_id='+str(user_id)).order_by('timestamp desc').limit(500)
            
            for_group_name = 'for user ' + str(user_id)

        else:
            history = self.getBookingHistory(limit=25) #DBSession.query(booking.BookingHistory).order_by('timestamp desc').limit(25)
        return dict(history=history,  change_op_map=change_op_map, for_group_name=for_group_name)
        

    @expose('hollyrosa.templates.rss_20_history')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view history'))
    def rss(self):
        return dict(history = DBSession.query(booking.BookingHistory).all().limit(100),  change_op_map=change_op_map,  publishing_date=time.localtime(time.time()))
