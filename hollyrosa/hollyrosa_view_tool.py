# -*- coding: utf-8 -*-
"""
hollyrosa_tool.py

Copyright 2010, 2011, 2012, 2013, 2014, 2015 Martin Eliasson

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

import couchdb,  json

    
#...read from ini file
db_url = 'http://localhost:5989'
db_name = 'hollyrosa_2015_prod'

couch_server = couchdb.Server(url=db_url)
couch_server.resource.credentials = ('username','password')
try:
    holly_couch = couch_server[db_name]
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create(db_name)
    
design_view_names = ['all_activities', 'booking_day', 'day_schema','history', 'notes','statistics','tag_statistics','tags','user', 'visiting_groups', 'vodb_overview', 'workflow', 'booking_day_live' , 'program_layer']
save_from = False
upload_to = True



if save_from:
    for tmp_name in design_view_names:
        tmp_dv = '_design/%s' % tmp_name
        print 'looking for ', tmp_dv
        dv_doc = holly_couch[tmp_dv]
        print dv_doc
        view_dict = dv_doc['views']
        file_name = 'design_views/%s.viewfunc' % tmp_name
        f = open(file_name, 'w')
        f.write(json.dumps(view_dict))
        f.close()
    

if upload_to:
    for tmp_name in design_view_names:
        tmp_dv = '_design/%s' % tmp_name
        print 'looking for ', tmp_dv
        
        try:
            dv_doc = holly_couch[tmp_dv]
        except couchdb.http.ResourceNotFound:
            dv_doc = dict(language='javascript')
            
        file_name = 'design_views/%s.viewfunc' % tmp_name
        f = open(file_name, 'r')
        views_txt = f.read()
        f.close()
        views_dict = json.loads(views_txt)
        dv_doc['views'] = views_dict
        holly_couch[tmp_dv] = dv_doc
        
