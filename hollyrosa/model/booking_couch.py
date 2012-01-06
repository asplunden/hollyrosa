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



def get_visiting_group_names():
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
                
                
                
def getAllActivities():
    """Helper function to get all activities from CouchDB"""
    map_fun = '''function(doc) {
    if (doc.type == 'activity') {
        emit(doc._id, doc);
    }}'''
    
    activities = holly_couch.query(map_fun)
    return activities
    
    
def getAllActivityGroups():
    #try:
    #    tmp = _activity_groups
    #except AttributeError:
    map_fun = '''function(doc) {
    if (doc.type == 'activity_group')
        emit(doc._id, doc.title);
    }'''
    all_groups_c = holly_couch.query(map_fun)
    _activity_groups = [DataContainer(id=d.key,  title=d.value) for d in all_groups_c]
    
    tmp = _activity_groups
    return tmp
        

def cmpKeyReverse(a, b):
    return cmp(b.key,  a.key)
    
def getBookingHistory(booking_id):
    map_fun = """function(doc) {
    if (doc.type == 'booking_history') {
        if (doc.booking_id == '"""+booking_id+"""') {
            emit(doc.timestamp, doc);
    }}}"""
    
    history= [h for h in holly_couch.query(map_fun)]
    history.sort(cmpKeyReverse)
    return [h.value for h in history]

            
            
def getBookingDays(from_date='',  to_date='',  return_map=False):
    """Helper function to get booking days from CouchDB"""
    if from_date=='':
        map_fun = '''function(doc) {
        if (doc.type == 'booking_day')
            emit(doc.date, doc);
            }'''
    else:
        from_date='2011-08-10'
        
        if to_date=='':
            map_fun = """function(doc) {
            if ((doc.type == 'booking_day') && (doc.date >= '"""+ from_date+"""' ))
                emit(doc.date, doc);
                }"""
        else:
            to_date='2011-08-15'
            map_fun = """function(doc) {
            if ((doc.type == 'booking_day') && (doc.date >= '"""+ from_date+"""' ) && (doc.date <= '""" + to_date+"""'))
                emit(doc.date, doc);
                }"""
    booking_days_c = holly_couch.query(map_fun)
    
    #...conversion to booking  days so the template looks like old SQL Alchemy
    if not return_map:
        booking_days = []
        for bdc in booking_days_c:
            o = BookingDayC(bdc)
            booking_days.append(o)
        return booking_days
    else:
        booking_days = dict()
        for bdc in booking_days_c:
            o = BookingDayC(bdc)
            booking_days[o.id] = o
        return booking_days
    
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
    

def get_visiting_groups_at_date(at_date):
    map_fun = """function(doc) {
    if ((doc.type == 'visiting_group') && (doc.from_date <= '"""+ at_date+"""' ) && (doc.to_date >= '""" + at_date+"""'))
        emit(doc.from_date, doc);
        }"""
    visiting_groups_c = holly_couch.query(map_fun)
    
    #...conversion 
    visiting_groups = []
    for vgc in visiting_groups_c:
        visiting_groups.append(vgc.value)
    return visiting_groups
    

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
