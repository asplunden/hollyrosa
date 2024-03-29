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

import json
import logging

from formencode import validators
from hollyrosa.controllers import common_couch
from hollyrosa.controllers.common import bokn_status_map, default_language, DataContainer, \
    has_level, reFormatDate, hide_cache_content_in_booking, ensurePostRequest
from hollyrosa.lib.base import BaseController
from hollyrosa.model import genUID, getHollyCouch
from hollyrosa.model.booking_couch import dateRange
from hollyrosa.model.booking_couch import getVisitingGroupsInDatePeriod, getAllProgramLayerBucketTexts, \
    get_bookings_of_visiting_group, getAllActivities, getBookingDays, getActivityTitleMap, \
    get_booking_info_notes_with_matched_language, getNotesForTarget
from tg import expose, require, request, redirect, validate
from tg.predicates import Any

__all__ = ['ProgramLayer']

log = logging.getLogger()


class ProgramLayer(BaseController):

    @expose('hollyrosa.templates.visiting_group.edit_layers')
    @validate(validators={"visiting_group_id": validators.UnicodeString()})
    @require(Any(has_level('staff'), has_level('pl'), msg='Only PL and staff members may change layers configuration'))
    def edit_layers(self, visiting_group_id):
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        vgroup_layers = vgroup.get('layers', list())

        # ...make map of layers from list of layers, keyed on id
        vgroup_layers_map = dict()
        for tmp_vgroup_layer in vgroup_layers:
            vgroup_layers_map[tmp_vgroup_layer['layer_id']] = tmp_vgroup_layer

        # ...get all visiting group that possibly could be mapped
        vgroups_in_daterange = getVisitingGroupsInDatePeriod(getHollyCouch(), vgroup['from_date'], vgroup['to_date'])

        # ...build data struct for dojo spreadsheet / grid
        grid_items = list()
        for tmp_vgroup_row in vgroups_in_daterange:
            tmp_vgroup = tmp_vgroup_row.doc
            if tmp_vgroup['_id'] != vgroup['_id']:
                if tmp_vgroup['_id'] in vgroup_layers_map.keys():
                    grid_items.append(dict(layer_id=tmp_vgroup['_id'], name=tmp_vgroup['name'], connect=True,
                                           colour=vgroup_layers_map[tmp_vgroup['_id']]['colour']))  # change colours
                else:
                    grid_items.append(
                        dict(layer_id=tmp_vgroup['_id'], name=tmp_vgroup['name'], connect=False, colour="#fff"))

        grid_data = dict(identifier='layer_id', items=grid_items)
        layer_data = json.dumps(grid_data)
        return dict(visiting_group=vgroup, layer_data=layer_data, reFormatDate=reFormatDate)

    @expose()
    @validate(validators={"visiting_group_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), msg='Only PL may change layers configuration'))
    def update_visiting_group_program_layers(self, visiting_group_id, save_button=None, layer_data=''):
        log.info("update_visiting_group_program_layers")
        ensurePostRequest(request, __name__)
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        vgroup_layers = vgroup.get('layers', list())

        layer_json = json.loads(layer_data)
        layer_to_save = list()

        for tmp_layer_data in layer_json['items']:
            if tmp_layer_data['connect']:
                layer_to_save.append(dict(layer_id=tmp_layer_data['layer_id'], colour=tmp_layer_data['colour'],
                                          name=tmp_layer_data['name']))

        vgroup['layers'] = layer_to_save
        getHollyCouch()[vgroup['_id']] = vgroup
        raise redirect(request.referer)

    @expose('hollyrosa.templates.visiting_group.program_booking_layers')
    @validate(validators={"visiting_group_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def layers(self, visiting_group_id):
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        notes = [n.doc for n in getNotesForTarget(getHollyCouch(), visiting_group_id)]
        return dict(visiting_group=vgroup,
                    notes=notes,
                    tags=[],
                    reFormatDate=reFormatDate,
                    program_state_map=bokn_status_map)

    def get_program_layer_bookings(self, visiting_group, layer_title, layer_colour):
        bookings = []
        for tmp in get_bookings_of_visiting_group(getHollyCouch(), visiting_group['name'], '<- MATCHES NO GROUP ->'):
            tmp_doc = tmp.doc
            tmp_doc['layer_title'] = layer_title
            tmp_doc['layer_colour'] = layer_colour
            bookings.append(tmp_doc)
        return bookings

    @expose('hollyrosa.templates.program_booking_layers_show_printable_table')
    @validate(validators={"visiting_group_id": validators.UnicodeString(), "hide_comment": validators.Int()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def layers_printable(self, visiting_group_id, hide_comment=1):
        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)

        date_range = dateRange(visiting_group['from_date'], visiting_group['to_date'])
        number_of_days = len(date_range)
        width_ratio = (100.0 / (number_of_days + 1))

        # ...TODO organize bookings per layer bucket
        result = self.program_layer_get_days_helper(visiting_group_id)

        result['notes'] = []
        result['tags'] = []
        result['reFormatDate'] = reFormatDate
        result['visiting_group'] = visiting_group

        slot_id_time_id_map = result['slot_id_time_map']
        bookings = dict()

        layers = visiting_group.get('layers', list())

        layers.append(dict(title=visiting_group['name'], colour='#ffe', layer_id=visiting_group_id))
        unscheduled_bookings = []

        # ...code repeat for making used_activities
        activities = dict()
        used_activities_keys = dict()
        for x in getAllActivities(getHollyCouch()):
            activities[x.key[1]] = x.doc

        for tmp_layer in layers:
            tmp_visiting_group = common_couch.getVisitingGroup(getHollyCouch(), tmp_layer['layer_id'])
            bookings_list = self.get_program_layer_bookings(tmp_visiting_group, tmp_visiting_group['name'],
                                                            tmp_layer['colour'])

            for tmp_booking in bookings_list:
                tmp_booking['layer_colour'] = tmp_layer['colour']
                if '' != tmp_booking['slot_id']:
                    tmp_time_id = slot_id_time_id_map[tmp_booking['slot_id']]

                    hide_cache_content_in_booking(tmp_booking)

                    tmp_id = tmp_booking['booking_day_id'] + ':' + tmp_time_id
                    if tmp_id not in bookings:
                        bookings[tmp_id] = list()
                    bookings[tmp_id].append(tmp_booking)
                else:
                    hide_cache_content_in_booking(tmp_booking)
                    unscheduled_bookings.append(tmp_booking)

                # ...fix used activities
                used_activities_keys[tmp_booking['activity_id']] = 1
                used_activities_keys[activities[tmp_booking['activity_id']]['activity_group_id']] = 1

        result['bookings'] = bookings
        result['width_ratio'] = width_ratio

        result['unscheduled_bookings'] = unscheduled_bookings
        visiting_group_language = visiting_group.get('language', default_language)
        result['booking_info_notes'] = get_booking_info_notes_with_matched_language(getHollyCouch(),
                                                                                    used_activities_keys,
                                                                                    visiting_group_language)
        return result

    @expose("json")
    @validate(validators={"visiting_group_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_get_days(self, visiting_group_id):
        return self.program_layer_get_days_helper(visiting_group_id)

    def getTimeIdMapping(self):
        time_id_mapping = dict(FM='fm', EM='em')
        time_id_mapping[u'Kväll'] = 'eve'
        time_id_mapping['After hours'] = 'afh'
        return time_id_mapping

    def fillInGeneralizedSlotRow(self, time_id_mapping, any_slot_row_in_schema, generalized_slot_row, layer_times):
        for tmp_slot_row in any_slot_row_in_schema:
            tmp_item = {}
            for k, v in tmp_slot_row.items():
                if k != 'slot_id':
                    tmp_item[k] = v
                if k == 'title':
                    layer_times.append(dict(title=v, symbol=time_id_mapping[v]))

            generalized_slot_row.append(tmp_item)

    def program_layer_get_days_helper(self, visiting_group_id):
        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)

        # ...create temporary mapping title-> id, in the future, this should be based on time rather on the title (
        # which can be dangerous)
        time_id_mapping = self.getTimeIdMapping()

        booking_days = [bd.doc for bd in
                        getBookingDays(getHollyCouch(), visiting_group['from_date'], visiting_group['to_date'])]
        schema_id_map = dict()
        for b in booking_days:
            schema_id_map[b['day_schema_id']] = b

        # ...now, if we have too many day schema ids, we have a problem...
        # TODO dangerous below, we can have diffreent schemas for different days
        first_booking_day = booking_days[0]

        schema_id = first_booking_day['day_schema_id']
        schema_doc = getHollyCouch()[schema_id]
        schema = schema_doc['schema']

        # ...if we assume the same layout for every slot row, we can get first row in schema and use it as template
        any_slot_row_in_schema = schema[list(schema.keys())[0]][
                                 1:]  # skip first part, now we have four time-slots that can be used

        # ...it would be best if we now could clean out the slot_id from the mapping
        generalized_slot_row = []
        layer_times = []

        # ...will change its parameters
        self.fillInGeneralizedSlotRow(time_id_mapping, any_slot_row_in_schema, generalized_slot_row, layer_times)

        # ...iterate through schema and find FM EM etc
        # iterate through schema and find the slot_id maping.

        layer_days = []
        for d in booking_days:
            tmp_item = dict(booking_day_id=d['_id'], date=d['date'])
            layer_days.append(tmp_item)

        # ...
        program_layers = visiting_group.get('layers', [])

        # ...I need to build this mapping from booking_day_id:slot_id:layer_id to datetime bucket
        #   so iterate through all schema rows and look at time,
        slot_id_time_map = {}
        for tmp_schema_id in schema_id_map.keys():
            tmp_schema_doc = getHollyCouch()[tmp_schema_id]
            tmp_schema = tmp_schema_doc['schema']

            for tmp_activity_id, tmp_activity_row in tmp_schema.items():
                for tmp_slot in tmp_activity_row[1:]:
                    tmp_time = tmp_slot['title']
                    slot_id_time_map[tmp_slot['slot_id']] = time_id_mapping[tmp_time]

        # TODO return activity title map
        activity_title_map = getActivityTitleMap(getHollyCouch())

        return dict(layer_time=layer_times, layer_days=layer_days, slot_id_time_map=slot_id_time_map,
                    visiting_group_id=visiting_group_id, activity_title_map=activity_title_map,
                    program_layers=program_layers)

    @expose("json")
    @validate(validators={"visiting_group_id": validators.UnicodeString(), "layer_title": validators.UnicodeString(),
                          "layer_colour": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_get_bookings(self, visiting_group_id, layer_title='', layer_colour='#fff'):
        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        bookings = self.get_program_layer_bookings(visiting_group, layer_title, layer_colour)

        processed_bookings = list()
        for b in bookings:
            hide_cache_content_in_booking(b)
            processed_bookings.append(b)

        bucket_texts = []
        for tmp in getAllProgramLayerBucketTexts(getHollyCouch(), visiting_group_id):
            tmp_doc = tmp.doc
            tmp_doc['layer_title'] = visiting_group['name']
            tmp_doc['layer_colour'] = '#fff'  # layer_colour

            # TODO: check if we want to hide comments. Really. Probably more dependent on who is logged in. Like
            #  program staff or visiting group
            bucket_texts.append(tmp_doc)

        return dict(bookings=processed_bookings, bucket_texts=bucket_texts)

    @expose("json")
    @validate(validators={"visiting_group_id": validators.UnicodeString(), "layer_text_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_edit_text(self, visiting_group_id, layer_text_id=''):
        is_new = (layer_text_id == '')

        if is_new:
            layer_text = DataContainer(text='', title='', program_layer_text_id='', state=0)
        else:
            layer_text = common_couch.getLayerText(getHollyCouch(), layer_text_id)

        return dict(layer_text=layer_text)

    @expose("json")
    @validate(validators={"visiting_group_id": validators.UnicodeString(), "booking_day_id": validators.UnicodeString(),
                          "bucket_time": validators.UnicodeString(), "layer_text_id": validators.UnicodeString(),
                          "text": validators.UnicodeString(), "title": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_save_layer_text(self, visiting_group_id='', booking_day_id='', bucket_time='', layer_text_id='',
                                      text='', title=''):
        log.info("program_layer_save_layer_text")
        ensurePostRequest(request, __name__)
        is_new = (layer_text_id == '')

        if is_new:
            id = genUID(type='program_layer_text')

            # ...if slot_id is none, we need to figure out slot_id of bucket_time OR we simply save bucket_time

            layer_text = dict(type='program_layer_text', subtype='layer_text', state=0, booking_day_id=booking_day_id,
                              bucket_time=bucket_time)
            # ...populate sheets and computed sheets?

            layer_text['text'] = text
            layer_text['title'] = title
            layer_text['visiting_group_id'] = visiting_group_id
            getHollyCouch()[id] = layer_text
        else:
            layer_text = common_couch.getLayerText(getHollyCouch(), layer_text_id)

            layer_text['text'] = text
            layer_text['title'] = title
            getHollyCouch()[layer_text['_id']] = layer_text
            # TODO call it bucket text or layer text ?

        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        layer_text['layer_title'] = visiting_group['name']
        layer_text['layer_colour'] = "#fff"
        return dict(layer_text=layer_text)

    @expose("json")
    @validate(validators={"visiting_group_id": validators.UnicodeString(), "booking_day_id": validators.UnicodeString(),
                          "bucket_time": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_new_layer_text(self, visiting_group_id='', booking_day_id='', bucket_time=''):
        layer_text = dict(type='program_layer_text', subtype='layer_text', status=0, booking_day_id=booking_day_id,
                          bucket_time=bucket_time, text='', title='', visiting_group_id=visiting_group_id)
        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), visiting_group_id)
        layer_text['layer_title'] = visiting_group['name']
        layer_text['layer_colour'] = "#fff"
        return dict(layer_text=layer_text)

    @expose("json")
    @validate(validators={"layer_text_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_get_layer_text(self, layer_text_id=''):
        layer_text = common_couch.getLayerText(getHollyCouch(), layer_text_id)
        visiting_group = common_couch.getVisitingGroup(getHollyCouch(), layer_text['visiting_group_id'])

        layer_text['layer_title'] = visiting_group['name']
        layer_text['layer_colour'] = "#fff"
        layer_text['layer_text_id'] = layer_text['_id']
        return dict(layer_text=layer_text)

    @expose("json")
    @validate(validators={"layer_text_id": validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('vgroup'),
                 msg=u'Du måste vara inloggad för att få tillgång till program lagren'))
    def program_layer_delete_layer_text(self, layer_text_id):
        log.info("program_layer_delete_layer_text()")
        ensurePostRequest(request, __name__)
        layer_text = common_couch.getLayerText(getHollyCouch(), layer_text_id)
        layer_text['state'] = -100
        getHollyCouch()[layer_text_id] = layer_text
        return dict()
