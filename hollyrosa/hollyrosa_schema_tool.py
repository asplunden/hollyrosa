# -*- coding: utf-8 -*-
"""
hollyrosa_tool.py

Copyright 2010-2020 Martin Eliasson

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
import datetime
import logging

import couchdb


def dateRange(from_date, to_date, format='%a %b %d %Y'):
    one_day = datetime.timedelta(1)
    formated_dates = list()
    tmp_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    tmp_to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    while tmp_date <= tmp_to_date:
        formated_dates.append(tmp_date.strftime(format))
        tmp_date = tmp_date + one_day
    return formated_dates


parser = argparse.ArgumentParser()
parser.add_argument("--couch", help="url to couch db", default='http://localhost:5989')
parser.add_argument("--database", help="name of database in couch", default='hollyrosa_2015_prod')
parser.add_argument("--username", help="login username", default=None)
parser.add_argument("--password", help="login password", default=None)
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
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create(db_name)

if True:
    for b in holly_couch.view('booking_day/all_booking_days', include_docs=True):
        doc = holly_couch[b.doc['_id']]
        doc['staff_schema_id'] = 'funk_schema.2015'
        holly_couch[b.doc['_id']] = doc

if True:
    for b in holly_couch.view('booking_day/all_booking_days', include_docs=True):
        doc = holly_couch[b.doc['_id']]
        doc['staff_schema_id'] = 'funk_schema.2015'
        holly_couch[b.doc['_id']] = doc
