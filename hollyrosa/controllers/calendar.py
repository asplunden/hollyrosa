# -*- coding: utf-8 -*-
"""
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

import datetime
import logging

from tg import expose, require, request, redirect, validate, abort
from tg import tmpl_context

from tg.predicates import Any

from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch
from hollyrosa.model.booking_couch import getBookingDays, getAllBookingDays, getVisitingGroupsInDatePeriod

from formencode import validators

from hollyrosa.widgets.forms.edit_booking_day_form import create_edit_booking_day_form

from hollyrosa.controllers.common import has_level, ensurePostRequest, getDateObject, cleanHtml
from hollyrosa.controllers import common_couch

log = logging.getLogger(__name__)

__all__ = ['Calendar']


class Calendar(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    @expose('hollyrosa.templates.calendar.calendar_overview')
    def overview_all(self):
        """Show an overview of all booking days"""
        return dict(booking_days=[b.doc for b in getAllBookingDays(getHollyCouch())], makeDate=getDateObject)

    @expose('hollyrosa.templates.calendar.calendar_overview')
    def overview(self):
        """Show an overview of all booking days"""
        today = datetime.date.today().strftime('%Y-%m-%d')

        return dict(booking_days=[b.doc for b in getBookingDays(getHollyCouch(), from_date=today)],
                    makeDate=getDateObject)

    @require(
        Any(has_level('staff'), has_level('viewer'), msg='Only staff and viewers may look at the upcoming calendar'))
    @expose('hollyrosa.templates.calendar.calendar_upcoming')
    def upcoming(self):
        """Show an overview of all booking days"""

        today_date_str = datetime.date.today().strftime('%Y-%m-%d')
        end_date_str = (datetime.date.today() + datetime.timedelta(5)).strftime('%Y-%m-%d')

        booking_days = getBookingDays(getHollyCouch(), from_date=today_date_str, to_date=end_date_str)

        # TODO: fix view later.  get_visiting_groups(from_date=today_date_str,  to_date=end_date_str)
        vgroups = getVisitingGroupsInDatePeriod(getHollyCouch(), today_date_str, end_date_str)

        group_info = dict()
        bdays = list()
        for tmp in booking_days:
            b_day = tmp.doc
            tmp_date_today_str = b_day['date']
            bdays.append(b_day)

            group_info[tmp_date_today_str] = dict(
                arrives=[v.doc for v in vgroups if v.doc.get('from_date', '') == tmp_date_today_str],
                leaves=[v.doc for v in vgroups if v.doc.get('to_date', '') == tmp_date_today_str],
                stays=[v.doc for v in vgroups if
                       v.doc.get('to_date', '') > tmp_date_today_str > v.doc.get('from_date', '')])

        return dict(booking_days=bdays, group_info=group_info, makeDate=getDateObject)

    @expose('hollyrosa.templates.calendar.booking_day_properties')
    @validate(validators={'booking_day_id': validators.Int(not_empty=True)})
    @require(Any(has_level('staff'), has_level('pl'), msg='Only staff members may change booking day properties'))
    def edit_booking_day(self, booking_day_id=None, **kw):
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)
        if 'title' not in booking_day:
            booking_day['title'] = ''
        booking_day['recid'] = booking_day['_id']
        tmpl_context.form = create_edit_booking_day_form
        return dict(booking_day=booking_day, usage='edit')

    @expose()
    @require(Any(has_level('staff'), has_level('viewer'), msg='Only staff members may change booking day properties'))
    @validate({"recid": validators.UnicodeString(not_empty=True), "note": validators.UnicodeString,
               "title": validators.UnicodeString, "num_program_crew_members": validators.Int,
               "num_fladan_crew_members": validators.Int})
    def save_booking_day_properties(self,
                                    recid=None,
                                    note='',
                                    title='',
                                    num_program_crew_members=0,
                                    num_fladan_crew_members=0):
        ensurePostRequest(request, __name__)
        booking_day_c = common_couch.getBookingDay(getHollyCouch(), recid)
        booking_day_c['note'] = cleanHtml(note if note is not None else '')
        booking_day_c['title'] = title
        booking_day_c['num_program_crew_members'] = num_program_crew_members
        booking_day_c['num_fladan_crew_members'] = num_fladan_crew_members
        getHollyCouch()[recid] = booking_day_c

        raise redirect('/booking/day?booking_day_id=' + str(recid))
