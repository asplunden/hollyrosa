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

Note: functions in this module should rarely if ever access holly_couch (couch db), instead, put such methods in the common_couch.py module
"""


from hollyrosa.model import booking

from repoze.what.predicates import Predicate
import datetime



workflow_map = dict()
workflow_map[5]='stand-by'
workflow_map[10]='booked'
workflow_map[20] ='approved'
workflow_map[30]='drop-in'
workflow_map[0] ='preliminary'
workflow_map[-10]='disapproved'
workflow_map[-100] ='deleted'

bokn_status_map = dict()
bokn_status_map[-100] ='deleted'
bokn_status_map[-10] ='canceled'
bokn_status_map[0] ='new'
bokn_status_map[5] ='created'
bokn_status_map[10] ='preliminary'
bokn_status_map[20] ='confirmed'
bokn_status_map[50] ='island'

vodb_status_map = dict()
vodb_status_map[-100] ='deleted'
vodb_status_map[-10] ='canceled'
vodb_status_map[0] ='new'
vodb_status_map[5] ='created'
vodb_status_map[10] ='preliminary'
vodb_status_map[20] ='confirmed'
vodb_status_map[50] ='island'

bokn_status_options = list()
for k, v in bokn_status_map.items():
    bokn_status_options.append((k, v))

change_op_lookup = {'schedule':1, 'unschedule':2, 'book_slot':3,  'new_booking_request':4,  'booking_request_change':5,  'delete_booking_request':6,  'booking_properties_change':7,  'booking_state_change':8, 'block_soft':9,  'block_hard':10,  'unblock':11,  'workflow_state_change':12, 'tag_change':13, 'note_change':14}

change_op_map = dict()
for k,  v in change_op_lookup.items():
    change_op_map[v] = k.replace('_',' ')


vodb_eat_times_options = [u'indoor', u'outdoor', u'own']
vodb_live_times_options = [u'indoor',u'outdoor',u'daytrip']


def sanitizeDate(d,  default_date=''):
    """Make sure d is on the form YYYY-mm-dd"""
    # TODO we really should use formenc validate here
    
    try:
        #...only use first ten chars
        d_trunc = d[:10]
        d_pars = datetime.datetime.strptime(d_trunc, '%Y-%m-%d')
        return True,  d_pars.strftime('%Y-%m-%d')
    except ValueError:
        return False, default_date
        
        
def reFormatDate(b):
    try:
        r = datetime.datetime.strptime(b, '%Y-%m-%d').strftime('%A %d %B')
    except:
        r = b
    return r
    

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
    """
    TODO: Describe here
    """
    def __init__(self, **kwds):
        for k, v in kwds.items():
            self.__setattr__(k, v)
   
    def has_key(self, key):
        return self.__hasattr__(key)
        
    def __getitem__(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            raise KeyError, 'key "%s" not found' % key
            
class DummyIdentity(object):
    def __init__(self):
        self.display_name = 'not logged in'
dummy_identity = DummyIdentity()


def getLoggedInDisplayName(request):
    return request.identity.get('user', dummy_identity)['display_name']
    
    
def getLoggedInUser(request):
    return request.identity.get('user', None)
    
    
def getLoggedInUserId(request):
    return request.identity.get('user', None)['_id']
    
    
def computeCacheContent(visiting_group, content):
    """
    Generate cached content must be done here. Only visiting groups that exists (has a visiting group) can be rendered using property substitution.
        
    $param is substituted for the value
    #param is substutured for the unit
    $#param or $$param is substituted for it all
        
    TODO: copied for booking_day.py , how share it between all?
    """
    # TODO: this is very wastefull when updating visiting groups which already are loaded from the couch database
    if visiting_group != None:
        cache_content = content
         
        for tmp_property in visiting_group['visiting_group_properties'].values():
            tmp_unit = tmp_property['unit']
            if tmp_unit == None:
                tmp_unit = '' 
            tmp_value = tmp_property['value']
            if tmp_value == None:
                tmp_value = ''
            cache_content = cache_content.replace('$$'+tmp_property['property'],  str(tmp_value) + " " + tmp_unit)
            cache_content = cache_content.replace('$#'+tmp_property['property'],  str(tmp_value) + " " + tmp_unit)
            cache_content = cache_content.replace('$'+tmp_property['property'],  str(tmp_value))
            cache_content = cache_content.replace('#'+tmp_property['property'],  tmp_unit)
    else:
        cache_content = content
            
    return cache_content






class has_level(Predicate):
    message = 'Only for users with level %s'

    def __init__(self, level, **kwargs):
        super(has_level, self).__init__(**kwargs)
        self.level = level


    def evaluate(self, environ, credentials):
        
        if not environ.has_key('repoze.who.identity'):
            self.unmet(level=self.level)
            
        if self.level not in environ['repoze.who.identity']['user_level']:
            #self.unmet(post_id=post_id, author=post.author_userid)
            self.unmet(level=self.level) # self.level
        



def makeVisitingGroupObjectOfVGDictionary(a_visiting_group):
    obj_params = makeParamsForObjectOfVGDictionary(a_visiting_group)
    
    # TODO: DataContainerFromDictLikeObject(fields=)
    visiting_group = DataContainer(name=a_visiting_group['name'],  _id=a_visiting_group['_id'],  info=a_visiting_group['info'],  visiting_group_properties=obj_params, 
                                   contact_person=a_visiting_group.get('contact_person', ''),  contact_person_email=a_visiting_group.get('contact_person_email', ''),  contact_person_phone=a_visiting_group.get('contact_person_phone', ''), 
                                   boknr=a_visiting_group['boknr'], password=a_visiting_group.get('password',''), boknstatus=a_visiting_group['boknstatus'],  camping_location=a_visiting_group['camping_location'],  
                                   from_date=datetime.datetime.strptime(a_visiting_group['from_date'],'%Y-%m-%d'), to_date=datetime.datetime.strptime(a_visiting_group['to_date'], '%Y-%m-%d'), 
                                   subtype=a_visiting_group['subtype'])
            
    return visiting_group
    
    
def makeVODBGroupObjectOfVGDictionary(a_visiting_group):
    obj_params = makeParamsForObjectOfVGDictionary(a_visiting_group)
    
    visiting_group = DataContainer(name=a_visiting_group['name'],  _id=a_visiting_group['_id'],  info=a_visiting_group['info'],  visiting_group_properties=obj_params, 
                                   vodb_contact_person=a_visiting_group.get('vodb_contact_person', ''),  vodb_contact_email=a_visiting_group.get('vodb_contact_email', ''),  
                                   vodb_contact_phone=a_visiting_group.get('vodb_contact_phone', ''), vodb_contact_address=a_visiting_group.get('vodb_contact_address', ''), 
                                   boknr=a_visiting_group['boknr'], password=a_visiting_group.get('password',''), boknstatus=a_visiting_group['boknstatus'],  camping_location=a_visiting_group['camping_location'],  
                                   from_date=datetime.datetime.strptime(a_visiting_group['from_date'],'%Y-%m-%d'), to_date=datetime.datetime.strptime(a_visiting_group['to_date'], '%Y-%m-%d'), 
                                   subtype=a_visiting_group['subtype'])
            
    return visiting_group
    
    
def makeParamsForObjectOfVGDictionary(visiting_group_c):
    """
    This function is for making an object that tw forms understands from a couchdb dict like object    
    """
    vgps = []
    for id, vgp in visiting_group_c['visiting_group_properties'].items():
        try:
            tmp_to_date = datetime.datetime.strptime(vgp['to_date'],'%Y-%m-%d')
        except ValueError:
            tmp_to_date = None
                
        try:
            tmp_from_date = datetime.datetime.strptime(vgp['from_date'],'%Y-%m-%d')
        except ValueError:
            tmp_from_date = None
                
                
        vgpx = DataContainer(property=vgp['property'],  value=vgp['value'],  unit=vgp['unit'], description=vgp['description'],  from_date=tmp_from_date,  to_date=tmp_to_date,  id=str(id))
        vgps.append(vgpx)
    return vgps
    
