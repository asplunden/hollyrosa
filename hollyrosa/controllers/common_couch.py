# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012, 2013, 2014 Martin Eliasson

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

import types


def getCouchDBDocument(holly_couch, id, doc_type=None, doc_subtype=None):
    """retrieve a document from couch db and do some sanity checkin on id, type and subtype of document"""
    if ((type(id) != types.StringType) and (type(id) != types.UnicodeType)):
        raise ValueError,  "the type of the document id must be string or unicode, but the given type was %s" % type(id) 
        
    l_doc = holly_couch[id]
    
    if None != doc_type:
        if not l_doc.has_key('type'):
            raise KeyError, "Document found in holly_couch but it lacks the require type field. Doc id: %s" % id
        if l_doc['type'] != doc_type:
            raise KeyError,  "Document found in holly_couch, but there is a document type missmatch for document with id %s, the supplied document type was %s but in document it is %s" % (id, doc_type,  l_doc['type'])

    if None != doc_subtype:
        if l_doc['subtype'] != doc_subtype:
            raise KeyError,  "Document found in holly_couch, but there is a document subtype missmatch for document with id %s, the supplied document type was %s but in document it is %s" % (id, doc_subtype,  l_doc['subtype'])

    return l_doc
    
    
def checkDocumentIdPrefix(id,  prefix):
    pass
    
    
def getBookingDay(holly_couch, booking_day_id):
    #return holly_couch[booking_day_id] 
    return getCouchDBDocument(holly_couch,  booking_day_id,  doc_type='booking_day')


def getBooking(holly_couch, booking_id):
    #return holly_couch[id]
    return getCouchDBDocument(holly_couch,  booking_id,  doc_type='booking')


def getProgramBooking(holly_couch, booking_id):
    #return holly_couch[id]
    return getCouchDBDocument(holly_couch,  booking_id,  doc_type='booking',  doc_subtype='program')


def getBedBooking(holly_couch, booking_id):
    #return holly_couch[id]
    return getCouchDBDocument(holly_couch,  booking_id,  doc_type='booking', doc_subtype='bed')


def getActivity(holly_couch,  activity_id):
    return getCouchDBDocument(holly_couch,  activity_id,  doc_type='activity')


def getActivityGroup(holly_couch,  activity_group_id):
    return getCouchDBDocument(holly_couch,  activity_group_id,  doc_type='booking',  doc_subtype='bed')


def getDaySchema(holly_couch,  day_schema_id):
    return getCouchDBDocument(holly_couch,  day_schema_id,  doc_type='day_schema')


def getProgramDaySchema(holly_couch,  day_schema_id):
    return getCouchDBDocument(holly_couch,  day_schema_id,  doc_type='day_schema',  doc_subtype='program_schema')


def getBedDaySchema(holly_couch,  day_schema_id):
    return getCouchDBDocument(holly_couch,  day_schema_id,  doc_type='day_schema',  doc_subtype='bed_schema')



def getVisitingGroup(holly_couch,  visiting_group_id):
    return getCouchDBDocument(holly_couch,  visiting_group_id,  doc_type='visiting_group')


def getSlot(holly_couch,  slot_id):
    return getCouchDBDocument(holly_couch,  slot_id,  doc_type='slot')
    

def getSlotState(holly_couch,  slot_state_id):
    return getCouchDBDocument(holly_couch,  slot_state_id,  doc_type='slot_state')
   
   
def getNote(holly_couch,  note_id):
    return getCouchDBDocument(holly_couch,  note_id,  doc_type='note')
    
    
def getAttachment(holly_couch,  attachment_id):
    return getCouchDBDocument(holly_couch,  attachment_id,  doc_type='attachment')
    
def getLayerText(holly_couch,  layer_text_id):
    return getCouchDBDocument(holly_couch,  layer_text_id,  doc_type='program_layer_text',  doc_subtype='layer_text')


def createEmptyProgramBooking(valid_from='',  valid_to='',  requested_date='',  subtype='program'):
    return dict(type='booking', subtype=subtype,  valid_from=valid_from,  valid_to=valid_to,  requested_date=requested_date, booking_day_id="", slot_id="")
    
    
def makeHouseBooking():
    pass

def makeVODBGroup():
    pass

def makeStaffVODBGroup():
    pass


def makeCourseVODBGroup():
    pass

def makeVisitingVODBGroup():
    pass
    
