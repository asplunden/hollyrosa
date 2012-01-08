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

#...ME
import couchdb
from uuid import uuid4
import datetime
from hollyrosa.controllers.common import DataContainer

def genUID():
    return uuid4().hex



def getBookingsOfVisitingGroup(visiting_group_id,  visiting_group_name):
    return holly_couch.view('visiting_groups/bookings_of_visiting_group',  keys=[visiting_group_id,  visiting_group_name],  include_docs=True)
    

    

def get_visiting_group_names():
    # TODO: switch over to using views
    """Helper function to get visiting groups from CouchDB"""
    map_fun = '''function(doc) {
    if (doc.type == 'visiting_group')
        emit(doc.from_date, doc.name);
        }'''
    visiting_groups_c = holly_couch.query(map_fun)
    
    #...conversion 
    visiting_group_names = []
    for vgn in visiting_groups_c:
        visiting_group_names.append(vgn.value)
    return visiting_group_names
    
    


    
# TODO: remove
class BookingDayC(object):
    """Assumes a lot when loading from Couch. Make an even better wrapper"""
    def __init__(self, m):
        for k, v in m.value.items():
            if k=='date':
                self.__dict__[k] = datetime.date.fromordinal(datetime.datetime.strptime(v, '%Y-%m-%d').toordinal())
            elif k == '_id':
                self.__dict__['id'] = v
            else:
                self.__dict__[k] = v
                
                


def getBookingDayOfDate(date):
    return list(holly_couch.view('booking_day/all_booking_days',  keys=[date],  include_docs=True))[0].doc
    
    
def getAllBookingDays():
    return holly_couch.view('booking_day/all_booking_days')
    

def getBookingDays(from_date='2011-01-01',  to_date='2011-12-11'):
    """Helper function to get booking days from CouchDB"""
    return holly_couch.view('booking_day/all_booking_days',  startkey=from_date,  endkey=to_date,  include_docs=True)

    
    
def get_visiting_groups_with_boknstatus(boknstatus):
    map_fun = """function(doc) {
    if ((doc.type == 'visiting_group') && (doc.boknstatus == '"""+ boknstatus+"""' ) )
        emit(doc.from_date, doc);
        }"""
    visiting_groups_c = holly_couch.query(map_fun)
    
    #...conversion 
    visiting_groups = []
    for vgc in visiting_groups_c:
        visiting_groups.append(vgc.value)
    return visiting_groups
    
    
    
def getVisitingGroupsAtDate(at_date):
    #...argh TODO: fix that now we have to use doc instead of value
    formated_date = datetime.datetime.strptime(at_date,'%Y-%m-%d').strftime('%a %b %d %Y')
    return holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=[formated_date],  include_docs =True)
    

def getVisitingGroupsInDatePeriod(from_date,  to_date):
    """create one key for each day"""
    
    one_day = datetime.timedelta(1)
    formated_dates = list()
    tmp_date = datetime.datetime.strptime(from_date,'%Y-%m-%d')
    tmp_to_date = datetime.datetime.strptime(to_date,'%Y-%m-%d')
    
    while tmp_date <= tmp_to_date:
        formated_dates.append(tmp_date.strftime('%a %b %d %Y'))
        tmp_date = tmp_date + one_day
    
    # TODO: maybe one can make a view using reduce that fixes this multiple-removing stuff.
    #return holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=formated_dates)
    
    r = dict()
    #print holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=formated_dates,  include_docs =True)
    for v in holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=formated_dates,  include_docs =True):
        print v
        r[v.doc['_id']] = v #DataContainer(key=v.key,  value=v.doc)
    return r.values()
    
    
    
def get_visiting_groups_in_date_period(from_date,  to_date):
    map_fun = """function(doc) {
    if (doc.type == 'visiting_group') {
        if ((doc.from_date <= '"""+ to_date+"""' ) && (doc.to_date >= '""" + from_date + """')) {
            emit(doc.from_date, doc);
        }}}"""
    
    visiting_groups_c = holly_couch.query(map_fun)
    
    #...conversion 
    visiting_groups = []
    for vgc in visiting_groups_c:
        visiting_groups.append(vgc.value)
    return visiting_groups
    
    
def get_visiting_groups(from_date='',  to_date=''):
    """Helper function to get visiting groups from CouchDB"""
    if from_date=='':
        map_fun = '''function(doc) {
        if (doc.type == 'visiting_group')
            emit(doc.from_date, doc);
            }'''
    else:
        
        
        if to_date=='':
            map_fun = """function(doc) {
            if ((doc.type == 'visiting_group') && (doc.from_date >= '"""+ from_date+"""' ))
                emit(doc.from_date, doc);
                }"""
        else:
        
            map_fun = """function(doc) {
            if ((doc.type == 'visiting_group') && (doc.from_date >= '"""+ from_date+"""' ) && (doc.to_date <= '""" + to_date+"""'))
                emit(doc.from_date, doc);
                }"""
    visiting_groups_c = holly_couch.query(map_fun)
    
    #...conversion 
    visiting_groups = []
    for vgc in visiting_groups_c:
        #o = BookingDayC(bdc)
        visiting_groups.append(vgc.value)
    return visiting_groups

