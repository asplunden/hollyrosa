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
from hollyrosa.model import holly_couch,  genUID
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
from hollyrosa.controllers.common import workflow_map,  getLoggedInUser,  getRenderContent,  has_level

from hollyrosa.model.booking_couch import getAllActivityGroups

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
            
        activity_groups = getAllActivityGroups()
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
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
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
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),  msg='Only PL or staff members can take a look at people statistics'))
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
    
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_activity_groups(self):
        activity_groups = DBSession.query(booking.ActivityGroup).all()
        for acg in activity_groups:
            acg_c = dict(title=acg.title,  description=acg.description, zorder=acg.id,  type='activity_group')
            holly_couch['activity_group.'+str(acg.id)] = acg_c
        raise redirect('tools')
    
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_activity(self):
        activity = DBSession.query(booking.Activity).all()
        for ac in activity:
            print ac
            ac_c = dict(type='activity',  bg_color=ac.bg_color,  guides_per_slot=ac.guides_per_slot,  guides_per_day=ac.guides_per_day,  equipment_needed=ac.equipment_needed, education_needed=ac.education_needed,  certificate_needed = ac.certificate_needed, 
                        tags = '', title=ac.title, description = ac.description,  external_link = ac.external_link,  internal_link = ac.internal_link,  print_on_demand_link = ac.print_on_demand_link,  capacity = ac.capacity,  default_booking_state = ac.default_booking_state, 
                        activity_group_id = 'activity_group.'+str(ac.activity_group_id))
                        
            holly_couch['activity.'+str(ac.id)] = ac_c
        raise redirect('/')
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def update_schema(self):
        s = holly_couch['day_schema.1']
        pos = 1
        activity = DBSession.query(booking.Activity).all() # use slot_rows instead , the pos counter screws things up...
        slot_rows = DBSession.query(booking.SlotRow).all()
        
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
        
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def update_booking_days(self):
        booking_days = DBSession.query(booking.BookingDay).all()
        pos = 1
        for bd in booking_days:
            bd_c = holly_couch['booking_day.'+str(bd.id)]
            #bd_c = dict(type='booking_day',  date=str(bd.date),  note=bd.note, num_program_crew_members=bd.num_program_crew_members,  num_fladan_crew_members=bd.num_fladan_crew_members,  day_schema_id='day_schema.'+str(bd.day_schema_id),  zorder=pos )
            bd_c['zorder'] = pos
            holly_couch['booking_day.'+str(bd.id)] = bd_c
            pos += 1
            
        raise redirect('/')
        
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_visiting_groups(self):
        visiting_groups = DBSession.query(booking.VisitingGroup).all()
        for vg in visiting_groups:
            vg_c = dict(type='visiting_group', name=vg.name,  from_date=str(vg.fromdate),  to_date = str(vg.todate),  info = vg.info,  contact_person = vg.contact_person,  contact_person_phone = vg.contact_person_phone,
                        contact_person_email = vg.contact_person_email,  calendar_id=vg.calendar_id,  boknr=vg.boknr, boknstatus=vg.boknstatus,  camping_location = vg.camping_location)        
                        
            #...now transfer properties
            vgp_c = dict()
            for vgp in vg.visiting_group_property:
                vgp_c[vgp.id] = dict(property=vgp.property,  value=vgp.value,  unit=vgp.unit,  description=vgp.description,  from_date=str(vgp.fromdate),  to_date=str(vgp.todate),  id=vgp.id)
            vg_c['visiting_group_properties'] = vgp_c



            holly_couch['visiting_group.'+str(vg.id)] = vg_c
        raise redirect('/')
        
        #...need to move all bookings into couch !
        
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_bookings(self):
        bookings = DBSession.query(booking.Booking).all()
        
        for b in bookings:
            bc = holly_couch['booking.'+str(b.id)]
            #bc = dict(type='booking')
            bc['type'] = 'booking'
            bc['content'] = b.content
            bc['visiting_group_name'] = b.visiting_group_name
            bc['requested_date'] = str(b.requested_date)
            bc['valid_from'] = str(b.valid_from)
            bc['valid_to'] = str(b.valid_to)
            bc['booking_state']  = b.booking_state
            bc['activity_id'] = 'activity.' + str(b.activity_id)
            
            if b.slot_row_position != None:
                if b.activity_id != b.slot_row_position.slot_row.activity_id:
                    raise IOError
                
            bc['last_changed_by_id'] = 'user.'+str(b.last_changed_by_id)
            bc['approved_by_id'] = 'user.'+str(b.last_changed_by_id)
            bc['visiting_group_id'] = 'visiting_group.' + str(b.visiting_group_id) 
            bc['slot_id'] = 'slot.'+str(b.slot_row_position_id)
            bc['booking_day_id'] = 'booking_day.' + str(b.booking_day_id)
            if None == b.booking_day_id:
                bc['booking_day_id'] = ''
            bc['misc'] = b.misc
            bc['cache_content'] = b.cache_content
            
        
            holly_couch['booking.'+str(b.id)] = bc
        raise redirect('/')
        
    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_slot_state(self):
        sts = DBSession.query(booking.SlotRowPositionState).all()
        
        for st in sts:
            #s = dict(type='slot_state')
            s = holly_couch['slot_state.'+str(st.id)]
            s['type'] = 'slot_state'
            s['level'] = st.level
            s['slot_id'] = 'slot.'+str(st.slot_row_position_id)
            s['booking_day_id'] = 'booking_day.'+str(st.booking_day_id)
            
            
            
            
            
            
            
            holly_couch['slot_state.'+str(st.id)] = s
        
        raise redirect('/')


    @expose()
    @require(Any(has_level('pl'),  msg='Only PL or staff members can take a look at booking statistics'))
    def transfer_history(self):
        sts = DBSession.query(booking.BookingHistory).all()
        
        for st in sts:
            #s = dict(type='booking_history')
            s = holly_couch['booking_history.'+str(st.id)]
            
            s['change_op'] = st.change_op
            s['booking_content'] = st.booking_content
            s['change'] = st.change
            s['changed_by'] = st.changed_by
            s['timestamp'] = str(st.timestamp)
            s['booking_id'] = 'booking.'+str(st.booking_id)
            s['booking_day_id'] = 'booking_day.'+str(st.booking_day_id)
            holly_couch['booking_history.'+str(st.id)] = s
            
        
        raise redirect('/')
