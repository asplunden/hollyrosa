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
from hollyrosa.model.booking_couch import getAllHistory,  getAllHistoryForVisitingGroup,  getAllHistoryForUser,  genUID
from hollyrosa.model import holly_couch
from sqlalchemy import and_
import datetime,  types
from hollyrosa.controllers.common import workflow_map,  getFormatedDate,  getLoggedInDisplayName,  change_op_map,  change_op_lookup,  has_level
from hollyrosa.controllers.common_couch import getCouchDBDocument

__all__ = ['History']





def remember_booking_change(holly_couch, booking_id=None,  booking_day_id=None,  visiting_group_id=None, note_id=None, change_op=None,  change_text='',  changed_by='',  booking_content=''):
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
    
    bh = dict(type='booking_history') 
    
    if type(change_op) ==types.StringType:
        change_op = change_op_lookup[change_op]
    bh['change_op'] = change_op
    bh['booking_content']=booking_content
    bh['change'] = change_text
    bh['changed_by'] = getLoggedInDisplayName(request) 
    bh['timestamp'] = str(datetime.datetime.now())
    bh['booking_id'] = booking_id
    bh['booking_day_id'] = booking_day_id

    if visiting_group_id != None:

        bh['visiting_group_id'] = visiting_group_id
    if note_id != None:
        bh['note_id'] = note_id
        
    holly_couch[genUID(type='booking_history')] = bh

    
def remember_schedule_booking(holly_couch, booking=None, slot_row_position=None, booking_day=None,  changed_by='',  activity=None):
    """Trapper booking for HSS scheduled wedneday january 10 19:10 to 21:15"""
    #activity = holly_couch[booking['activity_id']] # TODO: wastefull lookup
    text = '%s booking for %s scheduled %s between %s and %s' %(activity['title'], booking['visiting_group_name'],  booking_day['date'],  slot_row_position['time_from'], slot_row_position['time_to'])
    
    remember_booking_change(holly_couch, booking_id=booking.id, visiting_group_id=booking['visiting_group_id'], change_op=1,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day.id)


def remember_unschedule_booking(holly_couch, booking=None, slot_row_position=None, booking_day=None,  changed_by='',  activity=None):
    """Trapper booking for HSS scheduled wedneday january 10 19:10 to 21:15"""
    if booking['slot_id'] == '':
        text = '%s booking for %s unscheduled. Was scheduled for %s between %s and %s' %(activity['title'], booking['visiting_group_name'],  booking_day['date'],  slot_row_position['time_from'],  slot_row_position['time_to'])
    else:
        text = 'WARN: no slot_row_position for unscheduled booking. Cannot determine the time of unscheduling or activity but group was %s and bookingdate %s.' %(booking['visiting_group_name'],  booking_day['date'])
    remember_booking_change(holly_couch, booking_id=booking['_id'], visiting_group_id=booking['visiting_group_id'], change_op=2,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day['_id'])


def remember_book_slot(holly_couch, booking_id='',  slot_row_position=None, booking=None, booking_day=None,  changed_by='',  activity_title=''):
    """Trapper booked for HSS wedneday january 10 19:10 to 21:15"""
    text = '%s slot booked for %s %s between %s and %s' %(activity_title, booking['visiting_group_name'],  booking_day['date'], slot_row_position['time_from'],  slot_row_position['time_to'])
    
    remember_booking_change(holly_couch, booking_id=booking_id, visiting_group_id=booking['visiting_group_id'],    change_op=3, change_text=text, changed_by=changed_by, booking_day_id=booking_day['_id'])
    
    
def remember_booking_properties_change(holly_couch, booking=None, slot_row_position=None, booking_day=None,  old_visiting_group_name='',  new_visiting_group_name='', new_content='', changed_by='',  activity_title=''):
    """Trapper booked for HSS wedneday january 10 19:10 to 21:15"""
    text = '%s booking for %s properties changed to %s, slot on %s between %s and %s' %(activity_title, old_visiting_group_name,  new_visiting_group_name,  booking_day['date'],  slot_row_position['time_from'],  slot_row_position['time_to'])
    
    remember_booking_change(holly_couch, booking_id=booking['_id'],  change_op=7,  change_text=text,  changed_by=changed_by, booking_day_id=booking_day['_id'])
    
    