couch_server = couchdb.Server(url='http://localhost:5989')
try:
    holly_couch = couch_server['hollyrosa1']
    print 'opened hollyrosa1'
    
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create('hollyrosa1')
    
def getAllVisitingGroupsNameAmongBookings(from_date='',  to_date=''):
    """find all bookings in date range and look for the visiting_group_names.
        perhaps this can be done with reduce in the future."""
        
    # TODO: hmm. a view shold be possible somehow. We still need to iterate, but in a different way (more efficient)
    
    if from_date == '':
        map_fun = '''function(doc) {
        if (doc.type == 'booking')
            emit(doc._id, doc.visiting_group_name);
            }'''
    else:
        #...this is harder NEED TO LOOK AT BOOKING DAY ID; THEN BOOKING DAY AND THEN DATE. TRICKY
        map_fun = """function(doc) {
        if (doc.type == 'booking') {
                emit(doc._id, doc.visiting_group_name);
            }}"""
    #...add map fun for from_date and to_date
        
    visiting_groups_names = holly_couch.query(map_fun)
    
    #...conversion 
    visiting_group_names_result = dict()
    for vgn in visiting_groups_names:
        visiting_group_names_result[vgn.key] = vgn.value
        
        
    #print  visiting_group_names_result.values()
    return visiting_group_names_result.values()
    
    
def getSlotAndActivityIdOfBooking(booking):
    booking_day_id = booking['booking_day_id']
    booking_day_o = holly_couch[booking_day_id]
    schema_o = holly_couch[booking_day_o['day_schema_id']]
    slot_id = booking['slot_id']
    
    #...iterate thrue the schema
    for tmp_activity_id,  tmp_activity_row in schema_o['schema'].items():
        for tmp_slot in tmp_activity_row[1:]:
            if tmp_slot['slot_id'] == slot_id:
                return (tmp_activity_id,  tmp_slot)
    return (None,  None)



def getAllHistory(limit=None):
    """returns booking history sorted in reverse chronological order."""
    return holly_couch.view('history/all_history',  descending=True,  limit=limit)
    
def getAllHistoryForVisitingGroup(visiting_group_id,  limit=None):
    """returns booking history sorted in reverse chronological order."""
    # TODO: does not work, may need to look up all bookings first.
    return holly_couch.view('history/all_history',  startkey= [{},  {},  visiting_group_id],  endkey=[None,  None,  visiting_group_id],  descending=True,  limit=limit)
    
def getAllHistoryForUser(user_id,  limit=None):
    """returns booking history sorted in reverse chronological order."""
    return holly_couch.view('history/history_by_username',  keys=[user_id],  descending=True,  limit=limit)
    
def getAllHistoryForBookings(booking_ids,  limit=250):
    """returns booking history sorted in reverse chronological order."""
    return holly_couch.view('history/history_by_booking_id',  keys=booking_ids,  descending=True,  limit=limit)

    
#----

def getAllActivityGroups():
    return holly_couch.view('all_activities/all_activity_groups')
    
def getAllActivities():
    return holly_couch.view('all_activities/all_activities')
    
#---

def getAllVisitingGroups():
    return holly_couch.view('visiting_groups/all_visiting_groups',  include_docs=True)
    
#--- 

def getAllScheduledBookings(limit=100):
    return holly_couch.view('workflow/all_scheduled_bookings',  include_docs=True,  limit=limit)

def getAllUnscheduledBookings(limit=100):
    return holly_couch.view('workflow/all_unscheduled_bookings',  include_docs=True,  limit=limit)
    
def gelAllBookingsWithBookingState(booking_states,  limit=200):
    return holly_couch.view('workflow/all_bookings_by_booking_state',  keys=booking_states,  include_docs=True,  limit=limit)
    
def getActivityTitleMap():
    m = dict()
    for a in holly_couch.view('all_activities/activity_titles'):
        m[a.key[0]] = a.key[1]
    return m
    
def getBookingDayInfoMap():
    m = dict()
    for a in holly_couch.view('workflow/booking_day_map_info'):
        m[a.key] = a.value[0]
    return m
    
def getUserNameMap():
    m = dict()
    for a in holly_couch.view('workflow/user_name_map'):
        m[a.key] = a.value
    return m
    
def getSchemaSlotActivityMap(day_schema_id):
    m = dict()
    res = holly_couch.view('day_schema/slot_map')
    
    for a in res:
        v = a.value
        
        m[a.key[0]] = dict(activity_id=v[0],  duration=v[1]['duration'],  time_to=v[1]['time_to'],  slot_id=v[1]['slot_id'],  time_from=v[1]['time_from'],  title=v[1]['title'])
    
    return m
