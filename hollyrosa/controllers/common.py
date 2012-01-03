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


from hollyrosa.model import booking

workflow_map = dict()
workflow_map[10] ='booked'
workflow_map[20] ='approved'
workflow_map[0] = 'preliminary'
workflow_map[-10] ='disapproved'    
workflow_map[-100] ='deleted'

change_op_lookup = {'schedule':1, 'unschedule':2, 'book_slot':3,  'new_booking_request':4,  'booking_request_change':5,  'delete_booking_request':6,  'booking_properties_change':7,  'booking_state_change':8, 'block_soft':9,  'block_hard':10,  'unblock':11,  'workflow_state_change':12}

change_op_map = dict()
for k,  v in change_op_lookup.items():
    change_op_map[v] = k.replace('_',' ')



def getFormatedDate(date_obj):
    if None == date_obj:
        return ''
    else:
        return date_obj.strftime('%A %d %B')

def getRenderContent(booking):
    if booking.cache_content=='' or booking.cache_content == None:
        return booking.content
    else:
        return booking.cache_content
        
def getRenderContentDict(booking):
    if booking['cache_content']=='' or booking['cache_content'] == None:
        return booking['content']
    else:
        return booking['cache_content']

class DataContainer(object):
    def __init__(self, **kwds):
        for k, v in kwds.items():
            self.__setattr__(k, v)
            
            
class DummyIdentity(object):
    def __init__(self):
        self.display_name = 'not logged in'
dummy_identity = DummyIdentity()


def getLoggedInDisplayName(request):
    return request.identity.get('user', dummy_identity).display_name
    
def getLoggedInUser(request):
    return request.identity.get('user', None)
    
def computeCacheContent(dbsession, content,  visiting_group_id):
    """
    Generate cached content must be done here. Only visiting groups that exists (has a visiting group) can be rendered using property substitution.
        
    $param is substituted for the value
    #param is substutured for the unit
    $#param or $$param is substituted for it all
        
    TODO: copied for booking_day.py , how share it between all?
    """
    if visiting_group_id != None:
        cache_content = content
        the_visiting_group = dbsession[visiting_group_id] #dbsession.query(booking.VisitingGroup).filter('id='+str(visiting_group_id)).one()
        for tmp_property in the_visiting_group['visiting_group_properties'].values():
            tmp_unit = tmp_property['unit']
            if tmp_unit == None:
                tmp_unit = '' 
            tmp_value = tmp_property['value']
            if tmp_value == None:
                tmp_value = ''
            cache_content = cache_content.replace('$$'+tmp_property['property'],  tmp_value + " " + tmp_unit)
            cache_content = cache_content.replace('$#'+tmp_property['property'],  tmp_value + " " + tmp_unit)
            cache_content = cache_content.replace('$'+tmp_property['property'],  tmp_value)
            cache_content = cache_content.replace('#'+tmp_property['property'],  tmp_unit)
    else:
        cache_content = content
            
    return cache_content