def remember_booking_vgroup_properties_change(holly_couch, booking=None, visiting_group_name='', visiting_group_id='',  changed_by='',  activity_title=''):
    """Booking visiting group property change for HSS wedneday january 10 19:10 to 21:15"""
    booking_day_id=''
    if booking['booking_day_id'] != '' and booking['booking_day_id'] != None:
        booking_day_id = booking['booking_day_id']
        text = '%s visiting group properties changed for %s on %s' %(visiting_group_name,  activity_title, holly_couch[booking_day_id]['date'] )
    else:
        text = '%s visiting group properties changed for %s' %(visiting_group_name,  activity_title )
    remember_booking_change(holly_couch, booking_id=booking['_id'],  change_op=7,  change_text=text,  changed_by=changed_by, booking_day_id=booking_day_id,  visiting_group_id=visiting_group_id)
    

def remember_new_booking_request(holly_couch, booking=None, changed_by=''):
    """Trapper requested for HSS wedneday january 10 to friday januari 12"""
    activity = holly_couch[booking['activity_id']] # TODO: wastefull lookup
    text = '%s requested for %s %s to %s' %(activity['title'], booking['visiting_group_name'],  booking.get('valid_from',''),  booking.get('valid_to',''))
    
    remember_booking_change(holly_couch, booking_id=booking['_id'], visiting_group_id=booking['visiting_group_id'],  change_op=4,  change_text=text,  changed_by=changed_by)
    
    
def remember_delete_booking_request(holly_couch, booking=None, changed_by='',  activity_title=''):
    """deleted Trapper requested for HSS wedneday january 10 to friday januari 12"""
    text = 'deleted %s requested for %s %s to %s' %(activity_title, booking['visiting_group_name'], booking.get('valid_from',''), booking.get('valid_to',''))
    remember_booking_change(holly_couch, booking_id=booking.id, visiting_group_id=booking['visiting_group_id'],  change_op=6,  change_text=text,  changed_by=changed_by)
    

def remember_booking_request_change(holly_couch, old_booking=None, new_booking=None, changed_by=''):
    """Change Trapper requested for HSS wedneday january 10 to friday januari 12 . Changed to """
    text = 'Change %s requested for %s %s to %s. Changed to %s requested for %s %s to %s.' %(old_booking.activity['title'], old_booking.visiting_group_name,  old_booking.valid_from,  old_booking.valid_to,  new_booking['activity_id'], new_booking['visiting_group_name'],  new_booking['valid_from'],  new_booking['valid_to'])
    
    remember_booking_change(holly_couch, booking_id=old_booking.id, visiting_group_id=old_booking.visiting_group_id,  change_op=5,  change_text=text,  changed_by=changed_by)
    
    
def remember_booking_move(holly_couch, booking=None, old_activity_title=None, new_activity_title=None,  changed_by='',  booking_day=None):
    """Change Trapper requested for HSS wedneday january 10 to friday januari 12 . Changed to """
    text = 'Move from %s to %s requested for %s at %s .' %(old_activity_title, new_activity_title, booking['visiting_group_name'],  booking_day['date'])
    
    remember_booking_change(holly_couch, booking_id=booking['_id'], visiting_group_id=booking['visiting_group_id'],  change_op=5,  change_text=text,  changed_by=changed_by,  booking_day_id=booking['booking_day_id'])
    
    
def remember_block_slot(holly_couch, slot_row_position=None, booking_day=None,  level=0,  changed_by='',  activity_title=''):
    """Ekohuset slot blocked on level 4 wedneday january 10 between 09:00 and 12:00"""
    text = '%s slot blocked on level %d %s between %s and %s' %(activity_title, level,  booking_day['date'],  slot_row_position['time_from'],  slot_row_position['time_to'])
    
    remember_booking_change(holly_couch, booking_id=None,  change_op=9,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day['_id'])
    
    
def remember_unblock_slot(holly_couch, slot_row_position=None, booking_day=None,  level=0,  changed_by='',  activity_title=''):
    """Ekohuset slot unblocked from level 4 wedneday january 10 between 09:00 and 12:00"""
    text = '%s slot unblocked from level %d %s between %s and %s' %(activity_title, level,  booking_day['date'],  slot_row_position['time_from'],  slot_row_position['time_to'])
    
    remember_booking_change(holly_couch, booking_id=None,  change_op=11,  change_text=text,  changed_by=changed_by, booking_day_id=booking_day.id)
    
    
def remember_workflow_state_change(holly_couch, booking=None, state=None, changed_by='',  activity_title='',  booking_day_date=''):
    """Workflow state changed for Trapper booking for HSS wedneday january 10 .State changed from pending to approved"""
    text = 'Workflow state changed for %s booking for %s %s. State changed from %s to %s.' %(activity_title, booking['visiting_group_name'],  booking_day_date,  workflow_map[booking['booking_state']], workflow_map[int(state)])
    
    remember_booking_change(holly_couch, booking_id=booking['_id'], visiting_group_id=booking['visiting_group_id'],  change_op=12,  change_text=text,  changed_by=changed_by)


