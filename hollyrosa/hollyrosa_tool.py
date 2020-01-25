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

import copy, datetime, logging, argparse
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




parser = argparse.ArgumentParser()
parser.add_argument("--couch", help="url to couch db", default='http://localhost:5989')
parser.add_argument("--database", help="name of database in couch", default='hollyrosa_2018_prod')
parser.add_argument("--username", help="login username", default=None)
parser.add_argument("--password", help="login password", default=None)
parser.add_argument("--save-views", help="save all views code to file from database", action="store_true")
parser.add_argument("--load-views", help="load all views code from file to database", action="store_true")
parser.add_argument("--clear-erasable", help="dangerous option for creating a new DB", action="store_true")
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



if args.clear_erasable:
    for b in holly_couch.view('all_activities/erasure', include_docs=True):
        doc = b.doc
        logging.debug('delete %s' % str( doc ))
        holly_couch.delete(b.doc)

if False:
    for b in holly_couch.view('all_activities/scan_all', include_docs=True):
        b.doc['do_not_delete'] = True
        holly_couch[b.doc['_id']] = b.doc

if False:
    #...try to generate all booking days. Ah, first generate day schema!
    ds = holly_couch['summer_schema.2016']
    new_ds = copy.deepcopy(ds)

    holly_couch['summer_schema.2017'] = ds

    ds = holly_couch['school_schema.2016']
    new_ds = copy.deepcopy(ds)
    holly_couch['school_schema.2017'] = ds

    ds = holly_couch['60dn_schema.2013']
    new_ds = copy.deepcopy(ds)
    holly_couch['60dn_schema.2017'] = ds


if True:
    pos = 3500
    school_dates_spring = dateRange('2018-05-01', '2018-06-09', format='%Y-%m-%d')
    summer_dates = dateRange('2018-06-10', '2018-08-12', format='%Y-%m-%d')
    sixtydn_dates = [] #dateRange('2013-0', '2013-08-18', format='%Y-%m-%d')
    school_dates_autumn = dateRange('2018-08-13', '2018-10-31', format='%Y-%m-%d')

    worklist = [(school_dates_spring,  'school_schema.2018'), (summer_dates, 'summer_schema.2018'), (sixtydn_dates, '60dn_schema.2017'), (school_dates_autumn, 'school_schema.2018')]

    for days, day_schema_id in worklist:
        for d in days:
            bd_c = dict(type='booking_day', date=d, note='', title='', num_program_crew_members=0, num_fladan_crew_members=0, day_schema_id=day_schema_id, zorder=pos,  staff_schema_id='funk_schema.2015', room_schema_id='room_schema.2013' )
            holly_couch['booking_day.'+str(pos)] = bd_c
            pos += 1


#...We will have to list all activities and all activity_groups and then look for all booking_info_id. Save them all in a dict and after that we can delete note that are not in that dict
#...better mark the docs as eternal

# then for visiting groups we want to keep a few eternal too

#...a two step process really.

# never delete eternal documents


# Creating a tmp day schema
if False:
    activities = list()
    agroups=dict()

    for tmp_day_schema in holly_couch.view('day_schema/day_schema',  include_docs=True):
        day_schema = tmp_day_schema.doc

        for k, v in day_schema['schema'].items():
            activities.append(k)
            tmp_activity = holly_couch[k]
            agid = tmp_activity['activity_group_id']

            tmp_agroup = holly_couch[agid]
            if not agroups.has_key(tmp_agroup.id):
                agroups[tmp_agroup.id] = tmp_agroup

        all_keys = [k for k in agroups.keys()]
        day_schema2 = holly_couch[day_schema.id]
        day_schema2['activity_groups_ids'] = all_keys
        holly_couch[day_schema.id] = day_schema2



# Creating a room schema for 2013
if False:
    activities = list()
    agroups=dict()

    #...list all activities, but select only activities in activity groups starting with roomgroup.....

    for tmp_day_schema in holly_couch.view('day_schema/day_schema',  include_docs=True):
        day_schema = tmp_day_schema.doc

        for k, v in day_schema['schema'].items():
            activities.append(k)
            tmp_activity = holly_couch[k]
            agid = tmp_activity['activity_group_id']
            tmp_agroup = holly_couch[agid]
            if not agroups.has_key(tmp_agroup.id):
                agroups[tmp_agroup.id] = tmp_agroup

        all_keys = [k for k in agroups.keys()]
        day_schema2 = holly_couch[day_schema.id]
        day_schema2['activity_groups_ids'] = all_keys
        holly_couch[day_schema.id] = day_schema2



