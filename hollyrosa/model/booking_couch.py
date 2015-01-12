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

""" 

from uuid import uuid4
import datetime
from hollyrosa.controllers.common import DataContainer
    


# TODO: make type mandatory
def genUID(type='', user_id='', hostname=''):
    """
    returns a globaly unique id for holly rosa database (couchdb)

    user_id and hostname allows one to optionally see in th id
    on which system the id was generated and that helps
    ensuring globally unique ids (not very hopefully
    unique ids).    
    """
    tmp = type + '.'
    if hostname != '':
        tmp += hostname + '.'
    if user_id != '':
        tmp += user_id + '.'
    tmp += uuid4().hex
    return tmp
    

def getBookingsOfVisitingGroup(holly_couch, visiting_group_id,  visiting_group_name):
    args = [visiting_group_id,  visiting_group_name]
    return holly_couch.view('visiting_groups/bookings_of_visiting_group',  keys=[k for k in args if k != None],  include_docs=True)
    
 
    
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
                
                


def getBookingDayOfDate(holly_couch, date):
    return list(holly_couch.view('booking_day/all_booking_days',  keys=[date],  include_docs=True))[0].doc
    
    
def getBookingDayOfDateList(holly_couch, dates):
    return list(holly_couch.view('booking_day/all_booking_days',  keys=dates,  include_docs=True))
    
    
def getAllBookingDays(holly_couch):
    return holly_couch.view('booking_day/all_booking_days',  include_docs=True)
    

def getBookingDays(holly_couch, from_date='2011-01-01',  to_date='2015-12-11'):
    """Helper function to get booking days from CouchDB"""
    return holly_couch.view('booking_day/all_booking_days',  startkey=from_date,  endkey=to_date,  include_docs=True)

        
def getVisitingGroupsAtDate(holly_couch, at_date):
    #...argh TODO: fix that now we have to use doc instead of value
    formated_date = datetime.datetime.strptime(at_date,'%Y-%m-%d').strftime('%a %b %d %Y')
    return holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=[formated_date],  include_docs =True)
    	

def dateRange(from_date, to_date, format='%a %b %d %Y'):
    one_day = datetime.timedelta(1)
    formated_dates = list()
    tmp_date = datetime.datetime.strptime(from_date,'%Y-%m-%d')
    tmp_to_date = datetime.datetime.strptime(to_date,'%Y-%m-%d')
    while tmp_date <= tmp_to_date:
        formated_dates.append(tmp_date.strftime(format))
        tmp_date = tmp_date + one_day
    return formated_dates
    

def dateRange2(from_date, count, format='%Y-%m-%d'):
    one_day = datetime.timedelta(1)
    formated_dates = list()
    tmp_date = datetime.datetime.strptime(from_date,'%Y-%m-%d')
    for i in range(count):
        formated_dates.append(tmp_date.strftime(format))
        tmp_date = tmp_date + one_day
    return formated_dates
    
def getVisitingGroupsInDatePeriod(holly_couch, from_date,  to_date,  subtype='program'):
    """create one key for each day"""
    
    formated_dates = dateRange(from_date, to_date)
    
    # TODO: maybe one can make a view using reduce that fixes this multiple-removing stuff.
    #return holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=formated_dates)
    
    check = dict()
    r = list()
    for v in holly_couch.view("visiting_groups/all_visiting_groups_by_date",  keys=formated_dates,  include_docs=True):
        if not check.has_key(v.doc['_id']):
            if v.doc.get('subtype', 'program') == 'program':
                r.append(v)
        check[v.doc['_id']] = 1 
    return r
    
    
def getVisitingGroupsByBoknstatus(holly_couch, status):
    return holly_couch.view("visiting_groups/all_visiting_groups_by_boknstatus",  startkey=[status,  None],  endkey=[status,  '9999-99-99'],  include_docs =True) # keys=[[s, None]  for s in statuses],  

 
def getVisitingGroupByBoknr(holly_couch, boknr):
    return list( holly_couch.view("visiting_groups/visiting_group_by_boknr", keys=[boknr], include_docs =True) )
    

def getVisitingGroupsByVodbState(holly_couch, state):
    return holly_couch.view("visiting_groups/all_visiting_groups_by_vodb_state",  startkey=[state,  None],  endkey=[state,  '9999-99-99'],  include_docs =True)  


def getVisitingGroupsByGroupType(holly_couch,  group_type):
    return holly_couch.view("visiting_groups/all_visiting_groups_by_group_type",  startkey=[group_type,  None],  endkey=[group_type,  '9999-99-99'],  include_docs =True)  
    
    
def getVisitingGroupOfVisitingGroupName(holly_couch, name):
    return holly_couch.view('visiting_groups/visiting_group_by_name', keys=[name], include_docs=True)
    
    
def getAllVisitingGroupsNameAmongBookings(holly_couch, from_date='',  to_date='9999-99-99'):
    """find all bookings in date range and look for the visiting_group_names.
        perhaps this can be done with reduce in the future."""
        
    # TODO: hmm. a view shold be possible somehow. We still need to iterate, but in a different way (more efficient)
    
#    if from_date == '':
#        map_fun = '''function(doc) {
#        if (doc.type == 'booking')
#            emit(doc._id, doc.visiting_group_name);
#            }'''
#    else:
#        #...this is harder NEED TO LOOK AT BOOKING DAY ID; THEN BOOKING DAY AND THEN DATE. TRICKY
#        map_fun = """function(doc) {
#        if (doc.type == 'booking') {
#                emit(doc._id, doc.visiting_group_name);
#            }}"""
#    #...add map fun for from_date and to_date
        
#    visiting_groups_names = holly_couch.query(map_fun)
    visiting_groups_names = holly_couch.view('visiting_groups/all_names_among_bookings', reduce=True, group=True)
    
    #...conversion 
    visiting_group_names_result = dict()
    for vgn in visiting_groups_names:
        print vgn
        visiting_group_names_result[vgn.key[1]] = 1
        
        
    #print  visiting_group_names_result.values()
    return visiting_group_names_result.keys()
    
    
def getSlotAndActivityIdOfBooking(holly_couch, booking,  subtype):
    booking_day_id = booking['booking_day_id']
    booking_day_o = holly_couch[booking_day_id]
    
    if subtype=='program':
        schema_o = holly_couch[booking_day_o['day_schema_id']]
    elif subtype == 'live':
        schema_o = holly_couch[ booking_day_o['room_schema_id']]
    #schema_o = holly_couch[booking_day_o['day_schema_id']]
    slot_id = booking['slot_id']
    
    #...iterate thrue the schema
    for tmp_activity_id,  tmp_activity_row in schema_o['schema'].items():
        for tmp_slot in tmp_activity_row[1:]:
            if tmp_slot['slot_id'] == slot_id:
                return (tmp_activity_id,  tmp_slot)
    return (None,  None)

#
# HISTORY
#

def getAllHistory(holly_couch, limit=None):
    """returns booking history sorted in reverse chronological order."""
    return holly_couch.view('history/all_history',  descending=True,  include_docs=True, limit=limit)
    
def getAllHistoryForVisitingGroup(holly_couch, visiting_group_id,  limit=None):
    """returns booking history sorted in reverse chronological order."""
    # TODO: does not work, may need to look up all bookings first.
    return holly_couch.view('history/all_history_by_visiting_group', startkey=[visiting_group_id,'zzzzzzzzzzzzzzzzzzzzzzzzzzzzz'], endkey=[visiting_group_id,None], include_docs=True, descending=True, limit=limit)
    
def getAllHistoryForUser(holly_couch, user_id,  limit=None):
    """returns booking history sorted in reverse chronological order."""
    return holly_couch.view('history/history_by_username',  keys=[user_id], include_docs=True, descending=True,  limit=limit)
    
def getAllHistoryForBookings(holly_couch, booking_ids,  limit=250):
    """returns booking history sorted in reverse chronological order."""
    return holly_couch.view('history/history_by_booking_id',  keys=booking_ids, include_docs=True, descending=True,  limit=limit)

    
#----

def getAllActivityGroups(holly_couch,  filter_activity_group_ids=None):
    tmp_result = holly_couch.view('all_activities/all_activity_groups')
    if filter_activity_group_ids == None:
        return tmp_result
    else:
        filtered_result = list()
        for tmp_r in tmp_result:
            if tmp_r.value['_id'] in filter_activity_group_ids:
                filtered_result.append(tmp_r)
        return filtered_result
    
    
def getActivityGroupNameAndIdList(holly_couch,  day_schema=None):
    """for displaying drop down in web page and similar"""
    filter_activity_group_ids = None
    if day_schema != None:
        filter_activity_group_ids = day_schema['activity_groups_ids']
        
    tmp_result = getAllActivityGroups(holly_couch,  filter_activity_group_ids)
    return [DataContainer(id=d.value['_id'],  title=d.value['title']) for d in tmp_result]


def getAllActivities(holly_couch):
    return holly_couch.view('all_activities/all_activities', include_docs=True)
    
#---

def getAllVisitingGroups(holly_couch):
    return holly_couch.view('visiting_groups/all_visiting_groups',  include_docs=True)


def getAgeGroupStatistics(holly_couch, group_level=999, startkey=None):
    if startkey == None:
        startkey = []
    return holly_couch.view('statistics/age_group_statistics', startkey=startkey, reduce=True, group_level=group_level)

def getActivityStatistics(holly_couch):
    return holly_couch.view('statistics/activity_statistics', reduce=True, group_level=999)    


def getTagStatistics(holly_couch, group_level=999, startkey=None):
    if startkey == None:
        startkey = []
    return holly_couch.view('tag_statistics/tag_group_statistics', startkey=startkey, reduce=True, group_level=group_level)    

#--- 

def getAllScheduledBookings(holly_couch, limit=100):
    return holly_couch.view('workflow/all_scheduled_bookings',  include_docs=True,  limit=limit)

def getAllUnscheduledBookings(holly_couch, limit=100):
    return holly_couch.view('workflow/all_unscheduled_bookings',  include_docs=True,  limit=limit)
    
def gelAllBookingsWithBookingState(holly_couch, booking_states,  limit=200):
    return holly_couch.view('workflow/all_bookings_by_booking_state',  keys=booking_states,  include_docs=True,  limit=limit)

def getAllSimilarBookings(holly_couch, keys, limit=1000):
    return holly_couch.view('workflow/all_similar_bookings',  key=keys, include_docs=True,  limit=limit)

    
def getActivityTitleMap(holly_couch):
    m = dict()
    for a in holly_couch.view('all_activities/activity_titles'):
        m[a.key[0]] = a.key[1]
    return m
    
def getBookingDayInfoMap(holly_couch):
    m = dict()
    for a in holly_couch.view('workflow/booking_day_map_info'):
        m[a.key] = a.value[0]
    return m
    
def getUserNameMap(holly_couch):
    m = dict()
    for a in holly_couch.view('workflow/user_name_map'):
        m[a.key] = a.value
    return m

# TODO: VERY DNGEROUS TO CACHE
def getSchemaSlotActivityMap(holly_couch, booking_day,  subtype):
    if subtype == 'program':
        day_schema_id = booking_day['day_schema_id']
    else:
        day_schema_id = booking_day['room_schema_id']
    try:
        tmp = _schema_slot_activity_map
        print 'found'
    except NameError:
        res = holly_couch.view('day_schema/slot_map')
        m = dict()
    
        for a in res:
            v = a.value
        
            m[a.key[0]] = dict(activity_id=v[0],  duration=v[1]['duration'],  time_to=v[1]['time_to'],  slot_id=v[1]['slot_id'],  time_from=v[1]['time_from'],  title=v[1]['title'], pref=v[1].get('pref','time'))
        # TODO: stor cache and cache chack in holly_couch db wrapper when it is ready        
        tmp = m
        _schema_slot_activity_map = m
    
    return tmp
    
    
    
    
    

def getSlotRowSchemaOfActivity(holly_couch,  day_schema_id,  activity_id):
    return holly_couch.view('day_schema/slot_schema_of_activity',  key=[day_schema_id,  activity_id],  include_docs=True)
    
    
def getAllSchemas(holly_couch):
    return holly_couch.view('day_schema/day_schema',  include_docs=True)
    
    
    
def getNotesForTarget(holly_couch, target_id):
    return holly_couch.view("notes/notes_by_target_datesorted", include_docs=True, startkey=[target_id, None], endkey=[target_id, "9999-99-99 99:99"])

def getBookingInfoNotesOfUsedActivities(holly_couch, keys):
    return holly_couch.view("notes/notes_for_list_bookings", include_docs=True, keys=keys)


def getTargetNumberOfNotesMap(holly_couch):
    """It also includes number of attachments"""
    number_of_notes = holly_couch.view("notes/number_of_notes_per_target", reduce=True, group=True)
    the_map = dict()
    for x in number_of_notes:
        the_map[x.key] = x.value
    
    return the_map
    
#------ tags
def getDocumentsByTag(holly_couch, tag):
    return holly_couch.view("tags/documents_by_tag", include_docs=True, keys=[tag]) #startkey=[target_id, None], endkey=[target_id, "9999-99-99 99:99"])

def getAllTags(holly_couch):
    return holly_couch.view("tags/all_tags", reduce=True, group=True)
    
    
#------

def getAllUsers(holly_couch):
    return holly_couch.view('user/all_users', include_docs=True)
    
def getAllUtelunchBookings(holly_couch):
    return holly_couch.view('user/utelunch', include_docs=True)
  
#------ VODB

def getBookingOverview(holly_couch, from_date, to_date, group_level=9999, reduce=True):
    if reduce:
        return holly_couch.view('vodb_overview/vodb_overview', reduce=reduce, group_level=group_level)
    else:
        return holly_couch.view('vodb_overview/vodb_overview', reduce=reduce, include_docs=False) # dont include docs, it gets really slow


def getBookingEatOverview(holly_couch, from_date, to_date, group_level=9999, reduce=True):
    if reduce:
        return holly_couch.view('vodb_overview/vodb_eat_overview', reduce=reduce, group_level=group_level)
    else:
        return holly_couch.view('vodb_overview/vodb_eat_overview', reduce=reduce, include_docs=False) # dont include docs, it gets really slow



def getRoomBookingsOfVODBGroup(holly_couch,  visiting_group_id):
    return [b.doc for b in holly_couch.view('visiting_groups/live_bookings_of_visiting_group',  include_docs=True,  startkey=[visiting_group_id, ''],  endkey=[visiting_group_id, 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'])]


def getAllProgramLayerBucketTexts(holly_couch,  visiting_group_id):
    return holly_couch.view('program_layer/all_bucket_texts', include_docs=True,  keys=[visiting_group_id])
    
def getProgramLayerBucketTextByDayAndTime(holly_couch,  visiting_group_id,  booking_day_id,  bucket_time):
    return holly_couch.view('program_layer/bucket_text_by_day_and_time', include_docs=True,  keys=[(visiting_group_id,  booking_day_id,  bucket_time)])
