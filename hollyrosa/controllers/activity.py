# -*- coding: utf-8 -*-

"""
Copyright 2010-2017 Martin Eliasson

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


from tg import expose, flash, require, url, request, redirect, validate, abort, tmpl_context
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch

import datetime

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, getLoggedInUserId
from hollyrosa.widgets.edit_activity_form import create_edit_activity_form

from hollyrosa.model.booking_couch import genUID 
from hollyrosa.controllers.booking_history import remember_tag_change
from hollyrosa.controllers import common_couch
from formencode import validators

__all__ = ['activity']


def ensurePostRequest(request, name=''):
    """
    The purpose of this little method is to ensure that the controller was called with appropriate HTTP verb. 
    """
    if not request.method == 'POST':
        abort(405)


class Activity(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)    
        
    
    @expose('hollyrosa.templates.view_activity')
    @validate(validators={'activity_id':validators.UnicodeString(not_empty=True)})
    def view_activity(self, activity_id=None):
        activity = common_couch.getActivity(holly_couch, activity_id)
        activity_group = common_couch.getActivityGroup(holly_couch, activity['activity_group_id'])
        
        #...replace missing fields with empty string
        for tmp_field in ['print_on_demand_link','external_link','internal_link','guides_per_slot','guides_per_day','equipment_needed','education_needed']:
            if not activity.has_key(tmp_field):
                activity[tmp_field] = u''
        return dict(activity=activity, activity_group=activity_group)
        
    
    @expose('hollyrosa.templates.edit_activity')
    @validate(validators={'activity_id':validators.UnicodeString(not_empty=True)})
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may change activity information'))
    def edit_activity(self, activity_id=None,  **kw):
        tmpl_context.form = create_edit_activity_form
            
        if None == activity_id:
            activity = dict(id=None,  title='',  info='', activity_group_id='')
        elif id=='':
            activity = dict(id=None,  title='', info='', activity_group_id='')
        else:
            try:
                activity = common_couch.getActivity(holly_couch,  activity_id) 
                activity['id'] = activity_id 
            except:
                activity = dict(id=activity_id, title='', info='', default_booking_state=0, activity_group_id='')
        
        #...what about sanitizing colors like #fff to #ffffff
        if activity['bg_color'][0] == '#' and len(activity['bg_color']) == 4:
            a = activity['bg_color'][1]
            b = activity['bg_color'][2]
            c = activity['bg_color'][3]
            activity['bg_color'] = "%c%c%c%c%c%c%c" % ('#', a, a, b, b, c, c)
        
        return dict(activity=activity)
        
        
    @validate(form=create_edit_activity_form, error_handler=edit_activity)      
    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may change activity properties'))
    def save_activity_properties(self, id=None, title=None, external_link='', internal_link='', print_on_demand_link='', description='', tags='', capacity=0, default_booking_state=0, activity_group_id=1,  gps_lat=0,  gps_long=0,  equipment_needed=False, education_needed=False,  certificate_needed=False,  bg_color='', guides_per_slot=0,  guides_per_day=0 ):
        ensurePostRequest(request, name=__name__)
        
        is_new = None == id or '' == id 
        if is_new:
            activity = dict(type='activity')
            id = genUID(type='activity')
            
        else:
            activity = common_couch.getActivity(holly_couch,  id)
                
        activity['title'] = title
        activity['description'] = description
        activity['external_link'] = external_link
        activity['internal_link'] = internal_link
        activity['print_on_demand_link'] = print_on_demand_link
        activity['tags'] = tags
        activity['capacity'] = capacity
#        #activity.default_booking_state=default_booking_state
        activity['activity_group_id'] = activity_group_id
#        activity.gps_lat = gps_lat
 #       activity.gps_long = gps_long
        activity['equipment_needed'] = equipment_needed
        activity['education_needed'] = education_needed
        activity['certificate_needed'] = certificate_needed
        activity['bg_color'] = bg_color
        activity['guides_per_slot'] = guides_per_slot
        activity['guides_per_day'] = guides_per_day
        
        holly_couch[id] = activity    
        raise redirect('/activity/view_activity',  activity_id=id)
     
    
        