def makeSlotRow(slot_id_start, zorder, activity_id):
    result = list()
    result.append({u'zorder': zorder, u'id': activity_id})
    result.append({u'duration': u'12:00:00', u'time_to': u'12:00:00', u'slot_id': u'slot.%d' % slot_id_start, u'time_from': u'00:00:00', u'title': u'FM'})
    slot_id_start += 1
    result.append({u'duration': u'12:00:00', u'time_to': u'23:59:59', u'slot_id': u'slot.%d' % slot_id_start, u'time_from': u'12:00:00', u'title': u'EM'})
    slot_id_start += 1
    return result, slot_id_start


#...creating activities for all rooms with corresponding activity groups and schema.
def makeRoom(holly_rosa, title='', activity_group_id='',  capacity='', zorder=0, schema=None, max_slot_id=0 ):
    new_room = dict(tags="", certificate_needed=None, bg_color='#fff', capacity=0, title='-', type="activity", zorder=0, do_not_delete=True, default_booking_state=0, subtype='room')
    new_room['title'] = title
    new_room['activity_group_id'] = activity_group_id
    new_room['description']=title
    new_room['capacity']=capacity
    new_room['zorder']=zorder
    new_id = 'funk.'+title.lower()
    new_id = new_id.replace('å', 'a')
    new_id=new_id.replace('ä', 'a')
    new_id=new_id.replace('ö', 'o')
    new_id=new_id.replace(' ', '_')
    new_id=new_id.replace('-', '_')

    holly_rosa[new_id] = new_room

    tmp_slot_row, max_slot_id = makeSlotRow(max_slot_id, max_slot_id, new_id)
    schema[new_id] = tmp_slot_row

    return max_slot_id


