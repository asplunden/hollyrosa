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

from hollyrosa.controllers.common import has_level, ensurePostRequest
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, getHollyCouch
from hollyrosa.model.booking_couch import getAgeGroupStatistics, getTagStatistics, getActivityTitleMap, \
    getActivityStatistics
from hollyrosa.model.booking_couch import getAllActivityGroups, getAllScheduledBookings, getAllBookingDays, \
    getAllVisitingGroups, getAllActivities
from tg import expose, require, request, redirect, abort, config
from tg.predicates import Any

__all__ = ['tools']

log = logging.getLogger()


class Tools(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    @expose('hollyrosa.templates.tools.tools_show')
    @require(Any(has_level('staff'), has_level('pl'), msg='Only PL or staff members may view the tools page'))
    def show(self, day=None):
        """Show an overview of all bookings"""
        if day is None:
            day = datetime.datetime.today().date().strftime("%Y-%m-%d")

        activity_groups = [h.value for h in getAllActivityGroups(getHollyCouch())]
        return dict(show_day=day, activity_groups=activity_groups, db_name=config['couch.database'],
                    db_url=config['couch.db_url'], debug_enabled=config['debug'], serve_static=config['serve_static'])

    def get_severity(self, visiting_group, severity):
        if visiting_group.get('hide_warn_on_suspect_bookings', False):
            severity = 0
        return severity

    @expose('hollyrosa.templates.tools.view_sanity_check_property_usage')
    @require(Any(has_level('staff'), has_level('pl'),
                 msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def sanity_check_property_usage(self):
        log.info("sanity_check_property_usage()")

        # ...iterate through all bookings, we are only interested in scheduled bookings
        bookings = getAllScheduledBookings(getHollyCouch(), limit=1000000)
        booking_days_map = dict()
        for bd in getAllBookingDays(getHollyCouch()):
            booking_days_map[bd.doc['_id']] = bd.doc

        visiting_group_map = dict()
        for vg in getAllVisitingGroups(getHollyCouch()):
            visiting_group_map[vg.key[1]] = vg.doc

        activity_title_map = getActivityTitleMap(getHollyCouch())

        problems = list()
        for tmp_bx in bookings:
            tmp_b = tmp_bx.doc
            tmp_b_day_id = tmp_b['booking_day_id']
            tmp_b_day = booking_days_map[tmp_b_day_id]

            if None != tmp_b_day:  # and tmp_b_day.date >= datetime.date.today():
                if tmp_b['visiting_group_id'] != '' and (False == tmp_b.get('hide_warn_on_suspect_booking', False)):
                    tmp_date = tmp_b_day['date']
                    tmp_content = activity_title_map[tmp_b['activity_id']] + ' ' + tmp_b['content']
                    tmp_b_visiting_group = visiting_group_map[tmp_b['visiting_group_id']]

                    if 'from_date' not in tmp_b_visiting_group:
                        problems.append(dict(booking=tmp_b,
                                             msg='visiting group %s has no from_date' % tmp_b_visiting_group[
                                                 'visiting_group_name'], severity=100))
                    else:
                        if tmp_b_visiting_group['from_date'] > tmp_date:
                            problems.append(dict(booking=tmp_b, msg='arrives at %s but booking %s is at %s' % (
                                str(tmp_b_visiting_group['from_date']), tmp_content, str(tmp_date)), severity=10))

                        if tmp_b_visiting_group['from_date'] == tmp_date:
                            problems.append(dict(booking=tmp_b, msg='arrives same day as booking %s, at %s' % (
                                tmp_content, str(tmp_b_visiting_group['from_date'])),
                                                 severity=self.get_severity(tmp_b_visiting_group, 1)))

                    if tmp_b_visiting_group['to_date'] < tmp_date:
                        problems.append(dict(booking=tmp_b, msg='leves at %s but booking %s is at %s' % (
                            str(tmp_b_visiting_group['to_date']), tmp_content, str(tmp_date)), severity=10))

                    if tmp_b_visiting_group['to_date'] == tmp_date:
                        problems.append(dict(booking=tmp_b, msg='leves same day as booking %s, at %s' % (
                            tmp_content, str(tmp_b_visiting_group['to_date'])),
                                             severity=self.get_severity(tmp_b_visiting_group, 1)))

                    tmp_content = tmp_b['content']
                    for tmp_prop in tmp_b_visiting_group['visiting_group_properties'].values():
                        checks = [x + tmp_prop['property'] for x in ['$$', '$', '$#', '#']]

                        for check in checks:
                            if check in tmp_content:
                                if tmp_prop['from_date'] > tmp_date:
                                    problems.append(dict(booking=tmp_b, msg='property $' + tmp_prop[
                                        'property'] + ' usable from ' + str(
                                        tmp_prop['from_date']) + ' but booking is at ' + str(tmp_date), severity=10))

                                if tmp_prop['from_date'] == tmp_date:
                                    problems.append(dict(booking=tmp_b,
                                                         msg='property $' + tmp_prop['property'] + ' arrives at ' + str(
                                                             tmp_prop['from_date']) + ' and booking is the same day',
                                                         severity=self.get_severity(tmp_b_visiting_group, 1)))

                                if tmp_prop['to_date'] < tmp_date:
                                    problems.append(dict(booking=tmp_b,
                                                         msg='property $' + tmp_prop['property'] + ' usable to ' + str(
                                                             tmp_prop['to_date']) + ' but booking is at ' + str(
                                                             tmp_date), severity=10))

                                if tmp_prop['to_date'] == tmp_date:
                                    problems.append(dict(booking=tmp_b,
                                                         msg='property $' + tmp_prop['property'] + ' leavs at ' + str(
                                                             tmp_prop['to_date']) + ' and booking is the same day ',
                                                         severity=self.get_severity(tmp_b_visiting_group, 1)))

                                break  # there can be more than one match in checks
        problems.sort(key=lambda x: x['severity'], reverse=True)
        return dict(problems=problems, visiting_group_map=visiting_group_map)

    @expose('hollyrosa.templates.tools.activity_statistics')
    @require(
        Any(has_level('staff'), has_level('pl'), msg='Only PL or staff members can take a look at people statistics'))
    def activity_statistics(self):
        activity_statistics = getActivityStatistics(getHollyCouch())

        # ...return activity, activity_group, bookings
        result = list()
        for tmp_activity_stat in activity_statistics:
            tmp_key = tmp_activity_stat.key
            tmp_value = tmp_activity_stat.value

            tmp_activity_id = tmp_key[0]
            tmp_activity = getHollyCouch()[tmp_activity_id]
            tmp_activity_name = tmp_activity['title']
            activity_group_name = getHollyCouch()[tmp_activity['activity_group_id']]['title']
            totals = tmp_value
            row = dict(activity=tmp_activity_name, activity_group=activity_group_name, totals=totals)
            result.append(row)

        return dict(statistics=result)

    @expose('hollyrosa.templates.tools.visitor_statistics')
    @require(
        Any(has_level('staff'), has_level('pl'), msg='Only PL or staff members can take a look at people statistics'))
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

        statistics_totals = getAgeGroupStatistics(getHollyCouch(), group_level=1)
        statistics = getAgeGroupStatistics(getHollyCouch())

        property_names = dict()
        totals = dict()  # totals = list()
        for tmp in statistics:
            tmp_key = tmp.key
            tmp_value = tmp.value

            tmp_property = tmp_key[1]
            tmp_date_x = tmp_key[0]
            tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1],
                                     tmp_date_x[2])  # '-'.join([str(t) for t in tmp_date])

            tot = totals.get(tmp_date, dict())
            tot[tmp_property] = int(tmp_value)
            property_names[tmp_property] = 1  # keeping track of property names used
            totals[tmp_date] = tot

        # ...same thing but now for aggregate statistics
        all_totals = list()
        for tmp in statistics_totals:
            tmp_key = tmp.key
            tmp_value = tmp.value

            tmp_date_x = tmp_key[0]
            tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1], tmp_date_x[2])

            tot = totals.get(tmp_date, dict())
            # ...for now we need to protect against tot=0 giving zero division errors
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

        property_ns = ['spar', 'uppt', 'aven', 'utm']
        l = list()
        for n in property_names.keys():
            if n not in property_ns:
                l.append(n)

        return dict(property_names=l, people_by_day=all_totals)

    @expose('hollyrosa.templates.tools.vodb_statistics')
    @require(
        Any(has_level('staff'), has_level('pl'), msg='Only PL or staff members can take a look at people statistics'))
    def vodb_statistics(self):
        """
        This method is intended to show the number of participants in different workflow state (preliminary, etc)
        """
        statistics_totals = getTagStatistics(getHollyCouch(), group_level=1)
        statistics = getTagStatistics(getHollyCouch(), group_level=2)

        # ...find all tags that is used and perhaps filter out unwanted ones.

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
                sum = tot.get('tot', 0)
                sum += int(tmp_value)
                tot['tot'] = sum
                tags[tmp_tag] = 1
                totals[tmp_date] = tot

        all_totals = list()
        for tmp in statistics_totals:
            tmp_key = tmp.key
            tmp_value = tmp.value
            tmp_date_x = tmp_key[0]
            tmp_date = datetime.date(tmp_date_x[0], tmp_date_x[1], tmp_date_x[2])

            tot = totals.get(tmp_date, dict(tot=0))
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

        return dict(tags=['vodb:definitiv', u'vodb:preliminär', u'vodb:förfrågan', 'vodb:na'], people_by_day=all_totals)

    @expose()
    @require(Any(has_level('pl'), msg='Only PL can poke around the schemas'))
    def create_living_schema(self):
        log.info("create_living_schema()")
        ensurePostRequest(request, __name__)
        ew_id = genUID(type='living_schema')
        schema = dict(type='day_schema', subtype='room', title='room schema 2013',
                      activity_group_ids=["activity_groups_ids", "roomgroup.fyrbyn", "roomgroup.vaderstracken",
                                          "roomgroup.vindarnashus", "roomgroup.tunet",
                                          "roomgroup.skrakvik", "roomgroup.tc", "roomgroup.alphyddorna",
                                          "roomgroup.gokboet", "roomgroup.kojan"])
        all_activities = getAllActivities(getHollyCouch())

        # ...create some living, map to all activities in ag groups house
        i = 0
        z = 0
        tmp_schema = dict()
        for tmp_act in list(all_activities):
            if 'activity_group_id' in tmp_act or True:
                if tmp_act.doc['activity_group_id'][:9] == 'roomgroup':
                    z += 1
                    tmp_id = dict(zorder=z, id=tmp_act['id'])
                    tmp_fm = dict(time_from='00:00:00', time_to='12:00:00', duration='12:00:00', title='FM',
                                  slot_id='live_slot.' + str(i))
                    i += 1
                    tmp_em = dict(time_from='12:00:00', time_to='23:59:00', duration='12:00:00', title='EM',
                                  slot_id='live_slot.' + str(i))
                    # ...create fm and em but nothing more
                    i += 1

                    tmp_schema[tmp_act['id']] = [tmp_id, tmp_fm, tmp_em]

        schema['schema'] = tmp_schema
        getHollyCouch()[ew_id] = schema

        raise redirect(request.referer)
