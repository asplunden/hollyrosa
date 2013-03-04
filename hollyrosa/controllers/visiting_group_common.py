# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012, 2013 Martin Eliasson

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

from hollyrosa.model.booking_couch import genUID, getBookingDayOfDate, getSchemaSlotActivityMap, getVisitingGroupByBoknr, getAllVisitingGroups, getTargetNumberOfNotesMap, getAllTags, getNotesForTarget, getBookingsOfVisitingGroup, getBookingOverview, getBookingEatOverview, getDocumentsByTag, getVisitingGroupsByVodbState, getVisitingGroupsByBoknstatus, dateRange
from hollyrosa.controllers.common import workflow_map,  bokn_status_map, bokn_status_options,  DataContainer,  getRenderContent, computeCacheContent,  has_level,  reFormatDate, getLoggedInUserId

def updateBookingsCacheContentAfterPropertyChange(a_holly_couch, a_visiting_group,  logged_in_user_id):
    """after propertes have been changed, the bookings needs to have their cache content updated"""
    # TODO: if cachecontent changes, should we change booking status or somehow mark it?
    l_visiting_group_name = a_visiting_group['name']
    l_visiting_group_id = a_visiting_group['_id']
    bookings = getBookingsOfVisitingGroup(a_holly_couch, a_visiting_group.id,  None)
    for tmp in bookings:
        tmp_booking = tmp.doc
        
        new_content = computeCacheContent(a_visiting_group, tmp_booking['content'])
        if new_content != tmp_booking['cache_content'] :

            if new_content != tmp_booking['cache_content']:
                tmp_booking['cache_content'] = new_content
                tmp_booking['last_changed_by'] = logged_in_user_id 
                
                #...we need booking day of booking if it exists
                
                
                remember_booking_vgroup_properties_change(holly_couch, booking=tmp_booking, visiting_group_id=l_visiting_group_id,  visiting_group_name=l_visiting_group_name, changed_by=logged_in_user_id,  activity_title=a_holly_couch[tmp_booking['activity_id']]['title'])
                holly_couch[tmp_booking['_id']] = tmp_booking


def populatePropertiesAndRemoveUnusedProperties(a_visiting_group,  a_visiting_group_properties):
    """used when a property dict is obtained from edit_vodb group or edit vgroup forms"""
    visiting_group_property_o = dict()

    #...remove non-used params
    unused_params = {}        
    used_param_ids = []
    if  a_visiting_group.has_key('visiting_group_properties'):
        used_param_ids = a_visiting_group['visiting_group_properties'].keys()
    
    for param in a_visiting_group_properties:
        is_new_param = False
        if param['property'] != '' and param['property'] != None:
            if param['id'] != '' and param['id'] != None:
                visiting_group_property_o[param['id']] = dict(property=param['property'],  value=param.get('value',''),  description=param.get('description',''),  unit=param.get('unit',''),  from_date=str(param['from_date']),  to_date=str(param['to_date']))
            else:
                #...compute new unsued id
                # TODO: these ids are not perfectly unique. It could be a problem with dojo grid
                
                largest_int = max(used_param_ids)
                new_id_int = largest_int + 1
                #while str(new_id_int) in used_param_ids:
                #    new_id_int += 1
                used_param_ids.append(str(new_id_int))
                
                visiting_group_property_o[str(new_id_int)] = dict(property=param['property'],  value=param.get('value',''),  description=param.get('description',''),  unit=param.get('unit',''),  from_date=str(param['from_date']),  to_date=str(param['to_date']))
                
    # TODO: we need to add to history how params are changed and what it affects
    return visiting_group_property_o