if False:
    makeRoom(holly_couch,  'Grundkallen - Höger',  activity_group_id='roomgroup.fyrbyn', capacity=6,  zorder=0 )
    makeRoom(holly_couch,  'Grundkallen - Vänster',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=1 )
    makeRoom(holly_couch,  'Märket - Höger',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=2 )
    makeRoom(holly_couch,  'Märket - Vänster',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=3)
    makeRoom(holly_couch,  'Svartklubben - Höger',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=4 )
    makeRoom(holly_couch,  'Svartklubben - Vänster',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=5)
    makeRoom(holly_couch,  'Understen - Höger',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=6 )
    makeRoom(holly_couch,  'Understen - Vänster',  activity_group_id='roomgroup.fyrbyn',  capacity=6,  zorder=7)

    makeRoom(holly_couch,  'Nordan - Höger',  activity_group_id='roomgroup.vaderstracken',  capacity=4,  zorder=10)
    makeRoom(holly_couch,  'Nordan - Vänster',  activity_group_id='roomgroup.vaderstracken',  capacity=4,  zorder=11)
    makeRoom(holly_couch,  'Sunnan - Höger',  activity_group_id='roomgroup.vaderstracken',  capacity=6,  zorder=11)
    makeRoom(holly_couch,  'Sunnan - Vänster',  activity_group_id='roomgroup.vaderstracken',  capacity=6,  zorder=12)
    makeRoom(holly_couch,  'Västan - Höger',  activity_group_id='roomgroup.vaderstracken',  capacity=4,  zorder=13)
    makeRoom(holly_couch,  'Västan - Vänster',  activity_group_id='roomgroup.vaderstracken',  capacity=4,  zorder=14)
    makeRoom(holly_couch,  'Östan - Höger',  activity_group_id='roomgroup.vaderstracken',  capacity=5,  zorder=15)
    makeRoom(holly_couch,  'Östan - Vänster',  activity_group_id='roomgroup.vaderstracken',  capacity=6,  zorder=16)
    makeRoom(holly_couch,  'Sydvästen - Nedre',  activity_group_id='roomgroup.vaderstracken',  capacity=3,  zorder=17)
    makeRoom(holly_couch,  'Sydvästen - Övre',  activity_group_id='roomgroup.vaderstracken',  capacity=3,  zorder=18)

    makeRoom(holly_couch,  'Lugnet - Höger',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=20)
    makeRoom(holly_couch,  'Lugnet - Vänster',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=21)
    makeRoom(holly_couch,  'Brisen - Höger',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=22)
    makeRoom(holly_couch,  'Brisen - Vänster',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=23)
    makeRoom(holly_couch,  'Kulingen - Höger',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=24)
    makeRoom(holly_couch,  'Kulingen - Vänster',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=25)
    makeRoom(holly_couch,  'Stormen - Höger',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=26)
    makeRoom(holly_couch,  'Stormen - Vänster',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=27)
    makeRoom(holly_couch,  'Orkanen - Höger',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=28)
    makeRoom(holly_couch,  'Orkanen - Vänster',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=29)
    makeRoom(holly_couch,  'Bleket - Höger',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=30)
    makeRoom(holly_couch,  'Bleket - Vänster',  activity_group_id='roomgroup.vindarnashus',  capacity=2,  zorder=31)

    makeRoom(holly_couch,  'Kulan - Nedre Höger',  activity_group_id='roomgroup.tunet',  capacity=6,  zorder=40)
    makeRoom(holly_couch,  'Kulan - Övre Höger',  activity_group_id='roomgroup.tunet',  capacity=3,  zorder=41)
    makeRoom(holly_couch,  'Kulan - Nedre Vänster',  activity_group_id='roomgroup.tunet',  capacity=4,  zorder=42)
    makeRoom(holly_couch,  'Kulan - Övre Vänster',  activity_group_id='roomgroup.tunet',  capacity=3,  zorder=43)

    makeRoom(holly_couch,  'Lillgårn - Nedre',  activity_group_id='roomgroup.tunet',  capacity=1,  zorder=44)
    makeRoom(holly_couch,  'Lillgårn - Övre',  activity_group_id='roomgroup.tunet',  capacity=4,  zorder=45)

    makeRoom(holly_couch,  'Magasinet - Höger',  activity_group_id='roomgroup.tunet',  capacity=1,  zorder=46)
    makeRoom(holly_couch,  'Magasinet - Rakt Fram',  activity_group_id='roomgroup.tunet',  capacity=2,  zorder=47)

    makeRoom(holly_couch,  'Matlådan - Singel',  activity_group_id='roomgroup.tunet',  capacity=1,  zorder=48)
    makeRoom(holly_couch,  'Matlådan - Spis',  activity_group_id='roomgroup.tunet',  capacity=3,  zorder=49)
    makeRoom(holly_couch,  'Matlådan - Viggen',  activity_group_id='roomgroup.tunet',  capacity=2,  zorder=50)
    makeRoom(holly_couch,  'Matlådan - Vänster',  activity_group_id='roomgroup.tunet',  capacity=2,  zorder=51)
    makeRoom(holly_couch,  'Storgårn - Sjukan',  activity_group_id='roomgroup.tunet',  capacity=4,  zorder=52)

    #...add Alphyddan group
    makeRoom(holly_couch,  'Alphyddan - Norra Höger',  activity_group_id='roomgroup.alphyddorna',  capacity=2,  zorder=60)
    makeRoom(holly_couch,  'Alphyddan - Norra Vänster',  activity_group_id='roomgroup.alphyddorna',  capacity=2,  zorder=61)
    makeRoom(holly_couch,  'Alphyddan - Södra Höger',  activity_group_id='roomgroup.alphyddorna',  capacity=2,  zorder=62)
    makeRoom(holly_couch,  'Alphyddan - Södra Vänster',  activity_group_id='roomgroup.alphyddorna',  capacity=2,  zorder=63)

    #...add kojan group
    makeRoom(holly_couch,  'Kojan - Höger',  activity_group_id='roomgroup.kojan',  capacity=2,  zorder=70)
    makeRoom(holly_couch,  'Kojan - Vänster',  activity_group_id='roomgroup.kojan',  capacity=2,  zorder=71)
    makeRoom(holly_couch,  'Grönkulla - Allrum',  activity_group_id='roomgroup.kojan',  capacity=4,  zorder=72)

    #...add Gökboet group
    makeRoom(holly_couch,  'Gökboet',  activity_group_id='roomgroup.gokboet',  capacity=2,  zorder=80)


    makeRoom(holly_couch,  'Bygget - Höger',  activity_group_id='roomgroup.skrakvik',  capacity=3,  zorder=81)
    makeRoom(holly_couch,  'Bygget - Vänster',  activity_group_id='roomgroup.skrakvik',  capacity=3,  zorder=82)
    makeRoom(holly_couch,  'Enskede/Prästgården - Höger',  activity_group_id='roomgroup.skrakvik',  capacity=2,  zorder=83)
    makeRoom(holly_couch,  'Enskede/Prästgården - Vardagsrum',  activity_group_id='roomgroup.skrakvik',  capacity=2,  zorder=84)
    makeRoom(holly_couch,  'Enskede/Prästgården - Vänster',  activity_group_id='roomgroup.skrakvik',  capacity=2,  zorder=85)
    makeRoom(holly_couch,  'Gutegården - Höger',  activity_group_id='roomgroup.skrakvik',  capacity=3,  zorder=86)
    makeRoom(holly_couch,  'Gutegården - Vänster',  activity_group_id='roomgroup.skrakvik',  capacity=3,  zorder=87)

    #...add group TC
    makeRoom(holly_couch,  'Backstugan',  activity_group_id='roomgroup.tc',  capacity=4,  zorder=90)




