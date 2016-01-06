# -*- coding: utf-8 -*-
"""
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

import datetime,  logging

log = logging.getLogger(__name__)

from tg import expose, flash, require, url, request, redirect,  validate,  override_template
from tg import tmpl_context

from repoze.what.predicates import Any, is_user, has_permission

from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch, genUID
from hollyrosa.model.booking_couch import getBookingDays,  getAllBookingDays,  getSlotAndActivityIdOfBooking,  getBookingDayOfDate, getVisitingGroupsInDatePeriod,  dateRange2,  getBookingDayOfDateList,  getSlotRowSchemaOfActivity,  getActivityGroupNameAndIdList
from hollyrosa.model.booking_couch import getAllHistoryForBookings,  getAllActivities,  getAllActivityGroups,  getVisitingGroupsAtDate,  getUserNameMap,  getSchemaSlotActivityMap,  getAllVisitingGroups,  getActivityTitleMap


from formencode import validators


#...this can later be moved to the VisitingGroup module whenever it is broken out



from hollyrosa.widgets.edit_booking_day_form import create_edit_booking_day_form

#from hollyrosa.controllers.common import workflow_map,  DataContainer,  getLoggedInUserId,  change_op_map,  getRenderContent, getRenderContentDict,  computeCacheContent,  ,  reFormatDate
from hollyrosa.controllers.common import has_level
from hollyrosa.controllers import common_couch
from hollyrosa.model import holly_couch

__all__ = ['Calendar']


class Calendar(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
        

    @expose('hollyrosa.templates.calendar_overview')
    def overview_all(self):
        """Show an overview of all booking days"""
        return dict(booking_days=[b.doc for b in getAllBookingDays(holly_couch)])


    @expose('hollyrosa.templates.calendar_overview')
    def overview(self):
        """Show an overview of all booking days"""
        today = datetime.date.today().strftime('%Y-%m-%d')
        return dict(booking_days=[b.doc for b in getBookingDays(holly_couch, from_date=today)])
    

    @expose('hollyrosa.templates.calendar_upcoming')
    def upcoming(self):
        """Show an overview of all booking days"""
        today_date_str = datetime.date.today().strftime('%Y-%m-%d')
        
        end_date_str = (datetime.date.today()+datetime.timedelta(5)).strftime('%Y-%m-%d')

        #today_date_str = '2012-08-01'
        #end_date_str = '2012-08-04'
        
        booking_days = getBookingDays(holly_couch, from_date=today_date_str,  to_date=end_date_str) 


        vgroups = getVisitingGroupsInDatePeriod(holly_couch, today_date_str,  end_date_str) # TODO: fix view later.  get_visiting_groups(from_date=today_date_str,  to_date=end_date_str)

        group_info = dict()
        bdays = list()
        for tmp in booking_days:
            b_day = tmp.doc
            tmp_date_today_str = b_day['date']             
            bdays.append(b_day)
            
            group_info[tmp_date_today_str] = dict(arrives=[v.doc for v in vgroups if v.doc.get('from_date','') == tmp_date_today_str], leaves=[v.doc for v in vgroups if v.doc.get('to_date','') == tmp_date_today_str], stays=[v.doc for v in vgroups if v.doc.get('to_date','') > tmp_date_today_str and v.doc.get('from_date','') < tmp_date_today_str])

        return dict(booking_days=bdays, group_info=group_info)
        
        
    @expose('hollyrosa.templates.booking_day_properties')
    @validate(validators={'booking_day_id':validators.Int(not_empty=True)})
    @require(Any(has_level('staff'), has_level('pl'), msg='Only staff members may change booking day properties'))
    def edit_booking_day(self, booking_day_id=None,  **kw):
        booking_day = common_couch.getBookingDay(holly_couch, booking_day_id)
        if not booking_day.has_key('title'):
            booking_day['title'] = ''
        tmpl_context.form = create_edit_booking_day_form
        return dict(booking_day=booking_day,  usage='edit')
        
        
    @validate(create_edit_booking_day_form, error_handler=edit_booking_day)      
    @expose()
    @require(Any(has_level('staff'), has_level('viewer'), msg='Only staff members may change booking day properties'))
    def save_booking_day_properties(self,  _id=None,  note='', title='', num_program_crew_members=0,  num_fladan_crew_members=0):
        
        booking_day_c = common_couch.getBookingDay(holly_couch, _id)
        booking_day_c['note'] = note
        booking_day_c['title'] = title
        booking_day_c['num_program_crew_members'] = num_program_crew_members
        booking_day_c['num_fladan_crew_members'] = num_fladan_crew_members
        holly_couch[_id]=booking_day_c
        
        raise redirect('/booking/day?day_id='+str(_id))
        