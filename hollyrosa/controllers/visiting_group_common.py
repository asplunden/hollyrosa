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
import copy
import types

from hollyrosa.controllers.booking_history import remember_booking_vgroup_properties_change
from hollyrosa.controllers.common import computeCacheContent, sanitizeDate
from hollyrosa.model.booking_couch import getBookingsOfVisitingGroup

program_visiting_group_properties_template = [
    dict(property='sma', value='0', unit=u'småbarn', description=u'antal deltagare 0 till 8 år'),
    dict(property='spar', value='0', unit=u'spår', description=u'antal deltagare 8 till 9 år'),
    dict(property='uppt', value='0', unit=u'uppt', description=u'antal deltagare 10 till 11 år'),
    dict(property='aven', value='0', unit=u'aven', description=u'antal deltagare 12 till 15 år'),
    dict(property='utm', value='0', unit=u'utm', description=u'antal deltagare 16 till 18 år'),
    dict(property='rov', value='0', unit=u'rover', description=u'antal roverscouter'),
    dict(property='led', value='0', unit=u'ledare', description=u'antal ledare'),
    dict(property='antal', value='0', unit=u'antal', description=u'preliminärt uppskattat antal')]

staff_visiting_group_properties_template = [dict(property='funk', value='1', unit=u'funk', description=u'antal funk'),
                                            dict(property='barn', value='0', unit=u'fkbarn',
                                                 description=u'antal funk barn')]

course_visiting_group_properties_template = [
    dict(property='SSD', value='0', unit=u'SSD', description=u'antal kursdeltagare från SSD'),
    dict(property='scout', value='0', unit=u'scout', description=u'antal kursdeltagare från scouterna (utom SSD)'),
    dict(property='ovr', value='0', unit=u'övriga', description=u'antal övriga kursdeltagare'),
    dict(property='led', value='0', unit=u'kursled', description=u'antal kursledare'),
    dict(property='barn', value='0', unit=u'klbarn', description=u'antal kursledarbarn')]


def updateBookingsCacheContentAfterPropertyChange(a_holly_couch, a_visiting_group, logged_in_user_id):
    """after propertes have been changed, the bookings needs to have their cache content updated"""
    # TODO: if cachecontent changes, should we change booking status or somehow mark it?

    is_new_group = not a_visiting_group.has_key('_id')
    if is_new_group:
        return

    l_visiting_group_name = a_visiting_group['name']
    l_visiting_group_id = a_visiting_group['_id']
    bookings = getBookingsOfVisitingGroup(a_holly_couch, a_visiting_group.id, None)
    for tmp in bookings:
        tmp_booking = tmp.doc

        new_content = computeCacheContent(a_visiting_group, tmp_booking['content'])
        if new_content != tmp_booking['cache_content']:

            if new_content != tmp_booking['cache_content']:
                tmp_booking['cache_content'] = new_content
                tmp_booking['last_changed_by'] = logged_in_user_id

                # ...we need booking day of booking if it exists

                remember_booking_vgroup_properties_change(a_holly_couch, booking=tmp_booking,
                                                          visiting_group_id=l_visiting_group_id,
                                                          visiting_group_name=l_visiting_group_name,
                                                          changed_by=logged_in_user_id,
                                                          activity_title=a_holly_couch[tmp_booking['activity_id']][
                                                              'title'])
                a_holly_couch[tmp_booking['_id']] = tmp_booking


def populatePropertiesAndRemoveUnusedProperties(a_visiting_group, a_visiting_group_properties):
    """used when a property dict is obtained from edit_vodb group or edit vgroup forms"""
    visiting_group_property_o = dict()

    # ...remove non-used params
    unused_params = {}
    used_param_ids = []
    if a_visiting_group.has_key('visiting_group_properties'):
        used_param_ids = a_visiting_group['visiting_group_properties'].keys()

    for param in a_visiting_group_properties:
        is_new_param = False
        if param['property'] != '' and param['property'] is not None:
            if param['property_id'] != '' and param['property_id'] is not None:
                visiting_group_property_o[param['property_id']] = dict(property=param['property'],
                                                                       value=param.get('value', ''),
                                                                       description=param.get('description', ''),
                                                                       unit=param.get('unit', ''),
                                                                       from_date=sanitizeDate(param['from_date'])[1],
                                                                       to_date=sanitizeDate(param['to_date'])[
                                                                           1])  # TODO: better error handling of sanitieDate
            else:
                # ...compute new unsued id
                # TODO: these ids are not perfectly unique. It could be a problem with dojo grid

                if len(used_param_ids) > 0:
                    largest_int = max([int(i) for i in used_param_ids])
                else:
                    largest_int = 0

                new_id_int = largest_int + 1
                # while str(new_id_int) in used_param_ids:
                #    new_id_int += 1
                used_param_ids.append(str(new_id_int))

                visiting_group_property_o[str(new_id_int)] = dict(property=param['property'],
                                                                  value=param.get('value', ''),
                                                                  description=param.get('description', ''),
                                                                  unit=param.get('unit', ''),
                                                                  from_date=sanitizeDate(param['from_date'])[1],
                                                                  to_date=sanitizeDate(param['to_date'])[
                                                                      1])  # TODO: the usage of sanitizeDate is a little loose I think

    # TODO: we need to add to history how params are changed and what it affects
    return visiting_group_property_o


def visitingGroupPropertyVODBSheetSubstitutionHelper(rows, headers, properties):
    """
    """
    for row in rows:
        for k in headers:
            original_value = row.get(k, 0)
            new_value = original_value

            if type(new_value) == types.StringType or type(new_value) == types.UnicodeType:
                for prop in properties.values():
                    prop_prop = prop['property']
                    # todo: WARN IF DATE IS OUTSIDE RANGE

                    prop_value = prop['value']
                    if prop_value is not None:
                        new_value = new_value.replace(u'$' + prop_prop, prop_value)

                try:
                    new_value = str(eval(new_value, {"__builtins__": None}, {}))
                except ValueError:
                    pass
                except SyntaxError:
                    pass
            row[k] = new_value


def visitingGroupPropertyVODBSheetSubstitution(a_visiting_group, a_options, a_visiting_group_properties, a_sheet_name):
    if a_visiting_group.has_key(a_sheet_name):
        vodb_sheet = a_visiting_group[a_sheet_name]
        vodb_sheet_copy = copy.deepcopy(vodb_sheet)
        vodb_computed = vodb_sheet_copy['items']
        visitingGroupPropertyVODBSheetSubstitutionHelper(vodb_computed, a_options, a_visiting_group_properties)
        a_visiting_group[a_sheet_name.replace('sheet', 'computed')] = vodb_computed


def updateVisitingGroupComputedSheets(a_visiting_group, a_visiting_group_properties, sheet_map={}):
    """call this function whenever the sheets or the properties of a visiting groups has changed"""
    for sheet_name, options in sheet_map.items():
        visitingGroupPropertyVODBSheetSubstitution(a_visiting_group, options, a_visiting_group_properties, sheet_name)


def computeAllUsedVisitingGroupsTagsForTagSheet(tags, rows):
    all_current_vgroup_tags = dict()
    for tmp_key in tags:
        all_current_vgroup_tags[tmp_key] = 1

    for tmp_row in rows:
        for tmp_key in tmp_row.keys():
            if (tmp_key != 'date') and (tmp_key != 'time'):
                if not all_current_vgroup_tags.has_key(tmp_key):
                    all_current_vgroup_tags[tmp_key] = 1
    return all_current_vgroup_tags
