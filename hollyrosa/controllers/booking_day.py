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


Documentation pointers:
http://turbogears.org/2.0/docs/toc.html
http://turbogears.org/2.0/docs/main/ToscaWidgets/forms.html
http://blog.vrplumber.com/index.php?/archives/2381-ToscaWidgets-JQuery-and-TinyMCE-Tutorialish-ly.html
http://turbogears.org/2.0/docs/main/Auth/Authorization.html#module-repoze.what.predicates

"""

import datetime
import json
import logging
import functools

from tg import expose, flash, require, url, request, redirect, validate, override_template, abort, tmpl_context
import webob

from tg.predicates import Any, is_user
from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch, genUID
from hollyrosa.model.booking_couch import getAllBookingDays, getSlotAndActivityIdOfBooking, \
    getBookingDayOfDate, dateRange2, getBookingDayOfDateList, getSlotRowSchemaOfActivity, \
    getActivityGroupNameAndIdList
from hollyrosa.model.booking_couch import getAllHistoryForBookings, getAllActivities, getAllRooms, \
    getVisitingGroupsAtDate, getUserNameMap, getSchemaSlotActivityMap, getAllVisitingGroups, getActivityTitleMap, \
    getVisitingGroupOfVisitingGroupName

from formencode import validators

# ...this can later be moved to the VisitingGroup module whenever it is broken out

from hollyrosa.widgets.forms.edit_new_booking_request import create_edit_new_booking_request_form
from hollyrosa.widgets.forms.edit_book_slot_form import create_edit_book_slot_form
from hollyrosa.widgets.forms.edit_book_live_slot_form import create_edit_book_live_slot_form
from hollyrosa.widgets.forms.move_booking_form import create_move_booking_form

from hollyrosa.controllers.booking_history import remember_schedule_booking, \
    remember_unschedule_booking, remember_book_slot, remember_booking_properties_change, remember_new_booking_request, \
    remember_booking_request_change, remember_delete_booking_request, remember_block_slot, remember_unblock_slot, \
    remember_booking_move, remember_ignore_booking_warning

from hollyrosa.controllers.common import DataContainer, workflow_map, getLoggedInUserId, change_op_map, \
    getRenderContent, getRenderContentDict, computeCacheContent, has_level, reFormatDate, getSanitizeDate
from hollyrosa.controllers import common_couch

log = logging.getLogger(__name__)

__all__ = ['BookingDay']


def deleteBooking(holly_couch, booking_o):
    booking_o['booking_state'] = -100
    booking_o['booking_day_id'] = ''
    booking_o['slot_id'] = ''
    holly_couch[booking_o['_id']] = booking_o


def make_booking_day_activity_anchor(tmp_activity_id):
    return '#activity_row_id_' + tmp_activity_id


def getNextBookingDayId(holly_couch, booking_day):
    # TODO: relly needs refactoring
    this_date = booking_day['date']  # make date from string, but HOW?
    next_date = (datetime.datetime.strptime(this_date, '%Y-%m-%d') + datetime.timedelta(1)).strftime('%Y-%m-%d')

    bdays = holly_couch.view('booking_day/all_booking_days', keys=[next_date], include_docs=True)
    bdays2 = [b for b in bdays]
    return bdays2[0].value


def ensurePostRequest(request, name=''):
    """
    The purpose of this little method is to ensure that the controller was called with appropriate HTTP verb.
    """
    if not request.method == 'POST':
        raise webob.exc.HTTPMethodNotAllowed(
            comment='The method %s you tried to reached through TG2 object dispatch is only accepting POST requests. Most probable there is some old code still calling GET.' % str(
                name))


class BookingDay(BaseController):
    """
    The fallback controller for hollyrosa.

    By default, the final controller tried to fulfill the request
    when no other routes match. It may be used to display a template
    when all else fails, e.g.::

        def view(self, url):
            return render('/%s' % url)

    Or if you're using Mako and want to explicitly send a 404 (Not
    Found) response code when the requested template doesn't exist::

        import mako.exceptions

        def view(self, url):
            try:
                return render('/%s' % url)
            except mako.exceptions.TopLevelLookupException:
                abort(404)

    """

    def getAllDays(self):
        # TODO maybe stop caching and have a tuned view instead?
        try:
            tmp = self._all_days
        except AttributeError:
            all_days_c = getAllBookingDays(getHollyCouch())
            self._all_days = [DataContainer(id=d.key, date=d.value) for d in all_days_c]
            tmp = self._all_days

        return tmp

    def getActivitySlotPositionsMap(self, day_schema):
        """what do we map?"""
        try:
            tmp = self._activity_slot_position_map
        except AttributeError:
            self._activity_slot_position_map = day_schema['schema']
            tmp = self._activity_slot_position_map

        return tmp

    def fn_cmp_slot_row(self, a, b):
        return a.zorder - b.zorder #cmp(a.zorder, b.zorder)

    def getActivitiesMap(self, activities):
        """given a view from couchdb of activities, make a map/dict"""
        activities_map = dict()
        for a in activities:
            activities_map[a.doc['_id']] = a.doc
        return activities_map

    def make_slot_rows__of_day_schema(self, day_schema, activities_map, dates):
        if not isinstance(dates, list):
            dates = [dates]

        slot_row_schema = day_schema['schema']
        booking_days = [x.doc for x in getBookingDayOfDateList(getHollyCouch(), dates)]
        slot_rows = list()

        for tmp_activity_id, tmp_slots in slot_row_schema.items():
            tmp_activity = activities_map[tmp_activity_id]

            tmp_row = DataContainer(activity_id=tmp_activity_id, zorder=tmp_slots[0]['zorder'],
                                    title=tmp_activity['title'], activity_group_id=tmp_activity['activity_group_id'],
                                    bg_color=tmp_activity['bg_color'], capacity=tmp_activity['capacity'])

            tmp_row.slot_row_position = []
            for tmp_day in booking_days:  # te in dates:
                tmp_date = tmp_day['date']
                bdayid = tmp_day['_id']
                for s in tmp_slots[1:]:
                    tmp_row.slot_row_position.append(
                        DataContainer(id=str(s['slot_id']), time_from=s['time_from'], time_to=s['time_to'],
                                      duration=s['duration'], date=tmp_date, booking_day_id=bdayid))

            slot_rows.append(tmp_row)

        slot_rows.sort(key=functools.cmp_to_key(self.fn_cmp_slot_row))
        return slot_rows

    def getNonDeletedBookingsForBookingDay(self, holly_couch, day_id):
        # TODO refactor out view
        bookings_c = holly_couch.view('booking_day/non_deleted_bookings_of_booking_day', keys=[day_id])

        # TODO: optimize away this dict thing
        bookings = dict()
        for x in bookings_c:
            b = x.value
            new_booking = DataContainer(id=b['_id'], content=b['content'], cache_content=b['cache_content'],
                                        booking_state=b['booking_state'], visiting_group_id=b['visiting_group_id'],
                                        visiting_group_name=b['visiting_group_name'],
                                        valid_from=b.get('valid_from', ''), valid_to=b.get('valid_to', ''),
                                        requested_date=b.get('requested_date', ''),
                                        last_changed_by_id=b['last_changed_by_id'], slot_id=b['slot_id'])
            ns = bookings.get(new_booking.slot_id, list())
            ns.append(new_booking)
            bookings[new_booking.slot_id] = ns

        return bookings

    def getNonDeletedRoomBookingsForBookingDay(self, holly_couch, start_date, end_date, schema_subtype='room'):
        # TODO refactor out view
        # this is a modified copy of getNonDeletedBookingsForBookingDay
        view_name_map = dict(room='booking_day_live/non_deleted_room_bookings_of_booking_day',
                             staff='booking_day_live/non_deleted_staff_bookings_of_booking_day')
        view_name = view_name_map[schema_subtype]
        bookings_c = holly_couch.view(view_name, startkey=[start_date, ''], endkey=[end_date, 'zzzzzzzzz'])

        # TODO: optimize away this dict thing
        bookings = dict()
        for x in bookings_c:
            b = x.value
            new_booking = DataContainer(id=b['_id'], content=b['content'], cache_content=b['cache_content'],
                                        booking_state=b['booking_state'], visiting_group_id=b['visiting_group_id'],
                                        visiting_group_name=b['visiting_group_name'],
                                        valid_from=b.get('valid_from', ''), valid_to=b.get('valid_to', ''),
                                        requested_date=b.get('requested_date', ''),
                                        last_changed_by_id=b['last_changed_by_id'],
                                        slot_id=x.key[1], date=x.key[0])
            ns = bookings.get(new_booking.slot_id, list())
            ns.append(new_booking)
            bookings[new_booking.slot_id] = ns

        return bookings

    def getSlotStateOfBookingDayIdAndSlotId(self, holly_couch, booking_day_id, slot_id):
        return [s for s in
                holly_couch.view('booking_day/slot_states', keys=[[booking_day_id, slot_id]], include_docs=True)]

    def getSlotBlockingsForBookingDay(self, holly_couch, day_id):
        # todo refactor
        blockings_map = dict()
        for x in holly_couch.view("booking_day/slot_state_of_booking_day", keys=[day_id]):
            b = x.value
            # TODO: replace hack later. slot_id. and slot.
            blockings_map[b['slot_id']] = DataContainer(level=b['level'], booking_day_id=b['booking_day_id'],
                                                        slot_id=b['slot_id'])

        return blockings_map

    def getUnscheduledProgramBookingsForToday(self, holly_couch, date, activity_map, subtype='program'):
        """
        Get a list of all unscheduled program bookings for a given day
        """

        # need to convert 2011-10-01 to something like Fri Aug 05 2011
        # TODO: refactor
        tmp_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        tmp_date_f = tmp_date.strftime("%a %b %d %Y")

        log.debug('getUnscheduledProgramBookingsForToday() - %s , %s (subtype %s)' % (date, tmp_date_f, subtype))

        # TODO: need refactoring, add subtype component too
        unscheduled_bookings_c = holly_couch.view('booking_day/unscheduled_bookings_by_date', key=[tmp_date_f, subtype],
                                                  descending=True)

        # ...somehow convert all unscheduled bookings to a list form that can be returned
        unscheduled_bookings = list()
        for x in unscheduled_bookings_c:
            b = x.value
            a_id = b['activity_id']

            # ...TODO note that it is possible an unscheduled booking doesent belong to room or live (might be program)
            if a_id in activity_map:
                a = activity_map[a_id]

                # TODO: remove DataContainer here (will break templates)
                new_booking = DataContainer(id=b['_id'], content=b['content'], cache_content=b['cache_content'],
                                            booking_state=b['booking_state'], visiting_group_id=b['visiting_group_id'],
                                            visiting_group_name=b['visiting_group_name'], valid_from=b['valid_from'],
                                            valid_to=b['valid_to'], requested_date=b['requested_date'],
                                            last_changed_by_id=b['last_changed_by_id'], slot_id=b['slot_id'],
                                            activity_title=a['title'], activity_group_id=a['activity_group_id'],
                                            activity_id=a_id)
                unscheduled_bookings.append(new_booking)

        return unscheduled_bookings

    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    def getSumNumberOfRequiredCrewMembers(self, slots, slot_rows):
        """compute required number of program crew members, fladan crew members"""
        crew_count = dict()
        crew_count['program_count'] = 0
        crew_count['fladan_count'] = 0

        for x in slots:
            ac = x.slot_row_position.slot_row.activity
            if 4 == ac.activity_group_id:
                crew_count['fladan_count'] += ac.guides_per_slot
            else:
                crew_count['program_count'] += ac.guides_per_slot

        # ...now we can also compute roughly the number of guids per slot row:
        for x in slot_rows:
            ac = x.activity
            if 4 == ac.activity_group_id:
                crew_count['fladan_count'] += ac.guides_per_day
            else:
                crew_count['program_count'] += ac.guides_per_day

        return crew_count

    @expose('hollyrosa.templates.booking_day')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view a booking day'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=False),
                          'day': validators.DateValidator(not_empty=False),
                          'subtype': validators.UnicodeString(not_empty=False)})
    def day(self, day=None, booking_day_id=None, subtype=None):
        """Show a complete booking day"""

        # TODO: we really need to get only the slot rows related to our booking day schema or things will
        #  go wrong at some point when we have more than one schema to work with.

        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
        activities_map = self.getActivitiesMap(getAllActivities(getHollyCouch()))

        if booking_day_id is not None and booking_day_id != '':
            booking_day_o = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

        elif day == 'today':
            booking_day_o = getBookingDayOfDate(getHollyCouch(), today_sql_date)
            booking_day_id = booking_day_o['_id']

        else:
            booking_day_o = getBookingDayOfDate(getHollyCouch(), str(day))
            booking_day_id = booking_day_o['_id']

        #  TODO: fix row below
        booking_day_o['id'] = booking_day_id

        day_schema_id = booking_day_o['day_schema_id']
        day_schema = common_couch.getDaySchema(getHollyCouch(), day_schema_id)

        slot_rows = self.make_slot_rows__of_day_schema(day_schema, activities_map, dates=[booking_day_o['date']])

        # ...first, get booking_day for today
        new_bookings = self.getNonDeletedBookingsForBookingDay(getHollyCouch(), booking_day_id)

        # ...we need a mapping from activity to a list / tupple slot_row_position
        #
        #   the new version should be a list of rows. Each row is either a DataContainer or a
        #   dict (basically the same...)
        #  We need to know activity name, color, id and group (which we get from the activities) and we
        #  need a list of slot positions
        activity_slot_position_map = self.getActivitySlotPositionsMap(day_schema)

        # ...find all unscheduled bookings
        showing_sql_date = str(booking_day_o['date'])
        unscheduled_bookings = self.getUnscheduledProgramBookingsForToday(getHollyCouch(), showing_sql_date,
                                                                          activities_map)

        # ...compute all blockings, create a dict mapping slot_row_position_id to actual state
        blockings_map = self.getSlotBlockingsForBookingDay(getHollyCouch(), booking_day_id)
        days = self.getAllDays()

        activity_groups = getActivityGroupNameAndIdList(getHollyCouch(), day_schema)
        return dict(booking_day=booking_day_o, slot_rows=slot_rows, bookings=new_bookings,
                    unscheduled_bookings=unscheduled_bookings, activity_slot_position_map=activity_slot_position_map,
                    blockings_map=blockings_map, workflow_map=workflow_map, days=days,
                    getRenderContent=getRenderContent, activity_groups=activity_groups, reFormatDate=reFormatDate)

    @expose('hollyrosa.templates.live_day')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view a booking day'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=False),
                          'day': validators.DateValidator(not_empty=False),
                          'subtype': validators.UnicodeString(not_empty=True)})
    def live(self, day=None, booking_day_id=None, subtype=u'room'):
        """Show a complete booking day for room or staff"""
        # TODO: rename from live to room
        # TODO: we really need to get only the slot rows related to our booking day schema or things
        #  will go wrong at some point when we have more than one schema to work with.

        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")
        activities_map = self.getActivitiesMap(getAllRooms(getHollyCouch()))

        if booking_day_id is not None and booking_day_id != "":
            booking_day_o = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

        elif day == 'today':

            booking_day_o = getBookingDayOfDate(getHollyCouch(), today_sql_date)
            booking_day_id = booking_day_o['_id']

        else:
            booking_day_o = getBookingDayOfDate(getHollyCouch(), str(day))
            booking_day_id = booking_day_o['_id']

        #  TODO: fix row below
        booking_day_o['id'] = booking_day_id

        # ...trying to find all days, lets say seven days after the indicated day
        first_date = booking_day_o['date']
        dates = dateRange2(first_date, 7)
        headers = []
        for tmp_date in dates:
            headers.append('FM (%s)' % tmp_date)
            headers.append('EM (%s)' % tmp_date)

        # ...we also need a list of booking days in order to fill in all slots
        booking_o_list = []
        for tmp_date in dates:
            booking_o_list.append(getBookingDayOfDate(getHollyCouch(), str(tmp_date)))

        # ...we have to assume all days belong to the same day schema, otherwise, we really shouldnt display that day
        schema_type = self.getSchemaSubNameOfSubtype(subtype)
        schema_id = booking_day_o[schema_type]
        schema = common_couch.getDaySchema(getHollyCouch(), schema_id)
        title_hint = schema['title_hint']

        slot_rows = self.make_slot_rows__of_day_schema(schema, activities_map, dates=dates)

        # ...first, get booking_day for today
        all_bookings = dict()
        all_blockings = dict()

        for tmp_date in dates:
            # TODO: ...too many lookups here
            tmp_booking_day_o = getBookingDayOfDate(getHollyCouch(), tmp_date)
            tmp_day_id = tmp_booking_day_o['_id']
            tmp_bookings = self.getNonDeletedRoomBookingsForBookingDay(getHollyCouch(), tmp_date, tmp_date,
                                                                       schema_subtype=subtype)
            tmp_blockings = self.getSlotBlockingsForBookingDay(getHollyCouch(), tmp_day_id)
            for k, v in tmp_bookings.items():
                new_k = (str(tmp_date), str(k))  # change to day id later
                all_bookings[new_k] = v
            for k, v in tmp_blockings.items():
                new_k = (str(tmp_date), str(k))  # change to day id later
                all_blockings[new_k] = v

        # TODO: need a map for bookings that not only looks at slot_id but also on date. Thats a combined key.

        # ...we need a mapping from activity to a list / tupple slot_row_position
        #
        # the new version should be a list of rows. Each row is either a DataContainer or a dict (basically the
        # same...) We need to know activity name, color, id and group (which we get from the activities) and we need
        # a list of slot positions
        activity_slot_position_map = self.getActivitySlotPositionsMap(schema)

        # ...find all unscheduled bookings
        showing_sql_date = str(booking_day_o['date'])

        # TODO need to show for the whole date range
        unscheduled_bookings = self.getUnscheduledProgramBookingsForToday(getHollyCouch(), showing_sql_date,
                                                                          activities_map)

        # ...compute all blockings, create a dict mapping slot_row_position_id to actual state
        # TODO need to show blockings for whole date range

        days = self.getAllDays()
        activity_groups = getActivityGroupNameAndIdList(getHollyCouch(), schema)
        return dict(booking_day=booking_day_o, slot_rows=slot_rows, bookings=all_bookings,
                    unscheduled_bookings=unscheduled_bookings, activity_slot_position_map=activity_slot_position_map,
                    blockings_map=all_blockings, workflow_map=workflow_map, days=days,
                    getRenderContent=getRenderContent, activity_groups=activity_groups, headers=headers,
                    reFormatDate=reFormatDate, title_hint=title_hint, schema_subtype=subtype)

    @expose('hollyrosa.templates.booking_day_fladan')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view a booking day'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=False),
                          'date': validators.DateValidator(not_empty=False),
                          'ag': validators.UnicodeString(not_empty=False)})
    def fladan_day(self, date=None, booking_day_id=None, ag=''):
        """Show a complete booking day"""

        # TODO: move to common
        workflow_img_mapping = {'0': 'sheep.png', '10': 'paper_to_sign.png', '20': 'check_mark.png', '-10': 'alert.png',
                                '-100': 'alert.png', 'unscheduled': 'alert.png'}

        today_sql_date = datetime.datetime.today().date().strftime("%Y-%m-%d")

        activities_map = self.getActivitiesMap(getAllActivities(getHollyCouch()))

        if booking_day_id is not None and booking_day_id != '':
            booking_day_o = getBookingDay(getHollyCouch(), booking_day_id)

        else:
            the_day = str(date)
            booking_day_o = getBookingDayOfDate(getHollyCouch(), the_day)
            booking_day_id = booking_day_o['_id']

        #  TODO: fix row below
        booking_day_o['id'] = booking_day_id

        day_schema_id = booking_day_o['day_schema_id']
        day_schema = common_couch.getCouchDBDocument(getHollyCouch(), day_schema_id, 'day_schema')

        if ag != '':
            tmp_ag = common_couch.getCouchDBDocument(getHollyCouch(), ag, 'activity_group')
            ag_title = tmp_ag['title']  # getHollyCouch()[ag]['title']
            slot_rows = [sr for sr in
                         self.make_slot_rows__of_day_schema(day_schema, activities_map, booking_day_o['date']) if
                         sr.activity_group_id == ag]
        else:
            ag_title = 'All'
            slot_rows = self.make_slot_rows__of_day_schema(day_schema, activities_map, booking_day_o['date'])

        activity_slot_position_map = self.getActivitySlotPositionsMap(day_schema)

        new_bookings = self.getNonDeletedBookingsForBookingDay(getHollyCouch(), booking_day_id)
        blockings_map = self.getSlotBlockingsForBookingDay(getHollyCouch(), booking_day_id)

        return dict(booking_day=booking_day_o, slot_rows=slot_rows, bookings=new_bookings,
                    activity_slot_position_map=activity_slot_position_map, blockings_map=blockings_map,
                    workflow_map=workflow_map, activity_group=ag, workflow_img_mapping=workflow_img_mapping,
                    ag_title=ag_title, reFormatDate=reFormatDate)

    @expose()
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL may delete a booking request'))
    @validate(validators={'return_to_day_id': validators.UnicodeString(not_empty=True),
                          'booking_id': validators.UnicodeString(not_empty=True)})
    def delete_booking(self, return_to_day_id=None, booking_id=None):
        ensurePostRequest(request, __name__)
        tmp_booking = common_couch.getBooking(getHollyCouch(), booking_id)
        tmp_activity_id = tmp_booking['activity_id']
        remember_delete_booking_request(getHollyCouch(), booking=tmp_booking, changed_by='',
                                        activity_title=common_couch.getActivity(getHollyCouch(), tmp_activity_id)[
                                            'title'])

        subtype = tmp_booking['subtype']

        deleteBooking(getHollyCouch(), tmp_booking)

        redirect_map = dict(room='live', program='day', staff='live')
        # TODO Redirect to live or day ?
        raise redirect('/booking/%s?booking_day_id=%s&subtype=%s' % (
            redirect_map[subtype], str(return_to_day_id), subtype + make_booking_day_activity_anchor(tmp_activity_id)))

    def getBookingDayDate(self, booking_day_id):
        return common_couch.getBookingDay(getHollyCouch(), booking_day_id)['date']

    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may unschedule booking request'))
    @validate({"return_to_day_id": validators.UnicodeString, "booking_id": validators.UnicodeString(not_empty=True)})
    def unschedule_booking(self, return_to_day_id=None, booking_id=None):
        ensurePostRequest(request, __name__)
        b = common_couch.getBooking(getHollyCouch(), booking_id)
        b['last_changed_by_id'] = getLoggedInUserId(request)
        b['booking_state'] = 0
        old_booking_day_id = b['booking_day_id']
        old_slot_id = b['slot_id']
        b['booking_day_id'] = ''
        b['slot_id'] = ''

        # ...fix if valid_from , valid_to and requested date is None

        try:
            datetime.datetime.strptime(b['valid_from'], "%Y-%m-%d")
        except ValueError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['valid_from'] = date
        except TypeError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['valid_from'] = date
        except KeyError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['valid_from'] = date

        try:
            datetime.datetime.strptime(b['valid_to'], "%Y-%m-%d")
        except ValueError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['valid_to'] = date
        except TypeError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['valid_to'] = date
        except KeyError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['valid_to'] = date

        try:
            datetime.datetime.strptime(b['requested_date'], "%Y-%m-%d")
        except ValueError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['requested_date'] = date
        except TypeError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['requested_date'] = date
        except KeyError:
            date = self.getBookingDayDate(old_booking_day_id)
            b['requested_date'] = date

        b['hide_warn_on_suspect_booking'] = False  # TODO: refactor

        # TODO: refactor and safen
        getHollyCouch()[b['_id']] = b

        booking_day = common_couch.getBookingDay(getHollyCouch(), old_booking_day_id)
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype='program')
        slot = slot_map[old_slot_id]
        activity = common_couch.getActivity(getHollyCouch(), b['activity_id'])

        remember_unschedule_booking(getHollyCouch(), booking=b, slot_row_position=slot, booking_day=booking_day,
                                    changed_by='', activity=activity)

        raise redirect('day?booking_day_id=' + return_to_day_id + make_booking_day_activity_anchor(b['activity_id']))

    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may schedule booking request'))
    @validate({"return_to_day_id": validators.UnicodeString, "booking_id": validators.UnicodeString(not_empty=True),
               "booking_day_id": validators.UnicodeString(not_empty=True),
               "slot_row_position_id": validators.UnicodeString(not_empty=True)})
    def schedule_booking(self, return_to_day_id=None, booking_id=None, booking_day_id=None, slot_row_position_id=None):
        # TODO: ensure we do not have a GET request here (necessary at the momen)
        b = common_couch.getBooking(getHollyCouch(), booking_id)
        if '' != b['booking_day_id']:
            abort(500)
        b['last_changed_by_id'] = getLoggedInUserId(request)
        b['booking_day_id'] = booking_day_id
        b['slot_id'] = slot_row_position_id
        b['hide_warn_on_suspect_booking'] = False
        activity = common_couch.getActivity(getHollyCouch(), b['activity_id'])

        # TODO: check that activity ids match
        b['booking_state'] = activity['default_booking_state']

        # TODO: check save
        getHollyCouch()[b['_id']] = b
        booking_day = common_couch.getBookingDay(getHollyCouch(), b['booking_day_id'])
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype='program')
        slot = slot_map[slot_row_position_id]

        # ...TODO: have all lookuped data in some local ctx that can be passed on to all helper functions so we dont
        #  have to do a lot of re-lookups
        remember_schedule_booking(getHollyCouch(), booking=b, slot_row_position=slot, booking_day=booking_day,
                                  activity=activity)

        if return_to_day_id == None or return_to_day_id == '':
            return_to_day_id = booking_day_id
        raise redirect('day?booking_day_id=' + return_to_day_id + make_booking_day_activity_anchor(b['activity_id']))

    @expose('hollyrosa.templates.booking.edit_booked')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may book a slot'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=True),
                          'slot_id': validators.UnicodeString(not_empty=True),
                          'subtype': validators.UnicodeString(not_empty=False)})
    def book_slot(self, booking_day_id=None, slot_id=None, subtype='program'):
        tmpl_context.form = create_edit_book_slot_form

        ensurePostRequest(request, __name__)
        # ...find booking day and booking row
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

        tmp_visiting_groups = getVisitingGroupsAtDate(getHollyCouch(), booking_day['date'])
        visiting_groups = [(e.doc['_id'], e.doc['name']) for e in tmp_visiting_groups]

        # ...find out activity of slot_id for booking_day
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=subtype)
        slot = slot_map[slot_id]
        activity = common_couch.getActivity(getHollyCouch(), slot['activity_id'])
        booking_o = dict(content='', visiting_group_id='', visiting_group_name='', valid_from=None, valid_to=None,
                         requested_date=None, return_to_day_id=booking_day_id, activity_id=slot['activity_id'], id=None,
                         activity=activity, booking_day_id=booking_day_id, slot_id=slot_id)
        visiting_group_options = json.dumps([dict(name=a[1], id=a[0]) for a in visiting_groups])
        return dict(booking_day=booking_day, booking=booking_o, visiting_groups=visiting_groups,
                    edit_this_visiting_group=0, slot_position=slot, visiting_group_options=visiting_group_options)

    def getEndSlotIdOptions(self, living_schema_id, activity_id):
        slot_row_schema = getSlotRowSchemaOfActivity(getHollyCouch(), living_schema_id, activity_id)

        end_slot_id_options = []

        for t in slot_row_schema:
            for slot in t.value[1:]:
                end_slot_id_options.append((slot['slot_id'], slot['title']))
        return end_slot_id_options

    @expose('hollyrosa.templates.booking.edit_booked_live')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may book a slot'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=True),
                          'slot_id': validators.UnicodeString(not_empty=True),
                          'subtype': validators.UnicodeString(not_empty=False, default='room')})
    def book_live_slot(self, booking_day_id=None, slot_id=None, subtype='room'):
        tmpl_context.form = create_edit_book_live_slot_form

        log.debug("book_live_slot()")

        ensurePostRequest(request, __name__)

        validation_status = request.validation
        log.debug(str(validation_status))
        log.debug(dir(validation_status))
        log.debug("validation errors: " + str(validation_status.errors))
        log.debug("values: " + str(validation_status.values))

        if subtype not in ['program', 'room', 'staff']:
            raise ValueError('subtype %s not among valid choices' % subtype)

        # ...find booking day and booking row
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

        # ...TODO: only list visiting groups that lives indoors. That means they have a non-zero entry in the live
        #  sheet in the indoor column.
        tmp_visiting_groups = getVisitingGroupsAtDate(getHollyCouch(), booking_day['date'])
        visiting_groups = [(e.doc['_id'], e.doc['name']) for e in tmp_visiting_groups]

        # ...find out activity of slot_id for booking_day
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=subtype)
        slot = slot_map[slot_id]
        activity = common_couch.getActivity(getHollyCouch(), slot['activity_id'])

        # ...TODO: also extract the whole slot_row from the schema and remove the first entry. This will be needed
        #  for the date range to work correctly
        new_clean_booking = dict(booking_content='', visiting_group_id='', visiting_group_name='',
                                 visiting_group_displayname='', return_to_day_id=booking_day_id, valid_from=None,
                                 valid_to=None, requested_date=None, activity_id=slot['activity_id'], id=None,
                                 activity=activity, booking_day_id=booking_day_id, slot_id=slot_id, booking_id=None,
                                 subtype=subtype)

        # ...adapt date to datetime dates
        tmp_booking_date_ok, tmp_booking_date = getSanitizeDate(booking_day['date'])
        if tmp_booking_date_ok:
            new_clean_booking['booking_date'] = tmp_booking_date
            new_clean_booking['booking_end_date'] = tmp_booking_date

        schema_id = self.getSchemaSubNameOfSubtype(subtype)
        schema_o = booking_day[schema_id]

        end_slot_id_options_o = self.getEndSlotIdOptions(schema_o, slot['activity_id'])
        new_clean_booking['booking_end_slot_id'] = (end_slot_id_options_o[0][0], end_slot_id_options_o)
        end_slot_id_options = json.dumps(end_slot_id_options_o)
        start_slot_id_options = end_slot_id_options

        visiting_group_options = json.dumps([dict(name=a[1], id=a[0]) for a in visiting_groups])

        # ...modify singel select field
        return dict(booking=new_clean_booking, booking_day=booking_day, visiting_groups=visiting_groups,
                    edit_this_visiting_group=0, slot_position=slot, start_slot_id_options=start_slot_id_options,
                    end_slot_id_options=end_slot_id_options, visiting_group_options=visiting_group_options)

    @expose('hollyrosa.templates.booking.view')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may change booked booking properties'))
    @validate(validators={'booking_id': validators.UnicodeString(not_empty=True),
                          'return_to_day_id': validators.UnicodeString(not_empty=False)})
    def view_booked_booking(self, return_to_day_id=None, booking_id=None):

        # TODO: does it work with both kinds of bookings?

        # ...find booking day and booking row
        booking_o = common_couch.getBooking(getHollyCouch(), booking_id)
        booking_o.return_to_day_id = return_to_day_id
        activity_id = booking_o['activity_id']

        booking_day_id = None
        booking_day = None
        slot_position = None

        if 'booking_day_id' in booking_o:
            booking_day_id = booking_o['booking_day_id']
            if '' != booking_day_id:
                booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

                slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=booking_o['subtype'])
                slot_id = booking_o['slot_id']
                slot_position = slot_map[slot_id]

        activity = common_couch.getActivity(getHollyCouch(), activity_id)
        history = [h.doc for h in getAllHistoryForBookings(getHollyCouch(), [booking_id])]
        user_name_map = getUserNameMap(getHollyCouch())

        end_slot = None
        if 'booking_end_slot_id' in booking_o:
            end_slot = slot_map[booking_o['booking_end_slot_id']]

        return dict(booking_day=booking_day, slot_position=slot_position, booking=booking_o, workflow_map=workflow_map,
                    history=history, change_op_map=change_op_map, getRenderContent=getRenderContentDict,
                    activity=activity, formatDate=reFormatDate, user_name_map=user_name_map, end_slot=end_slot)

    def getSchemaSubNameOfSubtype(self, subtype):
        """
        For now, we only know about room and staff subtype. staff is for staff planning, room is for room planning.
        Live planning is bigger, it inlcudes not only rooms but all fields etc and is out of scope right now.
        """
        schema_id_map = dict(room='room_schema_id', staff='staff_schema_id', program='day_schema_id')
        return schema_id_map[subtype]

    def getSchemaIdOfBooking(self, a_booking):
        return self.getSchemaSubNameOfSubtype(a_booking['subtype'])

    @expose('hollyrosa.templates.booking.edit_booked')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may change booked booking properties'))
    @validate(validators={'id': validators.UnicodeString(not_empty=True),
                          'return_to_day': validators.UnicodeString(not_empty=False)})
    def edit_booked_booking(self, return_to_day_id=None, booking_id=None, **kw):
        # TODO: subtype should be what kind of booking,
        # TODO: then there should be a schema_type explaining what schema the booking belongs to.
        # ...find booking day and booking row
        booking_o = common_couch.getBooking(getHollyCouch(), booking_id)
        subtype = booking_o['subtype']
        if subtype == 'program':
            tmpl_context.form = create_edit_book_slot_form
        elif booking_o['subtype'] in ['room', 'staff']:
            tmpl_context.form = create_edit_book_live_slot_form

            # TODO: find out how to express this
            template = 'kajiki:hollyrosa.templates.edit_booked_live_booking'
            override_template(self.edit_booked_booking, template)

        booking_o['return_to_day_id'] = return_to_day_id

        booking_day_id = booking_o['booking_day_id']
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)
        slot_id = booking_o['slot_id']
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=subtype)
        slot_position = slot_map[slot_id]
        activity_id = booking_o['activity_id']
        activity = common_couch.getActivity(getHollyCouch(), activity_id)
        booking_ = dict(activity_id=activity_id, slot_id=slot_id, activity=activity, id=booking_o['_id'],
                        booking_id=booking_o['_id'], visiting_group_name=booking_o['visiting_group_name'],
                        visiting_group_id=booking_o['visiting_group_id'], booking_content=booking_o['content'],
                        booking_end_slot_id=booking_o.get('booking_end_slot_id', ''), return_to_day_id=return_to_day_id,
                        booking_day_id=return_to_day_id, subtype=subtype)

        tmp_visiting_groups = getVisitingGroupsAtDate(getHollyCouch(), booking_day['date'])
        visiting_groups = [(e.doc['_id'], e.doc['name']) for e in tmp_visiting_groups]

        # ...sanitize dates and convert to date objects
        tmp_booking_date_ok, tmp_booking_date = getSanitizeDate(
            booking_o.get('booking_date', '2013-07-24'))  # TODO: what should the dates be in the default case ???
        if tmp_booking_date_ok:
            booking_['booking_date'] = tmp_booking_date

        tmp_booking_end_date_ok, tmp_booking_end_date = getSanitizeDate(booking_o.get('booking_end_date', '2013-07-24'),
                                                                        datetime.datetime.now())

        # TODO: what should the dates be in the default case ???

        if tmp_booking_end_date_ok:
            booking_['booking_end_date'] = tmp_booking_end_date

        end_slot_id_options = json.dumps(
            self.getEndSlotIdOptions(booking_day[self.getSchemaIdOfBooking(booking_o)], slot_position['activity_id']))
        start_slot_id_options = end_slot_id_options

        visiting_group_options = json.dumps([dict(name=a[1], id=a[0]) for a in visiting_groups])
        return dict(booking_day=booking_day, slot_position=slot_position, booking=booking_,
                    visiting_groups=visiting_groups, edit_this_visiting_group=booking_o['visiting_group_id'],
                    activity=activity, start_slot_id_options=start_slot_id_options,
                    end_slot_id_options=end_slot_id_options,
                    living_schema_id=booking_day[self.getSchemaSubNameOfSubtype(subtype)],
                    visiting_group_options=visiting_group_options)

    # TODO: fix subtype, it's not always live, can be funk/staff. Maybe need to be hidden id I think
    # TODO is the error handler right?
    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may change booked live booking properties'))
    @validate({"booking_id": validators.UnicodeString, "booking_content": validators.UnicodeString,
               "visiting_group_name": validators.UnicodeString, "visiting_group_display_name": validators.UnicodeString,
               "visiting_group_id": validators.UnicodeString(not_empty=True),
               "activity_id": validators.UnicodeString(not_empty=True), "return_to_day_id": validators.UnicodeString,
               "slot_id": validators.UnicodeString, "booking_day_id": validators.UnicodeString,
               "booking_date": validators.DateValidator, "booking_end_date": validators.DateConverter,
               "booking_end_slot_id": validators.UnicodeString, "block_after_book": validators.Bool(default=False),
               "subtype": validators.UnicodeString(not_empty=True, default='room')})
    def save_booked_live_booking_properties(self, booking_id=None, booking_content=None, visiting_group_name=None,
                                            visiting_group_display_name=None, visiting_group_id=None, activity_id=None,
                                            return_to_day_id=None, slot_id=None, booking_day_id=None, booking_date=None,
                                            booking_end_date=None, booking_end_slot_id=None, block_after_book=False,
                                            subtype='room', **args):
        # ...This is a new way to try to block GET requests to pages which have a side effect.
        log.debug("save_booked_live_booking_properties()")
        ensurePostRequest(request, name=__name__)

        tmp_activity_id = self._saveBookedBookingPropertiesHelper(booking_id, booking_content,
                                                                  visiting_group_display_name, visiting_group_id,
                                                                  activity_id, return_to_day_id, slot_id,
                                                                  booking_day_id, booking_date=booking_date,
                                                                  block_after_book=block_after_book, subtype=subtype,
                                                                  booking_end_date=booking_end_date,
                                                                  booking_end_slot_id=booking_end_slot_id)
        raise redirect(
            'live?booking_day_id=' + str(return_to_day_id) + '&subtype=' + subtype + make_booking_day_activity_anchor(
                tmp_activity_id))

    @expose()
    @require(Any(is_user('root'), has_level('staff'), msg='Only staff members may change booked booking properties'))
    @validate({"id": validators.UnicodeString, "booking_content": validators.UnicodeString(not_empty=True),
               "visiting_group_display_name": validators.UnicodeString,
               "visiting_group_id": validators.UnicodeString(not_empty=True),
               "activity_id": validators.UnicodeString(not_empty=True), "return_to_day_id": validators.UnicodeString,
               "slot_id": validators.UnicodeString, "booking_day_id": validators.UnicodeString,
               "block_after_book": validators.Bool})
    def save_booked_booking_properties(self, id=None, booking_content=None, visiting_group_display_name=None,
                                       visiting_group_id=None, activity_id=None, return_to_day_id=None, slot_id=None,
                                       booking_day_id=None, block_after_book=False, **kwargs):
        """
        Accepts a form POST (or GET) request to store a booking.

        TODO: What do we do with visiting_group_display_name which is a little bit deprecated at the moment ?
        """

        # ...This is a new way to try to block GET requests to pages which have a side effect.
        ensurePostRequest(request, name=__name__)

        tmp_activity_id = self._saveBookedBookingPropertiesHelper(id, booking_content, visiting_group_display_name,
                                                                  visiting_group_id, activity_id, return_to_day_id,
                                                                  slot_id, booking_day_id,
                                                                  block_after_book=block_after_book, subtype='program')
        raise redirect(
            'day?booking_day_id=' + str(return_to_day_id) + make_booking_day_activity_anchor(tmp_activity_id))

    def _saveBookedBookingPropertiesHelper(self, id=None, content=None, visiting_group_name=None,
                                           visiting_group_id=None, activity_id=None, return_to_day_id=None,
                                           slot_id=None, booking_day_id=None, booking_date=None, block_after_book=False,
                                           subtype='program', booking_end_date='', booking_end_slot_id=''):
        """
        Common method for saving booking properties
        """
        is_new = (id is None or '' == id)
        # ...id can be None if a new slot is booked
        booking_day = None

        # ...there is a big difference on how booking_day_id is handled.
        #   for a program booking, booking day id decides the date but on room bookings (live) it's the opposite.
        #   booking_date determines booking_day_id

        # ...find visiting group and if id doesn't exist it indicates we should use N/A group
        if visiting_group_id == '':
            visiting_group_id = self.getN_A_VisitingGroupId(getHollyCouch())

        vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)

        # ...if new booking
        if is_new:
            old_booking = common_couch.createEmptyProgramBooking(subtype=subtype)

            if subtype in ['room', 'staff']:
                # ...look up booking day by date
                booking_day = getBookingDayOfDate(getHollyCouch(), booking_date)
                booking_day_id = booking_day['_id']
            else:
                booking_day = getHollyCouch()[booking_day_id]

            old_booking['slot_id'] = slot_id
            old_booking['booking_day_id'] = booking_day_id

            if visiting_group_id != '':
                old_booking['valid_from'] = vgroup['from_date']
                old_booking['valid_to'] = vgroup['to_date']

        else:  # saving to existing booking
            old_booking = common_couch.getBooking(getHollyCouch(), id)

            if subtype in ['room', 'staff']:
                # ...change booking_day_id according to booking date
                booking_day = getBookingDayOfDate(getHollyCouch(), booking_date)
                booking_day_id = booking_day['_id']
                old_booking['slot_id'] = slot_id
                old_booking['booking_day_id'] = booking_day_id
            elif subtype == 'program':
                booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

        # ...common for both new and existing bookings as well as program and room bookings
        old_visiting_group_name = old_booking.get('visiting_group_name', '')
        old_booking['visiting_group_name'] = visiting_group_name
        old_booking['visiting_group_id'] = visiting_group_id
        old_booking['last_changed_by_id'] = getLoggedInUserId(request)
        old_booking['content'] = content
        old_booking['cache_content'] = computeCacheContent(vgroup, content)

        # ...make sure activity is set
        if (None != activity_id) or ('' == activity_id):
            log.warn("activity is not set, using fallback method")
            tmp_activity_id = activity_id
            old_booking['activity_id'] = activity_id
        else:
            old_booking['activity'] = old_booking['slot_id'].activity_id  # again we need to lookup activity
            tmp_activity_id = None

        activity = common_couch.getActivity(getHollyCouch(), tmp_activity_id)

        # ...again we need to look up activity
        old_booking['booking_state'] = activity['default_booking_state']

        if is_new:
            slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=subtype)
            slot = slot_map[slot_id]
            new_uid = genUID(type='booking')

            # ...if subtype is live, then set dates and end-dates
            if subtype in ['room', 'staff']:
                old_booking[
                    'booking_date'] = booking_date  # strftime not needed .strftime('%Y-%m-%d') #booking_day['date']
                old_booking['booking_end_date'] = booking_end_date  # strftime not needed .strftime('%Y-%m-%d')
                old_booking['booking_end_slot_id'] = booking_end_slot_id

                # we don't change booking_date and slot_id on program bookings. They use the schedule method instead.
                old_booking['slot_id'] = slot_id

                tmp_schema_subname = self.getSchemaSubNameOfSubtype(subtype)
                tmp_schema_id = booking_day[tmp_schema_subname]
                slot_row_schema_of_activity = getSlotRowSchemaOfActivity(getHollyCouch(), tmp_schema_id,
                                                                         tmp_activity_id)
                slot_row_schema_of_activity = list(slot_row_schema_of_activity)[0].value[1:]
                old_booking['slot_schema_row'] = slot_row_schema_of_activity

            getHollyCouch()[new_uid] = old_booking
            id = new_uid
            remember_book_slot(getHollyCouch(), booking_id=new_uid, booking=old_booking, slot_row_position=slot,
                               booking_day=booking_day, activity_title=activity['title'])

        else:  # booking is not new.
            # shouldn't be necessary: booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)
            slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=subtype)
            slot = slot_map[slot_id]

            if subtype in ['room', 'staff']:
                old_booking['slot_id'] = slot_id
                old_booking['booking_date'] = booking_day['date']
                old_booking['booking_end_date'] = booking_end_date
                old_booking['booking_end_slot_id'] = booking_end_slot_id

                tmp_schema_id = booking_day[self.getSchemaSubNameOfSubtype(subtype)]
                slot_row_schema_of_activity = getSlotRowSchemaOfActivity(getHollyCouch(), tmp_schema_id,
                                                                         tmp_activity_id)
                slot_row_schema_of_activity = list(slot_row_schema_of_activity)[0].value[1:]
                old_booking['slot_schema_row'] = slot_row_schema_of_activity

            # ...TODO: update this remeber thing significantly
            remember_booking_properties_change(getHollyCouch(), booking=old_booking, slot_row_position=slot,
                                               booking_day=booking_day, old_visiting_group_name=old_visiting_group_name,
                                               new_visiting_group_name=visiting_group_name, new_content='',
                                               activity_title=activity['title'])

            getHollyCouch()[id] = old_booking

        # ...block after book?
        if block_after_book:
            # TODO: will fail so I disabled it temporarilly
            if False:
                self.block_slot_helper(getHollyCouch(), booking_day_id, slot_row_position_id)

        return tmp_activity_id

    @expose('hollyrosa.templates.booking.request_new')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may change a booking'))
    @validate(validators={'return_to_day_id': validators.UnicodeString(not_empty=False),
                          'booking_id': validators.UnicodeString(not_empty=True),
                          'visiting_group_id': validators.UnicodeString(not_empty=False)})
    def edit_booking(self, return_to_day_id=None, booking_id=None, visiting_group_id='', **kw):
        """
        edit_booking is really edit_program_booking since room and staff bookings are done slightly different,
        making use of from/to time, so we can assume this only concerns program bookings BUT
        given that we can have several schemas for a year, we cannot know well which activities are valid in whished
        date range or on any given day,

        HOWEVER

        if we view any program booking as a whish rather than a decission, then we could list all
        reasonable activities (all program activities) AND if an activity is choosen that is not available according to schema,
        then we WARN on that/those days that THIS activity is NOT available this day.

        Given that there can be many activities, we should have one field for the last N used activities and
        a completion list rather than drop down list.

        Can TW2 generate a selection box instead of a drop-down?

        Well, there is Choosen wich would be cool to test, but it aint Dojo.
        Maybe we can have a text box that we do DOJO magick with?

        Client side Dojo could find the text box and when user clicks it things starts to happen,
        like a pop up dynamic form being shown.

        """

        tmpl_context.form = create_edit_new_booking_request_form
        edit_this_visiting_group = 0

        activities = [(a.doc['_id'], a.doc['title']) for a in getAllActivities(getHollyCouch())]
        if return_to_day_id is None:
            visiting_groups = [(e.doc['_id'], e.doc['name']) for e in getAllVisitingGroups(getHollyCouch())]
        else:
            booking_day_o = common_couch.getBookingDay(getHollyCouch(), return_to_day_id)
            visiting_groups = [(e.doc['_id'], e.doc['name']) for e in
                               getVisitingGroupsAtDate(getHollyCouch(), booking_day_o['date'])]

        if '' != visiting_group_id:
            tmp_visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)

        # ...patch since this is the way we will be called if validator for new will fail
        if (visiting_group_id != '') and (visiting_group_id is not None):
            booking_o = dict(id='', booking_content='', visiting_group_id=visiting_group_id,
                             visiting_group_name=tmp_visiting_group['name'], activity_id='')
            edit_this_visiting_group = 0  # visiting_group_id
        elif booking_id == '' or booking_id is None:
            booking_o = dict(id='', booking_content='', visiting_group_id=visiting_group_id, visiting_group_name='',
                             activity_id='')
        else:
            log.debug('edit_booking: booking exists')
            b = common_couch.getBooking(getHollyCouch(), booking_id)

            # ...process and sanitize dates
            booking_o = dict(id=b['_id'], booking_content=b['content'], visiting_group_id=b['visiting_group_id'],
                             activity_id=b['activity_id'], visiting_group_name=b['visiting_group_name'])

            from_date_ok, tmp_valid_from = getSanitizeDate(b['valid_from'], None)
            if from_date_ok:
                booking_o['valid_from'] = tmp_valid_from

            to_date_ok, tmp_valid_to = getSanitizeDate(b['valid_to'], None)
            if to_date_ok:
                booking_o['valid_to'] = tmp_valid_to

            requested_date_ok, tmp_requested_date = getSanitizeDate(b['requested_date'], None)
            if requested_date_ok:
                booking_o['requested_date'] = tmp_requested_date

        # TODO: We still need to add some reasonable sorting on the activities abd the visiting groups
        log.debug(str(booking_o))

        if return_to_day_id is not None and return_to_day_id != '':
            if 'requested_date' not in booking_o:

                requested_date_ok, tmp_requested_date = getSanitizeDate(booking_day_o['date'], None)
                if requested_date_ok:
                    booking_o['requested_date'] = tmp_requested_date

        booking_o['return_to_day_id'] = return_to_day_id

        # ...these are the two types of options that we somehow need to transfer to the form tw2 style
        activity_entries = json.dumps([dict(name=a[1], id=a[0]) for a in activities])
        visiting_group_options = json.dumps([dict(name=a[1], id=a[0]) for a in visiting_groups])

        return dict(visiting_groups=visiting_groups, activities=activities, booking=booking_o,
                    edit_this_visiting_group=edit_this_visiting_group, activity_entries=activity_entries,
                    visiting_group_options=visiting_group_options)

    @expose('hollyrosa.templates.booking.move')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may change a booking'))
    @validate(validators={'return_to_day_id': validators.UnicodeString(not_empty=False),
                          'booking_id': validators.UnicodeString(not_empty=False)})
    def move_booking(self, return_to_day_id=None, booking_id=None, **kw):
        log.debug('move_booking()')
        tmpl_context.form = create_move_booking_form

        # ...patch since this is the way we will be called if validator for new will fail
        booking_o = common_couch.getBooking(getHollyCouch(), booking_id)
        booking_o.return_to_day_id = return_to_day_id
        log.debug("getSlotAndActivityIdOfBooking: %s" % str(booking_o))
        activity_id, slot_o = getSlotAndActivityIdOfBooking(getHollyCouch(), booking_o, booking_o['subtype'])
        activity_o = common_couch.getActivity(getHollyCouch(), booking_o['activity_id'])

        # ...select activities based on if we are dealing with program activities or rooms
        if booking_o['subtype'] == 'program':
            activities = [(a.doc['_id'], a.doc['title']) for a in getAllActivities(getHollyCouch())]
        elif booking_o['subtype'] == 'room':
            activities = [(a.doc['_id'], a.doc['title']) for a in getAllRooms(getHollyCouch())]
        else:
            abort(500)

        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_o['booking_day_id'])
        booking_ = dict(activity_id=activity_id, content=booking_o['content'], cache_content=booking_o['cache_content'],
                        visiting_group_name=booking_o['visiting_group_name'], id=booking_o['_id'],
                        return_to_day_id=return_to_day_id)

        activity_entries = json.dumps([dict(name=a[1], id=a[0]) for a in activities])
        return dict(booking=booking_, activity=activity_o, booking_day=booking_day, slot=slot_o,
                    getRenderContentDict=getRenderContentDict, activity_entries=activity_entries)

    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may change activity properties'))
    @validate({"id": validators.UnicodeString(not_empty=True), "activity_id": validators.UnicodeString(not_empty=True),
               "activity_name": validators.UnicodeString(not_empty=True), "return_to_day_id": validators.UnicodeString})
    def save_move_booking(self, id=None, activity_id=None, activity_name=None, return_to_day_id=None, **kw):
        ensurePostRequest(request, name=__name__)
        booking_o = common_couch.getBooking(getHollyCouch(), id)
        old_activity_id = booking_o['activity_id']

        # ...slot row position must be changed, so we need to find slot row of activity and then slot row position
        # with aproximately the same time span
        old_slot_id = booking_o['slot_id']
        # old_activity_id,  old_slot = getSlotAndActivityIdOfBooking(new_booking)
        booking_day_id = booking_o['booking_day_id']
        booking_day_o = common_couch.getBookingDay(getHollyCouch(), booking_day_id)

        schema_name = self.getSchemaSubNameOfSubtype(booking_o['subtype'])
        schema_o = common_couch.getDaySchema(getHollyCouch(), booking_day_o[schema_name])

        # ...iterate thrue the schema first time looking for slot_id_position and activity
        the_schema = schema_o['schema']

        old_end_slot_id = booking_o.get('booking_end_slot_id', '')
        # ...first, find the index of the slot id
        # ...try match slot_id
        old_end_slot_index = None
        for tmp_activity_id, tmp_activity_row in the_schema.items():
            tmp_slot_index = 1
            for tmp_slot in tmp_activity_row[1:]:
                if tmp_slot['slot_id'] == old_slot_id:
                    # ...we got a match
                    old_activity_id_according_to_slot_id = tmp_activity_id
                    old_slot = tmp_slot
                    old_slot_index = tmp_slot_index
                elif tmp_slot['slot_id'] == old_end_slot_id:
                    old_end_slot_index = tmp_slot_index
                tmp_slot_index += 1

        # ...now, find the
        try:
            tmp_new_slot_row = the_schema[activity_id]
        except KeyError:
            flash('Activity not valid for that day', 'error')
            # raise TGValidationError('Activity not valid for that day')
            raise redirect(url('move_booking', params=dict(return_to_day_id=return_to_day_id, booking_id=id)))

        new_slot = tmp_new_slot_row[old_slot_index]
        new_slot_id = new_slot['slot_id']

        new_end_slot_id = None
        if old_end_slot_index is not None:
            new_end_slot = tmp_new_slot_row[old_end_slot_index]
            new_end_slot_id = new_end_slot['slot_id']

        # TODO: also need to change slot_schema_row as well as well as start and end slot id's
        old_slot_row_schema_of_activity = getSlotRowSchemaOfActivity(getHollyCouch(), schema_o['_id'], old_activity_id)
        old_slot_row_schema_of_activity = list(old_slot_row_schema_of_activity)[0].value[1:]

        slot_row_schema_of_activity = getSlotRowSchemaOfActivity(getHollyCouch(), schema_o['_id'], activity_id)
        slot_row_schema_of_activity = list(slot_row_schema_of_activity)[0].value[1:]

        booking_o['slot_schema_row'] = slot_row_schema_of_activity

        # TODO need to move slot_id and end_slot_id as well as slot_schema

        # new_slot_row = DBSession.query(booking.SlotRow).filter('activity_id='+str(activity_id)).one()
        # for tmp_slot_row_position in new_slot_row.slot_row_position:
        #
        #   # TODO: too hackish below
        #   if tmp_slot_row_position.time_from == old_slot_row_position.time_from:
        #       new_booking.slot_row_position = tmp_slot_row_position

        # ...it's not perfectly normalized that we also need to change activity id
        booking_o['activity_id'] = activity_id
        booking_o['slot_id'] = new_slot_id
        booking_o['booking_end_slot_id'] = new_end_slot_id
        getHollyCouch()[booking_o['_id']] = booking_o

        activity_title_map = getActivityTitleMap(getHollyCouch())

        # TODO: remember move booking
        # TODO: problem is taht if move is done on a booking of type live we end up in the rong place...
        if booking_o.get('subtype', 'program') == 'program':
            return_path = 'day'
        else:
            return_path = 'live'
        remember_booking_move(getHollyCouch(), booking=booking_o, booking_day=booking_day_o,
                              old_activity_title=activity_title_map[old_activity_id],
                              new_activity_title=activity_title_map[activity_id])

        raise redirect('/booking/' + return_path + '?booking_day_id=' + str(return_to_day_id))

    def getN_A_VisitingGroupId(self, holly_couch):
        """
        Retrieves the N/A visiting group.
        """
        visiting_group_s = [v.doc for v in getVisitingGroupOfVisitingGroupName(holly_couch, 'N/A')]
        if len(visiting_group_s) > 1:
            log.error("two N/A visiting groups with the same name")
            visiting_group_id = visiting_group_s[0]['_id']
        if len(visiting_group_s) == 1:
            visiting_group_id = visiting_group_s[0]['_id']
        else:
            raise ValueError("failed to obtain the N/A visiting group from DB")
        return visiting_group_id

    @expose()
    @require(Any(is_user('root'), has_level('view'), has_level('staff'), has_level('pl'),
                 msg='Only viewers, staff and PL can submitt a new booking request'))
    @validate(validators={'booking_content': validators.UnicodeString, "activity_id": validators.UnicodeString,
                          "activity_name": validators.UnicodeString, "visiting_group_name": validators.UnicodeString,
                          "visiting_group_display_name": validators.UnicodeString,
                          "valid_from": validators.DateValidator(date_format='%Y-%m-%d'),
                          "valid_to": validators.DateValidator(date_format='%Y-%m-%d'),
                          "requested_date": validators.DateValidator(date_format='%Y-%m-%d'),
                          "visiting_group_id": validators.UnicodeString, "id": validators.UnicodeString,
                          "return_to_day_id": validators.UnicodeString})
    def save_new_booking_request(self, booking_content='', activity_id=None, activity_name=None, visiting_group_name='',
                                 visiting_group_display_name='', valid_from=None, valid_to=None, requested_date=None,
                                 visiting_group_id=None, id=None, return_to_day_id=None, **kwargs):
        """
        Saves a booking requests that has no slot or booking day. These are better known as unscheduled bookings.
        """

        ensurePostRequest(request, name=__name__)
        is_new = ((id is None) or (id == ''))

        log.debug('save_new_booking_request()')

        if is_new:
            log.debug('save_new_booking_request:new program booking request')
            new_booking = common_couch.createEmptyProgramBooking()
        else:
            log.debug('save_new_booking_request:editing existing unscheduled booking')
            new_booking = common_couch.getBooking(getHollyCouch(), id)
            tmp_activity = common_couch.getActivity(getHollyCouch(), new_booking['activity_id'])
            old_booking = DataContainer(activity=tmp_activity, activity_id=new_booking['activity_id'],
                                        visiting_group_name=new_booking['visiting_group_name'],
                                        visiting_group_id=new_booking['visiting_group_id'],
                                        valid_from=new_booking['valid_from'], valid_to=new_booking['valid_to'],
                                        requested_date=new_booking['requested_date'], content=new_booking['content'],
                                        id=new_booking['_id'])

        new_booking['booking_state'] = 0

        # ...Id visiting group id is empty, it should be replaced with the N/A Group
        log.debug(
            u'save_new_booking_request:visiting_group_name={}, visiting_group_display_name={}, visiting_group_id={}'.format(
                visiting_group_name, visiting_group_display_name, visiting_group_id))
        if '' == visiting_group_id:
            log.warn('save_new_booking_request: Attention, no visiting group id supplied, using N/A group.')
            visiting_group_id = self.getN_A_VisitingGroupId(getHollyCouch())

        new_booking['content'] = booking_content

        new_booking['visiting_group_id'] = visiting_group_id
        new_booking['cache_content'] = computeCacheContent(
            common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id), booking_content)

        new_booking['activity_id'] = activity_id
        new_booking['visiting_group_name'] = visiting_group_display_name
        new_booking['last_changed_by_id'] = getLoggedInUserId(request)

        # ...todo add dates, but only after form validation
        log.debug("save_new_booking_request requeste_date=%s" % str(requested_date))
        new_booking['requested_date'] = requested_date
        new_booking['valid_from'] = valid_from
        new_booking['valid_to'] = valid_to

        if is_new:
            getHollyCouch()[genUID(type='booking')] = new_booking
            remember_new_booking_request(getHollyCouch(), new_booking)
        else:
            getHollyCouch()[id] = new_booking
            remember_booking_request_change(getHollyCouch(), old_booking=old_booking, new_booking=new_booking)

        if return_to_day_id is not None:
            if return_to_day_id != '':
                raise redirect('/booking/day?booking_day_id=' + str(return_to_day_id))
        if is_new:
            raise redirect('/visiting_group/view_all#vgroupid_' + str(visiting_group_id))
        raise redirect('/calendar/overview')

    @expose()
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can block or unblock slots'))
    @validate(validators={'return_to_day_id': validators.UnicodeString(not_empty=False),
                          'booking_id': validators.UnicodeString(not_empty=False)})
    def prolong(self, return_to_day_id=None, booking_id=None):
        """
        Prolong a booking by copying a booking and placing the copy in the following slot
        If necessary, the copy is placed in the beginning of the next booking day
        """
        ensurePostRequest(request, name=__name__)
        # TODO: one of the problems with prolong that just must be sloved is what do we do if the day shema is
        #  different for the day after?

        # ...first, find the slot to prolong to
        old_booking = common_couch.getBooking(getHollyCouch(), booking_id)  # move into model
        booking_day_id = old_booking['booking_day_id']
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)
        day_schema_id = booking_day['day_schema_id']
        day_schema = common_couch.getDaySchema(getHollyCouch(), day_schema_id)
        old_slot_id = old_booking['slot_id']
        schema = day_schema['schema']

        # ... TODO: find the slot and slot index. FACTOR OUT COMPARE MOVE BOOKING
        for tmp_activity_id, tmp_activity_row in schema.items():
            tmp_slot_index = 1
            for tmp_slot in tmp_activity_row[1:]:
                if tmp_slot['slot_id'] == old_slot_id:
                    old_activity_id = tmp_activity_id
                    old_slot = tmp_slot
                    old_slot_index = tmp_slot_index
                    old_slot_row = tmp_activity_row
                    break
                tmp_slot_index += 1

        activity = common_couch.getActivity(getHollyCouch(), old_activity_id)

        if (old_slot_index + 1) >= len(old_slot_row):
            flash('last slot')

            new_booking_day_id = getNextBookingDayId(getHollyCouch(), booking_day)
            # new_booking_slot_row_position_id = slot_row_positions[0].id
            new_slot_id = old_slot_row[1]['slot_id']
        else:

            #            i = 0
            #            last_slrp = None
            #            for slrp in slot_row_positions:
            #                if last_slrp ==  old_booking.slot_row_position_id:
            #                    break
            #                last_slrp = slrp.id
            #            new_booking_slot_row_position_id = slrp.id
            new_slot_id = old_slot_row[old_slot_index + 1]['slot_id']
            new_booking_day_id = booking_day_id

        # ...then figure out if the slot to prolong to is blocked

        # todo: figure out if slot is blocked

        new_booking_slot_row_position_states = self.getSlotStateOfBookingDayIdAndSlotId(getHollyCouch(),
                                                                                        new_booking_day_id, new_slot_id)

        # ...if it isn't blocked, then book that slot.
        if len(new_booking_slot_row_position_states) == 0:

            # ...find the booking

            new_booking = common_couch.createEmptyProgramBooking()  # dict(type='booking')
            for k, v in old_booking.items():
                new_booking[k] = v

            new_booking['last_changed_by_id'] = getLoggedInUserId(request)
            new_booking['slot_id'] = new_slot_id
            new_booking['booking_day_id'] = new_booking_day_id
            new_booking['booking_state'] = activity['default_booking_state']

            getHollyCouch()[genUID(type='booking')] = new_booking
            remember_new_booking_request(getHollyCouch(), new_booking)
        else:
            flash('wont prolong since next slot is blocked', 'warning')
            redirect('/booking/day?booking_day_id=' + str(booking_day_id))

        # TODO: remember prolong

        raise redirect(
            '/booking/day?booking_day_id=' + str(new_booking['booking_day_id']) + make_booking_day_activity_anchor(
                new_booking['activity_id']))

    def getActivityIdOfBooking(self, holly_couch, booking_day_id, slot_id, subtype='program'):
        """
        try to find activity given booking day and slot_id

        We need to find booking day, then schema, in schema there are rows per activity. Somewhere in that schema
        is the answer.
        """
        # TODO: refactor, should be able to use existing view
        booking_day_o = common_couch.getBookingDay(holly_couch, booking_day_id)
        schema_name = booking_day_o[self.getSchemaSubNameOfSubtype(subtype)]
        schema_o = common_couch.getDaySchema(holly_couch, schema_name)

        # ...iterate thrue the schema
        for tmp_activity_id, tmp_activity_row in schema_o['schema'].items():
            for tmp_slot in tmp_activity_row[1:]:
                if tmp_slot['slot_id'] == slot_id:
                    return tmp_activity_id

        # TODO: I dont think it is unreasonable that each schema has a lookuptable slot_id -> activity that is
        #  updated if the schema is updated.

    def block_slot_helper(self, holly_couch, booking_day_id, slot_id, level=1, subtype='program'):
        slot_state = dict(slot_id=slot_id, booking_day_id=booking_day_id, level=level, type='slot_state')
        holly_couch[genUID(type='slot_state')] = slot_state
        # TODO: set state variable when it has been introduced

        booking_day = common_couch.getBookingDay(holly_couch, booking_day_id)
        slot_map = getSchemaSlotActivityMap(holly_couch, booking_day, subtype=subtype)
        slot = slot_map[slot_id]
        remember_block_slot(holly_couch, slot_row_position=slot, booking_day=booking_day, level=level,
                            changed_by=getLoggedInUserId(request),
                            activity_title=common_couch.getActivity(holly_couch, slot['activity_id'])['title'])

    @expose()
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can block or unblock slots'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=True),
                          'slot_id': validators.UnicodeString(not_empty=True),
                          'level': validators.UnicodeString(not_empty=True),
                          'subtype': validators.UnicodeString(not_empty=False)})
    def block_slot(self, booking_day_id=None, slot_id=None, level=1, subtype='program'):
        ensurePostRequest(request, name=__name__)
        self.block_slot_helper(getHollyCouch(), booking_day_id, slot_id, level=level)
        activity_id = self.getActivityIdOfBooking(getHollyCouch(), booking_day_id, slot_id, subtype=subtype)
        if subtype == 'program':
            raise redirect('day?booking_day_id=' + booking_day_id + make_booking_day_activity_anchor(activity_id))
        raise redirect(
            'live?booking_day_id=' + booking_day_id + '&subtype=' + subtype + make_booking_day_activity_anchor(
                activity_id))

    @expose()
    @require(Any(is_user('root'), has_level('pl'), msg='Only PL can block or unblock slots'))
    @validate(validators={'booking_day_id': validators.UnicodeString(not_empty=True),
                          'slot_id': validators.UnicodeString(not_empty=True),
                          'subtype': validators.UnicodeString(not_empty=False)})
    def unblock_slot(self, booking_day_id=None, slot_id=None, subtype='program'):
        ensurePostRequest(request, name=__name__)
        # todo: set state variable when it has been introduced
        tmp_slot_state_ids = self.getSlotStateOfBookingDayIdAndSlotId(getHollyCouch(), booking_day_id, slot_id)
        for tmp_slot_state_id in tmp_slot_state_ids:
            # TODO: optimize this, we shoud get the docs through the query above
            deleteme = common_couch.getSlotState(getHollyCouch(), tmp_slot_state_id.id)
            getHollyCouch().delete(deleteme)

        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype=subtype)
        slot = slot_map[slot_id]
        activity_id = slot['activity_id']
        remember_unblock_slot(getHollyCouch(), slot_row_position=slot, booking_day=booking_day,
                              changed_by=getLoggedInUserId(request), level=0,
                              activity_title=common_couch.getActivity(getHollyCouch(), activity_id)['title'])

        if subtype == 'program':
            raise redirect('day?booking_day_id=' + booking_day_id + make_booking_day_activity_anchor(activity_id))
        raise redirect(
            'live?day_id=' + booking_day_id + '&subtype=' + subtype + make_booking_day_activity_anchor(activity_id))

    # ---HERE STARTS MULTIBOOK WHICH SOON IS HISTORY I HOPE

    @expose('hollyrosa.templates.edit_multi_book')
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may use multibook functionality'))
    @validate(validators={'booking_id': validators.UnicodeString(not_empty=True)})
    def multi_book(self, booking_id=None, **kw):
        booking_o = common_couch.getBooking(getHollyCouch(), booking_id)
        booking_day_id = booking_o['booking_day_id']
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_day_id)
        day_schema_id = booking_day['day_schema_id']
        day_schema = common_couch.getDaySchema(getHollyCouch(), day_schema_id)

        booking_days = [b.doc for b in getAllBookingDays(getHollyCouch())]
        activity_id = booking_o['activity_id']
        activities_map = self.getActivitiesMap(getAllActivities(getHollyCouch()))

        slot_rows = self.make_slot_rows__of_day_schema(day_schema, activities_map, booking_day['date'])

        slot_row = [s for s in slot_rows if s.activity_id == activity_id][0]

        bookings = {}

        for tmp_booking_day in booking_days:
            bookings[tmp_booking_day.id] = {}

        slot_ids = [sp.id for sp in slot_row.slot_row_position]
        # for tmp_slot_row_position in slot_row.slot_row_position:
        bookings_of_slot_position = [b.doc for b in
                                     getHollyCouch().view('booking_day/slot_id_of_booking', keys=slot_ids,
                                                          include_docs=True)]

        for tmp_booking in bookings_of_slot_position:
            # if None == tmp_slot_row_position.id:
            #    raise IOError,  "None not expected"
            if None == tmp_booking.id:
                raise IOError("None not expected")

            if None != tmp_booking['booking_day_id']:

                if tmp_booking['slot_id'] not in bookings[tmp_booking['booking_day_id']]:
                    bookings[tmp_booking['booking_day_id']][tmp_booking['slot_id']] = []
                bookings[tmp_booking['booking_day_id']][tmp_booking['slot_id']].append(tmp_booking)

        blockings = [st.doc for st in
                     getHollyCouch().view('booking_day/slot_state_of_slot_id', keys=slot_ids, include_docs=True)]
        blockings_map = dict()
        for b in blockings:
            tmp_booking_day_id = b['booking_day_id']
            blockings_map[str(tmp_booking_day_id) + ':''' + str(b['slot_id'])] = b

        return dict(booking=booking_o, booking_days=booking_days, booking_day=None, slot_row=slot_row,
                    blockings_map=blockings_map, bookings=bookings, activities_map=activities_map,
                    getRenderContent=getRenderContentDict)

    @expose("json")
    @validate({'booking_day_id': validators.UnicodeString(not_empty=True),
               'slot_row_position_id': validators.UnicodeString(not_empty=True),
               'activity_id': validators.UnicodeString(not_empty=True),
               'content': validators.UnicodeString(not_empty=False),
               'visiting_group_id_id': validators.UnicodeString(not_empty=True),
               'block_after_book': validators.Bool(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may create a booking the async way'))
    def create_booking_async(self, booking_day_id='', slot_row_position_id='', activity_id='', content='',
                             block_after_book=False, visiting_group_id=None):
        ensurePostRequest(request, name=__name__)
        # ...TODO refactor to isBlocked
        slot_row_position_states = [b.doc for b in
                                    getHollyCouch().view('booking_day/slot_state_of_slot_id_and_booking_day_id',
                                                         keys=[booking_day_id, slot_row_position_id])]

        if 0 < len(slot_row_position_states):
            return dict(error_msg="slot blocked, wont book")

        else:
            vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
            new_id = genUID(type='booking')
            new_booking = common_couch.createEmptyProgramBooking()
            new_booking['booking_state'] = 0
            new_booking['content'] = content
            new_booking['cache_content'] = computeCacheContent(vgroup, content)
            new_booking['activity_id'] = activity_id
            new_booking['last_changed_by_id'] = getLoggedInUserId(request)
            new_booking['visiting_group_id'] = visiting_group_id
            new_booking['visiting_group_name'] = vgroup['name']

            # TODO: add dates, but only after form validation
            # new_booking.requested_date = old_booking.requested_date
            # new_booking.valid_from = old_booking.valid_from
            # new_booking.valid_to = old_booking.valid_to

            new_booking['booking_day_id'] = booking_day_id
            new_booking['slot_id'] = slot_row_position_id

            getHollyCouch()[new_id] = new_booking

            remember_new_booking_request(getHollyCouch(), new_booking)
            slot_row_position_state = 0
            if block_after_book:
                self.block_slot_helper(getHollyCouch(), booking_day_id, slot_row_position_id, level=1)
                slot_row_position_state = 1

        return dict(text="hello", booking_day_id=booking_day_id, slot_row_position_id=slot_row_position_id,
                    booking=new_booking, visiting_group_name=vgroup['name'], success=True,
                    slot_row_position_state=slot_row_position_state)

    @expose("json")
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may delete a booking using async interface'))
    @validate({'delete_req_booking_id': validators.UnicodeString(not_empty=True),
               'activity_id': validators.UnicodeString(not_empty=True),
               'visiting_group_id_id': validators.UnicodeString(not_empty=True)})
    def delete_booking_async(self, delete_req_booking_id=0, activity_id=0, visiting_group_id=None):
        """
        Delete booking async is for multibook view
        """
        ensurePostRequest(request, name=__name__)
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        booking_o = common_couch.getBooking(getHollyCouch(), delete_req_booking_id)
        remember_delete_booking_request(getHollyCouch(), booking_o)
        deleteBooking(getHollyCouch(), booking_o)

        return dict(text="hello", delete_req_booking_id=delete_req_booking_id, visiting_group_name=vgroup['name'],
                    success=True)

    @expose("json")
    @require(Any(is_user('root'), has_level('pl'), msg='Only pl may indicate to igonre a booking warning'))
    @validate(validators={'booking_id': validators.UnicodeString(not_empty=True)})
    def ignore_booking_warning_async(self, booking_id=''):
        """
        Finds a booking and set the ignore warning flag so it wont be listed among program booking warnings.
        """
        ensurePostRequest(request, name=__name__)
        booking_o = common_couch.getBooking(getHollyCouch(), booking_id)
        booking_o['hide_warn_on_suspect_booking'] = True
        getHollyCouch()[booking_id] = booking_o
        tmp_activity = common_couch.getActivity(getHollyCouch(), booking_o['activity_id'])
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_o['booking_day_id'])
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype='program')
        slot = slot_map[booking_o['slot_id']]

        remember_ignore_booking_warning(getHollyCouch(), booking=booking_o, slot_row_position=slot,
                                        booking_day=booking_day, changed_by=getLoggedInUserId(request),
                                        activity=tmp_activity)

        return dict(booking_id=booking_id)

    @expose("json")
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may unschedule bookings using async method'))
    @validate(validators={'delete_req_booking_id': validators.UnicodeString(not_empty=True),
                          'activity_id': validators.UnicodeString(not_empty=True),
                          'visiting_group_id_id': validators.UnicodeString(not_empty=True)})
    def unschedule_booking_async(self, delete_req_booking_id=0, activity_id=0, visiting_group_id=None):
        ensurePostRequest(request, name=__name__)
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        booking_o = common_couch.getBooking(getHollyCouch(), delete_req_booking_id)
        booking_o.last_changed_by_id = getLoggedInUserId(request)
        booking_day = common_couch.getBookingDay(getHollyCouch(), booking_o['booking_day_id'])
        old_slot_id = booking_o['slot_id']
        slot_map = getSchemaSlotActivityMap(getHollyCouch(), booking_day, subtype='program')
        slot = slot_map[old_slot_id]
        activity = common_couch.getActivity(getHollyCouch(), booking_o['activity_id'])
        remember_unschedule_booking(getHollyCouch(), booking=booking_o, slot_row_position=slot, booking_day=booking_day,
                                    changed_by='', activity=activity)
        booking_o['booking_state'] = 0
        booking_o['booking_day_id'] = None
        booking_o['slot_row_position_id'] = None
        getHollyCouch()[booking_o['_id']] = booking_o

        return dict(text="hello", delete_req_booking_id=delete_req_booking_id, visiting_group_name=vgroup['name'],
                    success=True)
