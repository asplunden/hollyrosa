# -*- coding: utf-8 -*-
"""
hollyrosa_tool.py 

Copyright 2010-2016 Martin Eliasson

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

import copy, datetime, logging, argparse
import couchdb
#from hollyrosa_tool import ds


    
parser = argparse.ArgumentParser()
parser.add_argument("--couch", help="url to couch db", default='http://localhost:5989')
parser.add_argument("--database", help="name of database in couch", default='hollyrosa_2015_prod')
parser.add_argument("--username", help="login username", default=None)
parser.add_argument("--password", help="login password", default=None)
parser.add_argument("-v", "--verbose", help="turn on verbose logging", action="store_true")
args = parser.parse_args()

#...init logging'
log = logging.getLogger("hollyrosa_view_tool")

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARN)
    
    
#...read from ini file
db_url = args.couch
db_name = args.database
db_username = args.username
db_password = args.password

couch_server = couchdb.Server(url=db_url)

if db_username != None:
    couch_server.resource.credentials = (db_username, db_password)

try:
    holly_couch = couch_server[db_name]
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create(db_name)
    
holly_couch_destination = couch_server['hollyrosa_2015_prod']

if False:
    #...transfering room schema from one database to another
    ds = holly_couch['room_schema.2013']
    new_ds = copy.deepcopy(ds)
    holly_couch_destination['room_schema.2013'] = new_ds
    
    schema = ds['schema']
    for k in schema.keys():
        print k
        
        rm = holly_couch[k]
        new_rm = copy.deepcopy(rm)
        print new_rm
        holly_couch_destination[k] = new_rm





    

def copyDocument(db, from_id, to_id):
    doc = db[from_id]
    new_doc = copy.deepcopy(doc)
    db[to_id] = new_doc
    
    
copyDocument(holly_couch, 'summer_schema.2014', 'summer_schema.2016')
copyDocument(holly_couch, 'school_schema.2014', 'school_schema.2016')
#copyDocument(holly_couch, 'arcanum_schema.2015', 'boomerang.2016')

if True:
    for b in holly_couch.view('booking_day/all_booking_days', include_docs=True):
        doc = holly_couch[b.doc['_id']]
        if doc['day_schema_id'] == 'summer_schema.2014':
            doc['day_schema_id'] = 'summer_schema.2016'
        if doc['day_schema_id'] == 'school_schema.2014':
            doc['day_schema_id'] = 'school_schema.2016'
        if doc['day_schema_id'] == 'arcanum_schema.2015':
            doc['day_schema_id'] = 'summer_schema.2016'
            
        holly_couch[b.doc['_id']] = doc

if False:
    for i in range(8):
        doc = holly_couch["activity.1"]
        new_doc = copy.deepcopy(doc)
        new_doc['activity_group_id'] = 'activity_group.20'
        new_doc['bg_color'] = '#efe'
        new_doc['zorder'] = 100+i
        
        
        
        holly_couch["activity.arcanum_%d" % (i+1)] = new_doc
        
    for i in range(8):
        doc = holly_couch["activity.1"]
        new_doc = copy.deepcopy(doc)
        new_doc['activity_group_id'] = 'activity_group.21'
        new_doc['bg_color'] = '#efe'
        new_doc['zorder'] = 110+i
        
        
        
        holly_couch["activity.arcanum_%d" % (i+1+8)] = new_doc
            

    
def makeSlotRow(slot_id_start, zorder, activity_id):
    result = list()
    result.append({u'zorder': zorder, u'id': activity_id})
    result.append({u'duration': u'03:00:00', u'time_to': u'12:00:00', u'slot_id': u'slot.%d' % slot_id_start, u'time_from': u'09:00:00', u'title': u'FM'})
    slot_id_start += 1 
    result.append({u'duration': u'03:30:00', u'time_to': u'17:00:00', u'slot_id': u'slot.%d' % slot_id_start, u'time_from': u'13:30:00', u'title': u'EM'})
    slot_id_start += 1 
    result.append({u'duration': u'02:00:00', u'time_to': u'21:00:00', u'slot_id': u'slot.%d' % slot_id_start, u'time_from': u'19:00:00', u'title': u'Kväll'})
    slot_id_start += 1 
    result.append({u'duration': u'03:00:00', u'time_to': u'23:59:00', u'slot_id': u'slot.%d' % slot_id_start, u'time_from': u'21:00:00', u'title': u'After hours'})
    slot_id_start += 1 
    return result, slot_id_start


if False:
    doc = holly_couch['arcanum_schema.2015']
    schema = doc['schema']
    print schema
    
    #...find max slot id
    max_slot_id = 0
    for k, v in schema.items():
        #...v is a list of slots
        for tmp_slot in v[1:]:
            print tmp_slot
            tmp_slot_id_num = int(tmp_slot['slot_id'].replace('slot.',''))
            max_slot_id = max(max_slot_id, tmp_slot_id_num)
            
    print 'max_slot_id', max_slot_id
    #copy last slot row inserting more slot rows
    max_slot_id += 1
    
    #...add the first 8 activities
    for i in range(8):
        tmp_activity_id = "activity.arcanum_%d" % (i+20+1)
        print max_slot_id
        tmp_slot_row, max_slot_id = makeSlotRow(max_slot_id, 100+i, tmp_activity_id)
        schema[tmp_activity_id] = tmp_slot_row
        
#    for i in range(12):
#        tmp_activity_id = "activity.arcanum_%d" % (i+1+8+8+12)
#        tmp_slot_row, max_slot_id = makeSlotRow(max_slot_id, 110+i, tmp_activity_id)
#        schema[tmp_activity_id] = tmp_slot_row
        
        
    holly_couch['arcanum_schema.2015'] = doc
    
    
    