if False:
    #...find funk schema
    doc = holly_couch['funk_schema.2015']
    schema = doc['schema']

    #...find max slot id
    max_slot_id = 0
    for k, v in schema.items():
        #...v is a list of slots
        for tmp_slot in v[1:]:
            tmp_slot_id_num = int(tmp_slot['slot_id'].replace('slot.',''))
            max_slot_id = max(max_slot_id, tmp_slot_id_num)

    #copy last slot row inserting more slot rows
    max_slot_id += 1

    #...add funk/add rooms


    max_slot_id = makeRoom(holly_couch,  'Kökslags chef',  activity_group_id='funkgroup.kok', capacity=0,  zorder=200, schema=schema, max_slot_id=max_slot_id )
    max_slot_id = makeRoom(holly_couch,  'Kök',  activity_group_id='funkgroup.kok', capacity=0,  zorder=201, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Inten PL',  activity_group_id='funkgroup.inten', capacity=0,  zorder=202, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Inten',  activity_group_id='funkgroup.inten', capacity=0,  zorder=203, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Bagar PL',  activity_group_id='funkgroup.bagare', capacity=0,  zorder=204, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Bagare',  activity_group_id='funkgroup.bagare', capacity=0,  zorder=205, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Lillis PL',  activity_group_id='funkgroup.lillis', capacity=0,  zorder=206, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Lillis',  activity_group_id='funkgroup.lillis', capacity=0,  zorder=207, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Skeppare',  activity_group_id='funkgroup.rederiet', capacity=0,  zorder=208, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Matros',  activity_group_id='funkgroup.rederiet', capacity=0,  zorder=209, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Assistent',  activity_group_id='funkgroup.island', capacity=0,  zorder=210, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Arbetshäst',  activity_group_id='funkgroup.island', capacity=0,  zorder=211, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Lägerdoktor',  activity_group_id='funkgroup.island', capacity=0,  zorder=212, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Sjöledare',  activity_group_id='funkgroup.fladan', capacity=0,  zorder=213, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Fladian',  activity_group_id='funkgroup.fladan', capacity=0,  zorder=214, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Programledare',  activity_group_id='funkgroup.program', capacity=0,  zorder=215, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Programmare',  activity_group_id='funkgroup.program', capacity=0,  zorder=216, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Läger',  activity_group_id='funkgroup.program', capacity=0,  zorder=217, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Traktor chef',  activity_group_id='funkgroup.traktor', capacity=0,  zorder=218, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Traktor',  activity_group_id='funkgroup.traktor', capacity=0,  zorder=219, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Storgårn PL',  activity_group_id='funkgroup.storgarn', capacity=0,  zorder=220, schema=schema, max_slot_id=max_slot_id  )
    max_slot_id = makeRoom(holly_couch,  'Storgårn',  activity_group_id='funkgroup.storgarn', capacity=0,  zorder=221, schema=schema, max_slot_id=max_slot_id  )

    #...we need to make a schema with no slot rows and then add the above to the schema
    holly_couch['funk_schema.2015'] = doc
