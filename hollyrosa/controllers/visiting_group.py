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
import functools

from tg import expose, flash, require, request, redirect, validate, response
from formencode import validators
from tg.predicates import Any
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, getHollyCouch
from hollyrosa.model.booking_couch import getAllActivities, getAllVisitingGroups, getVisitingGroupsAtDate, \
    getVisitingGroupsInDatePeriod, get_bookings_of_visiting_group, getSchemaSlotActivityMap, \
    getVisitingGroupsByBoknstatus, \
    getNotesForTarget, get_booking_info_notes_with_matched_language
from hollyrosa.model.booking_couch import getBookingDays, getAllVisitingGroupsNameAmongBookings, getAllTags, \
    getDocumentsByTag, getVisitingGroupOfVisitingGroupName, getTargetNumberOfNotesMap, getVisitingGroupsByVodbState, \
    getVisitingGroupTypes
from hollyrosa.controllers.common import sanitizeDate, languages_map, default_language

# ...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context

from hollyrosa.widgets.forms.edit_visiting_group_form import create_edit_visiting_group_form

from hollyrosa.controllers.common import workflow_map, bokn_status_map, DataContainer, \
    getRenderContent, has_level, reFormatDate, getLoggedInUserId, \
    makeVisitingGroupObjectOfVGDictionary, vodb_eat_times_options, vodb_live_times_options, \
    hide_cache_content_in_booking, getLoggedInUser, vodb_status_map, ensurePostRequest, cleanHtml
from hollyrosa.controllers.visiting_group_common import populatePropertiesAndRemoveUnusedProperties, \
    updateBookingsCacheContentAfterPropertyChange, updateVisitingGroupComputedSheets, \
    computeAllUsedVisitingGroupsTagsForTagSheet, program_visiting_group_properties_template, \
    staff_visiting_group_properties_template, course_visiting_group_properties_template
from hollyrosa.controllers import common_couch

log = logging.getLogger(__name__)

__all__ = ['VisitingGroup']


class VisitingGroupPropertyRow(object):
    """Used for supplying data to the properties row fields in edit visiting group and edit vodb group"""

    def __init__(self, id, property_row):
        self.id = id
        self.property = property_row['property']
        self.unit = property_row['unit']
        self.value = property_row['value']
        self.description = property_row['description']
        self.from_date = property_row['from_date']
        self.to_date = property_row['to_date']


