# -*- coding: utf-8 -*-

"""Couch db"""

#...ME
import couchdb
from uuid import uuid4
import datetime


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
    if ((doc.type == 'visiting_group') && (doc.from_date <= '"""+ to_date+"""' ) && (doc.to_date >= '""" + from_date + """'))
        emit(doc.from_date, doc);
        }"""
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
    
    
    
