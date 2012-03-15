# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012 Martin Eliasson

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

import pylons
from tg import expose, flash, require, url, request, redirect,  validate
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, holly_couch

import datetime,  StringIO,  time

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context
import hashlib

from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking

from booking_history import  remember_workflow_state_change
from hollyrosa.controllers.common import workflow_map,  getLoggedInUser,  getRenderContent,  has_level

from hollyrosa.model.booking_couch import getAllActivityGroups,  getAllScheduledBookings,  getAllBookingDays,  getAllVisitingGroups
from hollyrosa.model.booking_couch import getAgeGroupStatistics, getTagStatistics, getSchemaSlotActivityMap, getActivityTitleMap
__all__ = ['tools']

workflow_submenu = """<ul class="any_menu">
        <li><a href="overview">overview</a></li>
        <li><a href="view_nonapproved">non-approved</a></li>
        <li><a href="view_unscheduled">unscheduled</a></li>
        <li><a href="view_scheduled">scheduled</a></li>
        <li><a href="view_disapproved">dissapproved</a></li>
    </ul>"""

class Tools(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
    
    
    @expose('hollyrosa.templates.tools_show')
    def show(self,  day=None):
        """Show an overview of all bookings"""
        if day == None:
            day = datetime.datetime.today().date().strftime("%Y-%m-%d")
            
        activity_groups = [h.value for h in getAllActivityGroups(holly_couch)]
        return dict(show_day=day,  activity_groups=activity_groups)
        
    
    @expose(content_type='application/x-download')
    def make_program_day_doc(self,  day=None,  file=None):
        
        
        
        in_file = file.file
        
        #in_file=StringIO.StringIO()
        #in_file.write(template)
        #...generate the mapping:
        #   find booking_day corresponding to day
        
        booking_day_o = DBSession.query(booking.BookingDay).filter('date=\''+str(day)+'\'').one()
        bookings = DBSession.query(booking.Booking).filter('booking_day_id='+str(booking_day_o.id)).all()
        
        #...this is VERY wrong since the list isn't produced according to slot row position, have to rethink
        #   also, how to handle trapper 1 to trapper 7
        
        new_bookings = dict()
        new_bookings['Trapper 1'] = [[] for i in range(4)] 
        new_bookings['Trapper 2'] = [[] for i in range(4)] 
        new_bookings['Trapper 3'] = [[] for i in range(4)] 
        new_bookings['Trapper 4'] = [[] for i in range(4)] 
        new_bookings['Trapper 5'] = [[] for i in range(4)] 
        new_bookings['Trapper 6'] = [[] for i in range(4)] 
        new_bookings['Trapper 7'] = [[] for i in range(4)] 
        
        for s in bookings:
            if s.slot_row_position != None:
                tmp_activity_row = new_bookings.get(s.slot_row_position.slot_row.activity.title, [[] for i in range(4)] )
                tmp_slot_index = 0
                #print s.slot_row_position.time_from.strftime('%H:%M') 
                if s.slot_row_position.time_from.strftime('%H:%M') =='09:00':
                    tmp_slot_index = 0
                elif s.slot_row_position.time_from.strftime('%H:%M') == '13:00':
                    tmp_slot_index = 1
                elif s.slot_row_position.time_from.strftime('%H:%M') == '17:00':
                    tmp_slot_index = 2
                else:
                    tmp_slot_index = 3
                
                tmp_visiting_group_name = s.visiting_group_name
                if tmp_visiting_group_name == None:
                    tmp_visiting_group_name = ''
                #tmp_activity_row.append(s.visiting_group_name + ' ' + getRenderContent(s))
                tmp_new_string = tmp_visiting_group_name + ' ' + getRenderContent(s) #s.slot_row_position.slot_row.activity.title
                
                
                #print '***',  tmp_slot_index,  tmp_new_string,  s.slot_row_position.slot_row.activity.title
                
                if s.slot_row_position.slot_row.activity.title == 'Trapper':
                    #print 'TRAPPER'
                    tmp_trapper_index = 1
                    while (tmp_trapper_index < 8):
                        if 0 == len(new_bookings['Trapper %d' % tmp_trapper_index][tmp_slot_index] ):
                            tmp_activity_row = new_bookings['Trapper %d' % tmp_trapper_index]
                            break
                        tmp_trapper_index += 1
                
                tmp_activity_row[tmp_slot_index].append(tmp_new_string)
                new_bookings[s.slot_row_position.slot_row.activity.title] = tmp_activity_row
       
        #...fix Trapper -> Trapper 1--7
        new_new_bookings = dict()
        for key,  tmp_activity_row in new_bookings.items():
            new_new_bookings[key]  = [ ';\n'.join(ts) for ts in tmp_activity_row]
        
    
        #f = open('/home/marel069/programdayn.ods', 'r')
        #template=f.read()
        
        
        out_txt = OOorg.make(in_file,  booking_day_mapping=new_new_bookings)
        #f.close()

        pylons.response.headers['Content-Type'] = 'application/x-download'
        pylons.response.headers['Content-Length'] = len(out_txt)
        pylons.response.headers["Content-Disposition"] = "attachment; filename=make_program_day_doc.ods"
        
        return out_txt


    def get_severity(self, visiting_group,  severity):
        #if booking_o['visiting_group_name'] in ['Program II', 'Konf II', 'Program I', 'Konf I', 'WSJ Home hospitality', '60 Degrees North', 'Led Utb Scout']:
        if visiting_group.get('hide_warn_on_suspect_bookings', False) == True:
            #print 'HIDE WARN'
            severity = 0
        #else:
            #print visiting_group.get('hide_warn_on_suspect_bookings', 'MA')
        return severity


    def fn_sort_problems_by_severity(self, a, b):
        return cmp(b['severity'], a['severity'])
        

    @expose('hollyrosa.templates.view_sanity_check_property_usage')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def sanity_check_property_usage(self):
        
        #...iterate through all bookings, we are only interested in scheduled bookings
        bookings = getAllScheduledBookings(holly_couch, limit=1000000) 
        booking_days_map = dict()
        for bd in getAllBookingDays(holly_couch):
            booking_days_map[bd.doc['_id']] = bd.doc
            
        visiting_group_map = dict()
        for vg in getAllVisitingGroups(holly_couch):
            visiting_group_map[vg.key[1]] = vg.doc
            
        #activity_map = dict()
        activity_title_map = getActivityTitleMap(holly_couch)
        
        problems = list()
        for tmp_bx in bookings:
            tmp_b = tmp_bx.doc
            tmp_b_day_id = tmp_b['booking_day_id']
            tmp_b_day = booking_days_map[tmp_b_day_id]
            
        #    if not activity_map.has_key(tmp_b_day['day_schema_id']):
        #        activity_map[tmp_b_day['day_schema_id']] = getSchemaSlotActivityMap(holly_couch, tmp_b_day['day_schema_id'])

        #    tmp_activity_map = activity_map[tmp_b_day['day_schema_id']]
                 
            if None != tmp_b_day: # and tmp_b_day.date >= datetime.date.today():
                if tmp_b['visiting_group_id'] != '' and (False == tmp_b.get('hide_warn_on_suspect_booking',  False)):
                    tmp_date = tmp_b_day['date']
                    tmp_content = activity_title_map[tmp_b['activity_id']] + ' ' + tmp_b['content']
                    tmp_b_visiting_group = visiting_group_map[tmp_b['visiting_group_id']]

                    
                    if not tmp_b_visiting_group.has_key('from_date'):
                        problems.append(dict(booking=tmp_b, msg='visiting group %s has no from_date' % tmp_b_visiting_group['visiting_group_name'], severity=100))
                    else:
                        if tmp_b_visiting_group['from_date'] > tmp_date:
                            problems.append(dict(booking=tmp_b, msg='arrives at %s but booking %s is at %s' %(str(tmp_b_visiting_group['from_date']), tmp_content ,str(tmp_date)), severity=10))
    
                        if tmp_b_visiting_group['from_date'] == tmp_date:
                            problems.append(dict(booking=tmp_b, msg='arrives same day as booking %s, at %s' % (tmp_content, str(tmp_b_visiting_group['from_date'])), severity=self.get_severity(tmp_b_visiting_group, 1)))
                        
                    if tmp_b_visiting_group['to_date'] < tmp_date:
                        problems.append(dict(booking=tmp_b, msg='leves at %s but booking %s is at %s' % (str(tmp_b_visiting_group['to_date']), tmp_content , str(tmp_date)), severity=10))
    
                    if tmp_b_visiting_group['to_date'] == tmp_date:
                        problems.append(dict(booking=tmp_b, msg='leves same day as booking %s, at %s' % (tmp_content, str(tmp_b_visiting_group['to_date'])), severity=self.get_severity(tmp_b_visiting_group, 1)))
                    
                    tmp_content = tmp_b['content']
                    for tmp_prop in tmp_b_visiting_group['visiting_group_properties'].values():
                        checks = [x+tmp_prop['property'] for x in ['$$','$',  '$#','#']]
                        
                        for check in checks:
                            if check in tmp_content:
                                if tmp_prop['from_date'] > tmp_date:
                                    problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop['property'] + ' usable from ' + str(tmp_prop['from_date']) + ' but booking is at ' + str(tmp_date), severity=10))
    
                                if tmp_prop['from_date'] == tmp_date:
                                    problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop['property'] + ' arrives at ' + str(tmp_prop['from_date']) + ' and booking is the same day', severity=self.get_severity(tmp_b_visiting_group, 1)))
                                    
                                if tmp_prop['to_date'] < tmp_date:
                                    problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop['property'] + ' usable to ' + str(tmp_prop['to_date']) + ' but booking is at ' + str(tmp_date), severity=10))
    
                                if tmp_prop['to_date'] == tmp_date:
                                    problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop['property'] + ' leavs at ' + str(tmp_prop['to_date']) + ' and booking is the same day ', severity=self.get_severity(tmp_b_visiting_group, 1)))
    
                                break # there can be more than one match in checks
        problems.sort(self.fn_sort_problems_by_severity)
        return dict (problems=problems,  visiting_group_map=visiting_group_map)
        
    @expose('hollyrosa.templates.visitor_statistics')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can take a look at people statistics'))
    def visitor_statistics(self):
        
        # TODO: this complete calculation has to be redone 
        #       since visiting group properties doesent 
        #       exist as a 'table' any more.
        #
        # One way could be to make a list of all days.
        #   This list is filled with dicts containing the result
        #   The dicts are filled in by iterating through the visiting groups
        #   properties
        #
        # If one were to make a really complicated couch map, you would 
        # create a key [date, property-from-vgroup-properties] -> value and then sum it using reduce :)
        #
        #
        #
        #
        #        
        
        statistics_totals = getAgeGroupStatistics(holly_couch, group_level=1)
        statistics = getAgeGroupStatistics(holly_couch)
        
        property_names = dict()
        totals = dict() # totals = list()
        for tmp in statistics:   
            tmp_key = tmp.key
            tmp_value = tmp.value            
            
            tmp_property = tmp_key[1]
            tmp_date_x = tmp_key[0]
            tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1], tmp_date_x[2]) #'-'.join([str(t) for t in tmp_date])

            tot = totals.get(tmp_date, dict())
            tot[tmp_property] = int(tmp_value)
            property_names[tmp_property] = 1 # kepiong track of property names used
            totals[tmp_date] = tot
				
        #...same thing but now for aggrgate statistics
        all_totals = list()
        for tmp in statistics_totals:
            tmp_key = tmp.key
            tmp_value = tmp.value
            
            tmp_date_x = tmp_key[0]
            tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1], tmp_date_x[2]) #'-'.join([str(t) for t in tmp_date])
				
            tot = totals.get(tmp_date, dict())
            #...for now we need to protect against tot=0 giving zero division errors
            if tmp_value == 0:
                tmp_value = 1
            tot['tot'] = tmp_value
            totals[tmp_date] = int(tmp_value)
				
            mark = '#444;'
            if tot['tot'] < 250:
                mark = '#484;'
            elif tot['tot'] < 500:
                mark = '#448;'
            elif tot['tot'] < 1000:
                mark = '#828;'
            else:
                mark = '#844;'
            all_totals.append((tmp_date, tot, mark))

            
    #    for booking_day_kv in booking_days:
    #        booking_day = booking_day_kv.doc        
    #        tot = dict()
    #        tot['tot'] = 0 
    #        for tmp_property_row in vgroup_properties:
     #           if (tmp.fromdate <= d) and (tmp.todate >= d):
      #              try:       
            #            tot['tot'] += int(tmp.value)
             #           x = tot.get(tmp.property, 0)
              #          tot[tmp.property] = x + int(tmp.value)
             #           property_names[tmp.property] = 1
         #           except ValueError, e:
       #                 pass


        property_ns = ['spar','uppt','aven','utm']
        l = list()
        for n in property_names.keys():
            if n not in property_ns:
                l.append(n)

        
        return dict(property_names=l, people_by_day=all_totals)






    @expose('hollyrosa.templates.vodb_statistics')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can take a look at people statistics'))
    def vodb_statistics(self):
        
        statistics_totals = getTagStatistics(holly_couch, group_level=1)
        statistics = getTagStatistics(holly_couch, group_level=2)
        
        #...find all tags that is used and perhaps filter out unwanted ones.
        
        tags = dict()
        totals = dict() 
        for tmp in statistics:   
            tmp_key = tmp.key
            tmp_value = tmp.value                        
            tmp_tag = tmp_key[1]
            
            if tmp_tag[:4] == 'vodb':
                tmp_date_x = tmp_key[0]
                tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1], tmp_date_x[2]) 
            
                tot = totals.get(tmp_date, dict())
                tot[tmp_tag] = int(tmp_value)
                sum = tot.get('tot',0) 
                sum += int(tmp_value)
                tot['tot'] = sum
                tags[tmp_tag] = 1
                totals[tmp_date] = tot
                
        all_totals=list()
        for tmp in statistics_totals:   
            tmp_key = tmp.key
            tmp_value = tmp.value                        
            tmp_date_x = tmp_key[0]
            tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1], tmp_date_x[2]) 
            
            tot = totals[tmp_date]
            mark = '#444;'                
            if tot['tot'] < 250:
                mark = '#484;'
            elif tot['tot'] < 500:
                mark = '#448;'
            elif tot['tot'] < 1000:
                mark = '#828;'
            else:
                mark = '#844;'
            all_totals.append((tmp_date, tot, mark))

        
        return dict(tags=['vodb:definitiv',u'vodb:preliminär',u'vodb:förfrågan', 'vodb:na'], people_by_day=all_totals)










    @expose('hollyrosa.templates.booking_day_summary')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def booking_statistics(self):
        """Show a complete booking day"""
        
        slot_rows = DBSession.query(booking.SlotRow).options(eagerload('activity'))
        slot_rows_n = []
        for s in slot_rows:
            slot_rows_n.append(s)

        #...first, get booking_day for today
        bookings = DBSession.query(booking.Booking).all()
        
        #...additions - counting properties
        visiting_groups = DBSession.query(booking.VisitingGroup).all() #join(booking.VistingGroupProperty).all()
        vgroup_properties = DBSession.query(booking.VistingGroupProperty).all()
        
        activity_totals = dict()
        totals = 0
        for s in bookings:
            if s.booking_day_id != None:
                activity_count_list, activity_property_count = activity_totals.get(s.activity.id, (list(), {}))
                
                #...check in content for properties
                tmp_content = s.content
                tmp_visiting_group = s.visiting_group
               
                if None != tmp_visiting_group:
                    tmp_vgroup_properties = tmp_visiting_group.visiting_group_property
                    for tmp_vgroup_property in tmp_vgroup_properties:
                        if '$'+tmp_vgroup_property.property in tmp_content:
                            tmp_count_x = activity_property_count.get(tmp_vgroup_property.property, 0) + int(tmp_vgroup_property.value)
                            activity_property_count[tmp_vgroup_property.property] = tmp_count_x
                            tmp_count_all = activity_property_count.get('ALL', 0) + int(tmp_vgroup_property.value)
                            activity_property_count['ALL'] = tmp_count_all


                activity_count_list.append(s)
                activity_totals[s.activity.id] = (activity_count_list, activity_property_count)
                totals += 1


        return dict(slot_rows=slot_rows_n,  bookings=activity_totals, totals=totals)
    
    
        
    #@expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def update_schema(self):
        s = holly_couch['day_schema.1']
        pos = 1
        activity = DBSession.query(booking.Activity).all() # use slot_rows instead , the pos counter screws things up...
        slot_rows = DBSession(booking.SlotRow).all()
        
        zorder = 1
        sch = dict()
        for sl in slot_rows:
            #for ac in activity:
            ac = sl.activity
            
            tmp = [dict(id='activity.'+str(ac.id),  zorder=zorder)]
            zorder += 1
            
            slrp = dict(time_from='09:00:00',  time_to='12:00:00',  duration='03:00:00' ,  slot_id='slot.'+str(pos),  title='FM')
            pos += 1
            tmp.append(slrp)
            
            slrp = dict(time_from='13:30:00',  time_to='17:00:00',  duration='03:30:00' ,  slot_id='slot.'+str(pos),  title='EM')
            pos += 1
            tmp.append(slrp)
            
            slrp = dict(time_from='19:00:00',  time_to='21:00:00',  duration='02:00:00' ,  slot_id='slot.'+str(pos),  title=u'Kväll')
            pos += 1
            tmp.append(slrp)

            slrp = dict(time_from='21:00:00',  time_to='23:59:00',  duration='03:00:00' ,  slot_id='slot.'+str(pos),  title='After hours')
            pos += 1
            tmp.append(slrp)

            sch['activity.'+str(ac.id)] = tmp
        s['schema'] = sch
        s = holly_couch['day_schema.1'] = s
        raise redirect('/')
        
        