def remember_tag_change(holly_couch, booking_id=None, old_tags='', new_tags='', changed_by='', visiting_group_id='', visiting_group_name=''):
    text = 'Tags changed for visiting group %s from %s to %s.' %(visiting_group_name, old_tags, new_tags)
    
    remember_booking_change(holly_couch, visiting_group_id=visiting_group_id,  change_op=13,  change_text=text,  changed_by=changed_by)


def remember_note_change(holly_couch, target_id='', note_id='', changed_by='', note_change='changed'):
    text = 'Note %s for target_id=%s, note_id=%s' %(note_change, target_id, note_id)
    visiting_group_id = ''
    visiting_group_name = ''
    #...check if target is a visiting_group and if so get name of visiting group
    if 'visiting_group' in target_id:
        visiting_group_id = target_id
        vgroup = holly_couch[visiting_group_id]
        visiting_group_name = vgroup['name']
        
        text = 'Note %s for visiting group %s, note_id=%s' %(note_change, visiting_group_name, note_id)
         
            
    remember_booking_change(holly_couch, visiting_group_id=visiting_group_id,  change_op=14,  change_text=text,  changed_by=changed_by)



def remember_visiting_group_properties_change(holly_couch, booking=None, visiting_group=None, changed_by=''):
    """how do we figure out the booking properties change and all bookings it will affect?"""

    text = 'Visiting group properties saved/changed for %s' % visiting_group.visiting_group_name

    remember_booking_change(holly_couch, booking_id=booking.id, visiting_group_id=visiting_group.id,  change_op=14,  change_text=text,  changed_by=changed_by)


def remember_ignore_booking_warning(holly_couch, booking=None, slot_row_position=None, booking_day=None,  changed_by='',  activity=None):
    """Trapper booking for HSS scheduled wedneday january 10 19:10 to 21:15"""
    text = 'Ignoring warning for %s booking for %s scheduled %s between %s and %s' %(activity['title'], booking['visiting_group_name'],  booking_day['date'],  slot_row_position['time_from'], slot_row_position['time_to'])
    
    remember_booking_change(holly_couch, booking_id=booking.id, visiting_group_id=booking['visiting_group_id'], change_op=1,  change_text=text,  changed_by=changed_by,  booking_day_id=booking_day.id)


class History(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    def fnCmpTimestamp(self,  a,  b):
        return cmp(b.key,  a.key)
        
        
    def getBookingHistory(self, holly_couch, limit=30):
        booking_history = getAllHistory(holly_couch, limit=limit)
        all = [h.doc for h in booking_history]
        return all
        
        
    def getBookingHistoryForVisitingGroup(self, holly_couch, visiting_group_id,  limit=1000):
        booking_history = getAllHistoryForVisitingGroup(holly_couch, visiting_group_id,  limit=limit)
        all = [h.doc for h in booking_history]
        return all
        
    def getBookingHistoryForUser(self, holly_couch, user_id, limit=250):
        booking_history = getAllHistoryForUser(holly_couch, user_id,  limit=limit)
        all = [h.doc for h in booking_history]
        return all
        
        
    @expose('hollyrosa.templates.history_show')
    @validate(validators={'visiting_group_id':validators.UnicodeString(not_empty=False), 'user_id':validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view history'))
    def show(self, visiting_group_id='', user_id=''):
        for_group_name = ''
        if visiting_group_id != '':
            history = self.getBookingHistoryForVisitingGroup(holly_couch, visiting_group_id)
            vgroup = holly_couch[visiting_group_id]
            for_group_name = vgroup['name']
        elif user_id != '':
            user_o = getCouchDBDocument(holly_couch, user_id, doc_type='user') #, doc_subtype=None)
            history = self.getBookingHistoryForUser(holly_couch, user_o['display_name'])
            
            for_group_name = 'for user ' + user_o['display_name']

        else:
            history = self.getBookingHistory(holly_couch, limit=250) 
        return dict(history=history,  change_op_map=change_op_map, for_group_name=for_group_name)
        

    @expose('hollyrosa.templates.rss_20_history')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('view'), msg='Only staff members and viewers may view history'))
    def rss(self):
        return dict(history = DBSession.query(booking.BookingHistory).all().limit(100),  change_op_map=change_op_map,  publishing_date=time.localtime(time.time()))


    
