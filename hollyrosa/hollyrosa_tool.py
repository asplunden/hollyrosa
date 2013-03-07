# tool for administring the holly_couch database from command line

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
db_name = 'hollyrosa_2013_prod'

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
    
if True:
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


