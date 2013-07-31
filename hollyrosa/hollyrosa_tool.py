# -*- coding: utf-8 -*-
"""
hollyrosa_tool.py

Copyright 2010, 2011, 2012, 2013 Martin Eliasson

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

import copy,  datetime
import couchdb


def dateRange(from_date, to_date, format='%a %b %d %Y'):
    one_day = datetime.timedelta(1)
    formated_dates = list()
    tmp_date = datetime.datetime.strptime(from_date,'%Y-%m-%d')
    tmp_to_date = datetime.datetime.strptime(to_date,'%Y-%m-%d')
    while tmp_date <= tmp_to_date:
        formated_dates.append(tmp_date.strftime(format))
        tmp_date = tmp_date + one_day
    return formated_dates
    
    
#...read from ini file
db_url = 'http://localhost:5989'
db_name = 'hollyrosa_2013_test'

couch_server = couchdb.Server(url=db_url)
try:
    holly_couch = couch_server[db_name]
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create(db_name)
    
    

if False:
    for b in holly_couch.view('all_activities/erasure', include_docs=True):
        doc = b.doc
        dtype = doc['type']
        print 'delete', doc
        holly_couch.delete(b.doc)
    
if False:
    for b in holly_couch.view('all_activities/scan_all', include_docs=True):
        b.doc['do_not_delete'] = True
        holly_couch[b.doc['_id']] = b.doc
        
if False:
    #...try to generate all booking days. Ah, first generate day schema!
    ds = holly_couch['day_schema.2012']
    new_ds = copy.deepcopy(ds)
    holly_couch['summer_schema.2013'] = ds
    holly_couch['school_schema.2013'] = ds
    holly_couch['60dn_schema.2013'] = ds
    
if False:
    pos = 1300
    school_dates_spring = dateRange('2013-05-01', '2013-06-08', format='%Y-%m-%d')
    summer_dates = dateRange('2013-06-09', '2013-08-02', format='%Y-%m-%d')
    sixtydn_dates = dateRange('2013-08-03', '2013-08-18', format='%Y-%m-%d')
    school_dates_autumn = dateRange('2013-08-19', '2013-10-20', format='%Y-%m-%d')
    
    worklist = [(school_dates_spring,  'school_schema.2013'), (summer_dates, 'summer_schema.2013'), (sixtydn_dates, '60dn_schema.2013'), (school_dates_autumn, 'school_schema.2013')]
    
    for days, day_schema_id in worklist:
        for d in days:
            bd_c = dict(type='booking_day', date=d, note='', title='', num_program_crew_members=0, num_fladan_crew_members=0, day_schema_id=day_schema_id, zorder=pos,  room_schema_id='room_schema.2013' )
            holly_couch['booking_day.'+str(pos)] = bd_c
            pos += 1
            
            
#...We will have to list all activities and all activity_groups and then look for all booking_info_id. Save them all in a dict and after that we can delete note that are not in that dict
#...better mark the docs as eternal

# then for visiting groups we want to keep a few eternal too

#...a two step process really.

# never delete eternal documents


if True:
    design_view_names = ['all_activities', 'booking_day', 'day_schema','history', 'notes','statistics','tag_statistics','tags','user', 'visiting_groups', 'vodb_overview', 'workflow', 'booking_day_live' ]
    
    for tmp_name in design_view_names:
        tmp_dv = '_design/%s' % tmp_name
        dv_doc = holly_couch[tmp_dv]
        print dv_doc
        print dv_doc['views']
        
        file_name = 'design_views/%s.viewfunc' % tmp_name
        f = open(file_name, 'w')
        f.write(str(dv_doc))
        f.close()
        
if False:
    
    activities = list()
    agroups=dict()
    
    for tmp_day_schema in holly_couch.view('day_schema/day_schema',  include_docs=True):
        day_schema = tmp_day_schema.doc
        
        for k, v in day_schema['schema'].items():
            #print k
            #print v
            activities.append(k)
            tmp_activity = holly_couch[k]
            agid = tmp_activity['activity_group_id']
            #print 'agid',  agid
            tmp_agroup = holly_couch[agid]
            if not agroups.has_key(tmp_agroup.id):
                agroups[tmp_agroup.id] = tmp_agroup
                print 'added agroup', tmp_agroup
        print 'ALL AGS',  agroups
        print 
        all_keys = [k for k in agroups.keys()]
        print 
        day_schema2 = holly_couch[day_schema.id]
        day_schema2['activity_groups_ids'] = all_keys
        holly_couch[day_schema.id] = day_schema2
        
#        # given all activities, find all activity groups
#        activity_groups = dict()
#        
#        for tmp_ag in holly_couch.view('all_activities/all_activity_groups_and_activity',  include_docs=True,  keys=activities):
#            print tmp_ag
