# -*- coding: utf-8 -*-
"""
hollyrosa_tool.py

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

import argparse
import json
import logging

import couchdb

parser = argparse.ArgumentParser()
parser.add_argument("--couch", help="url to couch db", default='http://localhost:5989')
parser.add_argument("--database", help="name of database in couch", default='hollyrosa_2015_prod')
parser.add_argument("--username", help="login username", default=None)
parser.add_argument("--password", help="login password", default=None)
parser.add_argument("--save-views", help="save all views code to file from database", action="store_true")
parser.add_argument("--load-views", help="load all views code from file to database", action="store_true")
parser.add_argument("-v", "--verbose", help="turn on verbose logging", action="store_true")
args = parser.parse_args()

# ...init logging'
log = logging.getLogger("hollyrosa_view_tool")

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARN)

# ...read from ini file
db_url = args.couch
db_name = args.database
db_username = args.username
db_password = args.password

couch_server = couchdb.Server(url=db_url)

if db_username != None:
    couch_server.resource.credentials = (db_username, db_password)

try:
    holly_couch = couch_server[db_name]
except couchdb.ResourceNotFound as e:
    holly_couch = couch_server.create(db_name)

design_view_names = ['all_activities', 'booking_day', 'day_schema', 'history', 'notes', 'statistics', 'tag_statistics',
                     'tags', 'user', 'visiting_groups', 'vodb_overview', 'workflow', 'booking_day_live',
                     'program_layer']
save_from = True
upload_to = False

if args.save_views:
    for tmp_name in design_view_names:
        tmp_dv = '_design/%s' % tmp_name
        print('looking for ' + tmp_dv)
        dv_doc = holly_couch[tmp_dv]
        print(dv_doc)
        view_dict = dv_doc['views']
        file_name = ('design_views/%s.viewfunc' % tmp_name)
        f = open(file_name, 'w')
        f.write(json.dumps(view_dict))
        f.close()

if args.load_views:
    for tmp_name in design_view_names:
        tmp_dv = '_design/%s' % tmp_name
        print ('looking for ' + tmp_dv)

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