class VisitingGroup(BaseController):

    def make_remaining_visiting_groups_map(self, visiting_groups, from_date='', to_date=''):
        v_group_map = dict()
        all_existing_names = \
            getAllVisitingGroupsNameAmongBookings(getHollyCouch(), from_date=from_date, to_date=to_date)
        exisiting_vgroup_names = [n['name'] for n in visiting_groups]
        for b in all_existing_names:
            if b not in exisiting_vgroup_names:
                v_group_map[b] = 1

        return v_group_map

    def fn_sort_by_second_item(self, a, b):
        return cmp(a[0], b[0])

    def fn_cmp_booking_date_list(self, a, b):
        if a[0].booking_day is None:
            if b[0].booking_day is None:
                return 0
            else:
                return -1

        elif b[0].booking_day is None:
            return 1
        else:
            if a[0].booking_day['date'] > b[0].booking_day['date']:
                return 1
            elif a[0].booking_day['date'] < b[0].booking_day['date']:
                return -1
            else:
                return 0

    def fn_cmp_booking_timestamps(self, a, b):
        if a.booking_day is None:
            if b.booking_day is None:
                return 0
            else:
                return -1

        elif b.booking_day is None:
            return 1

        elif a.booking_day['date'] > b.booking_day['date']:
            return 1
        elif a.booking_day['date'] < b.booking_day['date']:
            return -1
        else:
            if a.slot['time_from'] > b.slot['time_from']:
                return 1
            elif a.slot['time_from'] < b.slot['time_from']:
                return -1
            else:
                return 0

    def get_slot_map_of_booking_day(self, booking_day_slot_map, tmp_booking_day, subtype='program'):

        # in the future, select between bookings subtype

        tmp_schema_id = tmp_booking_day['day_schema_id']

        if tmp_schema_id not in booking_day_slot_map:
            tmp_slot_map = getSchemaSlotActivityMap(getHollyCouch(), tmp_booking_day, subtype=subtype)
            booking_day_slot_map[tmp_schema_id] = tmp_slot_map
        return booking_day_slot_map[tmp_schema_id]

    def get_to_think_about_title(self, visiting_group):
        """
        Creates translated title for the page. It's not much that's need translation right now.
        """
        if not visiting_group:
            return u"Att tänka på"
        trans = {"se-SV": u"Att tänka på", "us-EN": u"Important Info", "de-DE": "Wichtig Information"}
        return trans[visiting_group.get("language", default_language)]

    def get_activity_title(self, visiting_group, activity):
        """
        To be used in templates, returns the language matched activity title
        """
        language = visiting_group.get('language', default_language)

        if 'language_versions' in activity:
            if language in activity['language_versions']:
                return activity['language_versions'][language]['title']
        return activity['title']

    def view_bookings_of_visiting_group(self, visiting_group, visiting_group_id, name, bookings, hide_comment=0,
                                        show_group=0, render_time=''):
        # now group all bookings in a dict mapping activity_id:content
        clustered_bookings = {}
        booking_day_map = dict()
        booking_day_slot_map = dict()
        for bd in getBookingDays(getHollyCouch()):
            booking_day_map[bd.doc['_id']] = bd.doc

            # this is very time consuming, better list all slot map and build a map
            # booking_day_slot_map[bd.doc['_id']] = getSchemaSlotActivityMap(getHollyCouch(), bd.doc, subtype='program')

        activities = dict()
        used_activities_keys = dict()
        for x in getAllActivities(getHollyCouch()):
            activities[x.key[1]] = x.doc

        # TODO: There will be quite a few multiples if we search on both id and name!
        for b in bookings:
            if hide_comment == 1:
                hide_cache_content_in_booking(b)

            key = str(b['activity_id']) + ':' + b['content']
            if b.get('booking_day_id', None) is None:
                key = 'N' + key

            # we need to do this transfer because we need to add booking_day.date and slot time.
            # HERE WE MUST NOW ONCE AGAIN GET SLOT FROM BOOKING DAY ID AND SLOT ID...
            booking_day_id = None
            slot_id = ''
            slot_o = None
            tmp_booking_day = None

            used_activities_keys[b['activity_id']] = 1
            used_activities_keys[activities[b['activity_id']]['activity_group_id']] = 1

            if 'booking_day_id' in b:
                booking_day_id = b['booking_day_id']
                if '' != booking_day_id:
                    tmp_booking_day = booking_day_map[booking_day_id]
                    slot_id = b['slot_id']
                    tmp_slot_map = self.get_slot_map_of_booking_day(booking_day_slot_map, tmp_booking_day)
                    slot_o = tmp_slot_map[slot_id]

            b2 = DataContainer(booking_state=b['booking_state'],
                               cache_content=b['cache_content'],
                               content=b['content'],
                               activity=activities[b['activity_id']],
                               id=b['_id'],
                               booking_day=tmp_booking_day,
                               slot_id=slot_id,
                               slot=slot_o,
                               booking_day_id=booking_day_id,
                               valid_from=b.get('valid_from', ''),
                               valid_to=b.get('valid_to', ''),
                               requested_date=b.get('requested_date', ''))

            if key in clustered_bookings:
                bl = clustered_bookings[key]
                bl.append(b2)
            else:
                bl = list()
                bl.append(b2)
                clustered_bookings[key] = bl

        clustered_bookings_list = list(clustered_bookings.values())
        clustered_bookings_list.sort(key=functools.cmp_to_key(self.fn_cmp_booking_date_list))
        for bl in clustered_bookings_list:
            bl.sort(key=functools.cmp_to_key(self.fn_cmp_booking_timestamps))

        if True:  # show_group==1:
            # filter the booking info notes on language.
            # if visiting group has no language, use default language
            # if there is a specific language, filter the notes on that language
            visiting_group_language = visiting_group.get('language', default_language)

            # build a map from id of activity -> list of note languages and use the map to find best language match
            booking_info_notes_with_matched_language = \
                get_booking_info_notes_with_matched_language(getHollyCouch(), used_activities_keys,
                                                             visiting_group_language)

        else:
            booking_info_notes = []
        return dict(clustered_bookings=clustered_bookings_list,
                    name=name,
                    workflow_map=workflow_map,
                    visiting_group_id=visiting_group_id,
                    getRenderContent=getRenderContent,
                    formatDate=reFormatDate,
                    booking_info_notes=booking_info_notes_with_matched_language,
                    render_time=render_time,
                    visiting_group=visiting_group,
                    bokn_status_map=bokn_status_map,
                    notes=[n.doc for n in getNotesForTarget(getHollyCouch(), visiting_group_id)],
                    show_group=show_group,
                    to_think_about_title=self.get_to_think_about_title(visiting_group),
                    getActivityTitle=self.get_activity_title)

    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view listing of visiting groups'))
    @expose('hollyrosa.templates.visiting_group.view_all')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view(self, url):
        """Shows a view of all visiting groups in the system"""
        visiting_groups = [x.doc for x in getAllVisitingGroups(getHollyCouch())]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        activity_groups = ["group", "staff", "course", "school"]
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    activity_groups=activity_groups,
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @validate(validators={'from_date': validators.DateValidator(not_empty=False),
                          'to_date': validators.DateValidator(not_empty=False)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view_date_range(self, from_date=None, to_date=None):
        visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(getHollyCouch(), from_date, to_date)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @require(Any(has_level('pl'), has_level('staff'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view_tags(self, tag):
        # TODO: rename and maybe only return visiting groups docs ?
        visiting_groups = [v.doc for v in getDocumentsByTag(getHollyCouch(), tag)]
        remaining_visiting_groups_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=remaining_visiting_groups_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @require(Any(has_level('pl'), has_level('staff'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view_all(self):
        visiting_groups = [v.doc for v in getAllVisitingGroups(getHollyCouch())]
        remaining_visiting_groups_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        log.debug('view_all')
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=remaining_visiting_groups_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    # in the future, return the maps, but change contents depending on wether the user is logged in or not
    @expose("json")
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def get_all_tags_and_vodb_state_maps(self):
        if getLoggedInUser(request) is None:
            return dict(all_tags={})
        else:
            bokn_status_map_list = []
            for k, v in bokn_status_map.items():
                bokn_status_map_list.append([k, v])
            bokn_status_map_list.sort(self.fn_sort_by_second_item)

            vodb_status_map_list = []
            for k, v in vodb_status_map.items():
                vodb_status_map_list.append([k, v])
            vodb_status_map_list.sort(self.fn_sort_by_second_item)

            return dict(all_tags=[t.key for t in getAllTags(getHollyCouch())],
                        bokn_status_map=bokn_status_map_list,
                        vodb_status_map=vodb_status_map_list)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @validate(validators={'program_state': validators.Int(not_empty=True)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view_program_state(self, program_state=None):
        visiting_groups = [v.doc for v in getVisitingGroupsByBoknstatus(getHollyCouch(), program_state)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @validate(validators={'vodb_state': validators.Int(not_empty=True)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view_vodb_state(self, vodb_state=None):
        visiting_groups = [v.doc for v in getVisitingGroupsByVodbState(getHollyCouch(), vodb_state)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @validate(validators={'period': validators.String(not_empty=False)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def view_period(self, period=None):

        # TODO: refactor so we only show visiting groups in time span given by daterange document.
        if period == '1an':
            from_date = '2022-06-12'
            to_date = '2022-07-17'

            visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(getHollyCouch(), from_date, to_date)]
        elif period == '2an':
            from_date = '2022-07-17'
            to_date = '2022-08-21'
            visiting_groups = [v.doc for v in getVisitingGroupsInDatePeriod(getHollyCouch(), from_date, to_date)]

        else:
            from_date = ''
            to_date = ''
            visiting_groups = [v.doc for v in getAllVisitingGroups(getHollyCouch(), from_date, to_date)]

        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose("json")
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view listing of visiting groups'))
    def get_unbound_visiting_group_names(self, from_date='', to_date=''):
        v_group_map = self.make_remaining_visiting_groups_map([], from_date=from_date, to_date=to_date)
        return dict(names=v_group_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_today(self):
        at_date = datetime.datetime.today().strftime('%Y-%m-%d')
        visiting_groups = [v.doc for v in getVisitingGroupsAtDate(getHollyCouch(), at_date)]
        v_group_map = {}
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    program_state_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    has_notes_map=has_notes_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.view_all')
    @validate(validators={'date': validators.DateValidator(not_empty=False)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group and their properties properties'))
    def view_at_date(self, date=None):
        visiting_groups = [v.doc for v in getVisitingGroupsAtDate(getHollyCouch(), date)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(getHollyCouch())
        return dict(visiting_groups=visiting_groups,
                    remaining_visiting_group_names=v_group_map.keys(),
                    bokn_status_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    all_tags=[t.key for t in getAllTags(getHollyCouch())],
                    has_notes_map=has_notes_map,
                    program_state_map=bokn_status_map,
                    visiting_group_types=getVisitingGroupTypes(getHollyCouch()),
                    languages_map=languages_map)

    @expose("json")
    @validate(validators={'id': validators.UnicodeString})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view listing of visiting groups'))
    def show_visiting_group_data(self, id=None, **kw):
        log.debug('show_visiting_group_data with id "%s"' % str(id))
        properties = []
        if id is None:
            log.info('show_visiting_group_data: id is None')
            visiting_group = dict(name='', id=None, info='')

        elif '' == id:
            log.info('show_visiting_group_data: id is empty string')
            visiting_group = dict(name='', id=None, info='')

        else:
            visiting_group = common_couch.getVisitingGroup(getHollyCouch(), id)

            properties = [p for p in visiting_group['visiting_group_properties'].values()]

        return dict(visiting_group=visiting_group,
                    properties=properties)

    @expose('hollyrosa.templates.visiting_group.view')
    @validate(validators={'visiting_group_id': validators.UnicodeString})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def show_visiting_group(self, visiting_group_id=None, **kw):

        if visiting_group_id is None:
            visiting_group = DataContainer(name='', id=None, info='')
            bookings = []
            notes = []
        elif visiting_group_id == '':
            visiting_group = DataContainer(name='', id=None, info='')
            bookings = []
            notes = []
        else:
            visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)

            # TODO: there is no composite view any more showing both bookings and visiting group data
            bookings = []
            notes = [n.doc for n in getNotesForTarget(getHollyCouch(), visiting_group_id)]
        return dict(visiting_group=visiting_group,
                    bookings=bookings,
                    workflow_map=workflow_map,
                    getRenderContent=getRenderContent,
                    program_state_map=bokn_status_map,
                    vodb_state_map=bokn_status_map,
                    reFormatDate=reFormatDate,
                    notes=notes,
                    languages_map=languages_map)

    @expose('hollyrosa.templates.visiting_group.edit')
    @validate(validators={'visiting_group_id': validators.UnicodeString, 'subtype': validators.UnicodeString})
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def edit_visiting_group(self, visiting_group_id=None, subtype='', **kw):
        tmpl_context.form = create_edit_visiting_group_form

        is_new = ((visiting_group_id is None) or ('' == visiting_group_id))
        if is_new:
            log.info('edit new visiting group')
            properties_template = dict()

            if subtype == 'program':
                properties_template = program_visiting_group_properties_template

            if subtype == 'staff':
                properties_template = staff_visiting_group_properties_template

            if subtype == 'course':
                properties_template = course_visiting_group_properties_template

            visiting_group = dict(name='',
                                  id=None,
                                  _id=None,
                                  info='',
                                  visiting_group_properties=properties_template,
                                  subtype=subtype,
                                  contact_person='',
                                  contact_person_email='',
                                  contact_person_phone='',
                                  boknr='',
                                  language='se-SV')

        else:
            log.info('looking up existing visiting group %s' % str(visiting_group_id))
            visiting_group_c = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
            if 'subtype' not in visiting_group_c:
                visiting_group_c['subtype'] = 'program'
            visiting_group = makeVisitingGroupObjectOfVGDictionary(visiting_group_c)

        return dict(visiting_group=visiting_group,
                    is_new=is_new)

    @expose()
    @validate(create_edit_visiting_group_form, error_handler=edit_visiting_group)
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def save_visiting_group_properties(self,
                                       visiting_group_id=None,
                                       name='',
                                       info='',
                                       from_date=None,
                                       to_date=None,
                                       contact_person='',
                                       contact_person_email='',
                                       contact_person_phone='',
                                       visiting_group_properties=None,
                                       camping_location='',
                                       boknr='',
                                       password='',
                                       subtype='',
                                       language=''):
        log.info('save_visiting_group_properties')

        ensurePostRequest(request, __name__)
        is_new = ((visiting_group_id is None) or (visiting_group_id == ''))

        # this is a hack so we can direct the id of the visiting group for special groups

        if not is_new:
            if 'visiting_group' not in visiting_group_id:
                is_new = True
                id_c = 'visiting_group.' + visiting_group_id
        else:
            id_c = genUID(type='visiting_group')

        if is_new:
            # TODO: make sure subtype is in one of
            if subtype not in ['program', 'course', 'staff']:
                flash('error with subtype')
                raise redirect(request.referrer)

            visiting_group_c = dict(type='visiting_group', subtype=subtype, tags=[], boknstatus=0, vodbstatus=0)
            # populate sheets and computed sheets?

        else:
            id_c = visiting_group_id
            visiting_group_c = getHollyCouch()[id_c]

        visiting_group_c['name'] = name
        visiting_group_c['info'] = cleanHtml(info if info is not None else '')

        ok, ok_from_date = sanitizeDate(from_date)
        if not ok:
            # TODO better error handling here
            flash('error with from-date')
            raise redirect(request.referrer)

        visiting_group_c['from_date'] = ok_from_date

        ok, ok_to_date = sanitizeDate(to_date)
        if not ok:
            # TODO: better error handling here
            flash('error with to-date')
            raise redirect(request.referrer)
        visiting_group_c['to_date'] = ok_to_date

        visiting_group_c['contact_person'] = contact_person
        visiting_group_c['contact_person_email'] = contact_person_email
        visiting_group_c['contact_person_phone'] = contact_person_phone
        visiting_group_c['language'] = language

        # TODO: boknr maybe shouldnt be changeble if program or vodb state has passed by preliminary (10) ?

        visiting_group_c['boknr'] = boknr

        # TODO: password for group should be set in special page
        if password != '':
            visiting_group_c['password'] = password

        visiting_group_c['camping_location'] = camping_location

        # ...now we have to update all cached content, so we need all bookings that belong to this visiting group
        visiting_group_c['visiting_group_properties'] = \
            populatePropertiesAndRemoveUnusedProperties(visiting_group_c, visiting_group_properties)

        updateBookingsCacheContentAfterPropertyChange(getHollyCouch(), visiting_group_c, getLoggedInUserId(request))
        vodb_tag_times_tags = computeAllUsedVisitingGroupsTagsForTagSheet(visiting_group_c['tags'],
                                                                          visiting_group_c.get('vodb_tag_sheet',
                                                                                               dict(items=[]))['items'])
        updateVisitingGroupComputedSheets(visiting_group_c, visiting_group_c['visiting_group_properties'],
                                          sheet_map=dict(vodb_eat_sheet=vodb_eat_times_options,
                                                         vodb_live_sheet=vodb_live_times_options,
                                                         vodb_tag_sheet=vodb_tag_times_tags))

        getHollyCouch()[id_c] = visiting_group_c

        if 'visiting_group_id' in  visiting_group_c:
            raise redirect(
                '/visiting_group/show_visiting_group?visiting_group_id=' + visiting_group_c['visiting_group_id'])
        raise redirect('/visiting_group/view_all')

    @validate(validators={'id': validators.UnicodeString})
    @require(Any(has_level('pl'), msg='Only pl members may delete visiting groups'))
    def delete_visiting_group(self, id=None):
        ensurePostRequest(request, __name__)
        log.info("delete_visiting_group()")
        if id is None:
            pass

        raise redirect('/visiting_group/view_all')

    @expose('hollyrosa.templates.view_bookings_of_name')
    @validate(validators={"visiting_group_id": validators.UnicodeString(),
                          "render_time": validators.UnicodeString(),
                          "hide_comment": validators.Int(),
                          "show_group": validators.Int()})
    @require(Any(has_level('staff'), has_level('view'), has_level('pl'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def view_bookings_of_visiting_group_id(self, visiting_group_id=None, render_time='', hide_comment=0, show_group=0):
        bookings = [b.doc for b in
                    get_bookings_of_visiting_group(getHollyCouch(), '<- MATCHES NO GROUP ->', visiting_group_id)]
        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        return self.view_bookings_of_visiting_group(visiting_group,
                                                    visiting_group_id,
                                                    visiting_group['name'],
                                                    bookings,
                                                    hide_comment=hide_comment,
                                                    show_group=show_group,
                                                    render_time=render_time)

    @expose('hollyrosa.templates.view_bookings_of_name')
    @validate(validators={"name": validators.UnicodeString(),
                          "render_time": validators.UnicodeString(),
                          "hide_comment": validators.Int(),
                          "show_group": validators.Int()})
    @require(Any(has_level('staff'), has_level('view'), has_level('pl'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def view_bookings_of_name(self, name=None, render_time='', hide_comment=0, show_group=0):
        # TODO: its now possible to get bookings on both name and id
        bookings = [b.doc for b in get_bookings_of_visiting_group(getHollyCouch(), name, '<- MATCHES NO GROUP ->')]

        visiting_group_id = None
        visiting_group = [v.doc for v in getVisitingGroupOfVisitingGroupName(getHollyCouch(), name)]
        if len(visiting_group) > 1:
            log.error("two visiting groups with the same name")

        if len(visiting_group) == 1:
            visiting_group_id = visiting_group[0]['_id']
            first_visiting_group = visiting_group[0]

        return self.view_bookings_of_visiting_group(first_visiting_group,
                                                    visiting_group_id,
                                                    name,
                                                    bookings,
                                                    hide_comment=hide_comment,
                                                    show_group=show_group,
                                                    render_time=render_time)

    @expose()
    @validate(validators={"visiting_group_id": validators.UnicodeString(), "doc_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members may view visiting group attachments'))
    def download_attachment(self, visiting_group_id, doc_id):
        response.content_type = 'x-application/download'
        response.headerlist.append(('Content-Disposition', 'attachment;filename=%s' % doc_id))

        return getHollyCouch().get_attachment(visiting_group_id, doc_id).read()

    @expose('hollyrosa.templates.edit_visiting_group_vodb_data')
    @validate(validators={"id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'),
                 msg='Only staff members and viewers may view visiting group properties'))
    def edit_vodb_data(self, id):
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), id)
        return dict(visiting_group=vgroup)

    def do_set_program_state(self, holly_couch, visiting_group_id, visiting_group_o, state):
        visiting_group_o['boknstatus'] = state
        holly_couch[visiting_group_id] = visiting_group_o

        # ..TODO: remember state change

        # TODO: only PL can set state=20 (approved) or -10 (disapproved)

        ##if state=='20' or state=='-10' or booking_o['booking_state'] == 20 or booking_o['booking_state']==-10:
        # ok = False
        # for group in getLoggedInUserId(request):
        #    if group.group_name == 'pl':
        #        ok = True
        ##ok = has_level('pl').check_authorization(request.environ)

        # TODO: fix

    #            if not ok:
    #                flash('Only PL can do that. %s' % request.referrer, 'warning')
    #                raise redirect(request.referrer)
    ##activity = holly_couch[booking_o['activity_id']]
    ##booking_day = holly_couch[booking_o['booking_day_id']]

    ##booking_o['booking_state'] = state
    ##booking_o['last_changed_by_id'] = getLoggedInUserId(request)

    ##holly_couch[booking_id] = booking_o
    ##remember_workflow_state_change(holly_couch, booking=booking_o, state=state,  booking_day_date=booking_day['date'],  activity_title=activity['title'])

    def do_set_vodb_state(self, holly_couch, visiting_group_id, visiting_group_o, state):
        visiting_group_o['vodbstatus'] = state
        holly_couch[visiting_group_id] = visiting_group_o

    @expose()
    @validate(validators={'visiting_group_id': validators.UnicodeString(not_empty=True),
                          'state': validators.Int(not_empty=True)})
    @require(Any(has_level('staff'), has_level('pl'),
                 msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def set_program_state(self, visiting_group_id=None, state=0):
        log.info("set_program_state()")
        ensurePostRequest(request, __name__)
        visiting_group_o = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        self.do_set_program_state(getHollyCouch(), visiting_group_id, visiting_group_o, int(state))
        raise redirect(request.referrer)

    @expose()
    @validate(validators={'visiting_group_id': validators.UnicodeString(not_empty=True),
                          'state': validators.Int(not_empty=True)})
    @require(Any(has_level('staff'), has_level('pl'),
                 msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def set_vodb_state(self, visiting_group_id=None, state=0):
        log.info("set_vodb_state()")
        ensurePostRequest(request, __name__)
        visiting_group_o = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        self.do_set_vodb_state(getHollyCouch(), visiting_group_id, visiting_group_o, int(state))
        raise redirect(request.referrer)

    @expose()
    @validate(validators={'visiting_group_id': validators.UnicodeString(not_empty=True)})
    @require(Any(has_level('staff'), has_level('pl'),
                 msg='Only PL or staff members can change booking state, and only PL can approve/disapprove'))
    def copy_vodb_contact_info(self, visiting_group_id=None):
        log.info("copy_vodb_contact_info()")
        ensurePostRequest(request, __name__)
        visiting_group_o = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)

        if visiting_group_o.get('contact_person', '') == '':
            visiting_group_o['contact_person'] = visiting_group_o.get('vodb_contact_name', '')
        if visiting_group_o.get('contact_person_email', '') == '':
            visiting_group_o['contact_person_email'] = visiting_group_o.get('vodb_contact_email', '')
        if visiting_group_o.get('contact_person_phone', '') == '':
            visiting_group_o['contact_person_phone'] = visiting_group_o.get('vodb_contact_phone', '')
        getHollyCouch()[visiting_group_id] = visiting_group_o
        raise redirect(request.referrer)
