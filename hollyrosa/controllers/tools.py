# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011 Martin Eliasson

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
from hollyrosa.model import DBSession, metadata,  booking
from sqlalchemy import and_
from sqlalchemy.orm import eagerload,  eagerload_all

import datetime,  StringIO,  time

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context
import OOorg 


from hollyrosa.widgets.edit_visiting_group_form import create_edit_visiting_group_form
from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form
from hollyrosa.widgets.edit_new_booking_request import  create_edit_new_booking_request_form
from hollyrosa.widgets.edit_book_slot_form import  create_edit_book_slot_form
from hollyrosa.widgets.validate_get_method_inputs import  create_validate_schedule_booking,  create_validate_unschedule_booking

from booking_history import  remember_workflow_state_change
from hollyrosa.controllers.common import workflow_map,  getLoggedInUser,  getRenderContent

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
            
        activity_groups = DBSession.query(booking.ActivityGroup).all()
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
                print s.slot_row_position.time_from.strftime('%H:%M') 
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
                    print 'TRAPPER'
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


    def get_severity(self, booking_o, severity):
        if booking_o.visiting_group.name in ['Program II', 'Konf II', 'Program I', 'Konf I', 'WSJ Home hospitality', '60 Degrees North', 'Led Utb Scout']:
            severity = 0
        return severity


    def fn_sort_problems_by_severity(self, a, b):
        return cmp(b['severity'], a['severity'])

    @expose('hollyrosa.templates.view_sanity_check_property_usage')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def sanity_check_property_usage(self):
        
        #...iterate through all bookings
        bookings = DBSession.query(booking.Booking).join(booking.VisitingGroup).join(booking.VistingGroupProperty).all()
        
        #...join visiting group (bookings with no visiting group is not interesting)
        
        #...also, booking with no booking day is not interesting
        
        #...given a visiting group for the booking, check the visiting group properties and for each visiting group property:
        #      check content for usage of each property, if property is used, check from and to date of property against bookings day
        #...do a check on groups from and to date against booking day too.
        
        problems = []
        for tmp_b in bookings:
            tmp_b_day = tmp_b.booking_day
            
            if None != tmp_b_day and tmp_b_day.date >= datetime.date.today():
                tmp_date = tmp_b_day.date
                
                if tmp_b.visiting_group.fromdate > tmp_date:
                    problems.append(dict(booking=tmp_b, msg='arrives at ' + str(tmp_b.visiting_group.fromdate) + ' but booking is at ' + str(tmp_date), severity=10))

                if tmp_b.visiting_group.fromdate == tmp_date:
                    problems.append(dict(booking=tmp_b, msg='arrives same day as booking, at ' + str(tmp_b.visiting_group.fromdate), severity=self.get_severity(tmp_b, 1)))
                    
                if tmp_b.visiting_group.todate < tmp_date:
                    problems.append(dict(booking=tmp_b, msg='leves at ' + str(tmp_b.visiting_group.todate) + ' but booking is at ' + str(tmp_date), severity=10))

                if tmp_b.visiting_group.todate == tmp_date:
                    problems.append(dict(booking=tmp_b, msg='leves same day as booking, at ' + str(tmp_b.visiting_group.todate), severity=self.get_severity(tmp_b, 1)))
                
                tmp_content = tmp_b.content
                for tmp_prop in tmp_b.visiting_group.visiting_group_property:
                    checks = [x+tmp_prop.property for x in ['$$','$',  '$#','#']]
                    
                    for check in checks:
                        if check in tmp_content:
                            if tmp_prop.fromdate > tmp_date:
                                problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop.property + ' usable from ' + str(tmp_prop.fromdate) + ' but booking is at ' + str(tmp_date), severity=10))

                            if tmp_prop.fromdate == tmp_date:
                                problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop.property + ' arrives at ' + str(tmp_prop.fromdate) + ' and booking is the same day', severity=self.get_severity(tmp_b, 1)))
                                
                            if tmp_prop.todate < tmp_date:
                                problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop.property + ' usable to ' + str(tmp_prop.todate) + ' but booking is at ' + str(tmp_date), severity=10))

                            if tmp_prop.todate == tmp_date:
                                problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop.property + ' leavs at ' + str(tmp_prop.todate) + ' and booking is the same day ', severity=self.get_severity(tmp_b, 1)))

                            break # there can be more than one match in checks
        problems.sort(self.fn_sort_problems_by_severity)
        return dict (problems=problems)
        
    @expose('hollyrosa.templates.visitor_statistics')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('pl'),  msg='Only PL or staff members can take a look at people statistics'))
    def visitor_statistics(self):
        
        booking_days = DBSession.query(booking.BookingDay).all()
        visiting_groups = DBSession.query(booking.VisitingGroup).all() #join(booking.VistingGroupProperty).all()
        vgroup_properties = DBSession.query(booking.VistingGroupProperty).all()
        totals = []
        dates = [b.date for b in booking_days]
        dates.sort()
        property_names = dict()
        for d in dates:        
            tot = dict()
            tot['tot'] = 0 
            for tmp in vgroup_properties:
                if (tmp.fromdate <= d) and (tmp.todate >= d):
                    try:
                        tot['tot'] += int(tmp.value)
                        x = tot.get(tmp.property, 0)
                        tot[tmp.property] = x + int(tmp.value)
                        property_names[tmp.property] = 1
                    except ValueError, e:
                        pass
            mark = '#444;'
            if tot['tot'] < 250:
                mark = '#484;'
            elif tot['tot'] < 500:
                mark = '#448;'
            elif tot['tot'] < 1000:
                mark = '#828;'
            else:
                mark = '#844;'
            totals.append((d, tot, mark))


        property_ns = ['spar','uppt','aven','utm']
        l = list()
        for n in property_names.keys():
            if n not in property_ns:
                l.append(n)

        return dict(property_names=l, people_by_day=totals)



    @expose('hollyrosa.templates.booking_day_summary')
    @require(Any(is_user('root'), has_permission('staff'), has_permission('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
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