#    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def make_booking_days(self):
        pos = 1000
        dates = list()
        #...must iterate a date range, check out websetup.py....        
        for i in range(30):
            d = datetime.date(2012, 6, i+1)
            dates.append(str(d))
       
        for i in range(31):
            d = datetime.date(2012, 7, i+1)
            dates.append(str(d))

        for i in range(31):
            d = datetime.date(2012, 8, i+1)
            dates.append(str(d))
            
            
        for d in dates:
            #print d
            bd_c = dict(type='booking_day', date=d, note='', title='', num_program_crew_members=0, num_fladan_crew_members=0, day_schema_id='day_schema.1', zorder=pos )
            holly_couch['booking_day.'+str(pos)] = bd_c
            pos += 1
            
        raise redirect('/')       
        
#    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_bookings(self):
        for b in holly_couch.view('all_activities/erasure', include_docs=True):
            holly_couch.delete(b.doc)
        raise redirect('/')
    
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def update_password(self, id, new_passwd):
        s = holly_couch[id]
        h = hashlib.sha256('gninyd') # salt
        h.update(new_passwd)
        c = h.hexdigest()
        s['password'] = c
        holly_couch[id] = s
        raise redirect('/')


    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def set_booking_day_schema_ids(self):
        booking_days = [b.doc for b in getAllBookingDays(holly_couch)]
        for bdy in booking_days:
            if bdy['date'] <= '2012-07-22' or bdy['date'] > '2012<07-29':
                bdy['day_schema_id'] = 'day_schema.2012'
                holly_couch[bdy['_id']] = bdy
            
        raise redirect('/')
        