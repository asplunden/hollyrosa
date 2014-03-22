# -*- coding: utf-8 -*-
"""
Copyright 2010, 2011, 2012, 2013, 2014 Martin Eliasson

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

import pylons
from tg import expose, flash, require, url, request, redirect,  validate
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch

import datetime

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId

from hollyrosa.model.booking_couch import genUID 
from hollyrosa.controllers.booking_history import remember_tag_change
from hollyrosa.controllers import common_couch
from formencode import validators

__all__ = ['tag']


class Tag(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)    
        
    @expose("json")
    @validate(validators={'id':validators.UnicodeString})        
    def get_tags(self, id):
        vgroup = common_couch.getVisitingGroup(holly_couch,  id)
        tags = vgroup.get('tags',[])
        return dict(tags=tags)
    
        
    @expose("json")
    @validate(validators={'id':validators.UnicodeString, 'tags':validators.UnicodeString})        
    def add_tags(self, id, tags):
        vgroup = common_couch.getVisitingGroup(holly_couch,  id)
        old_tags = vgroup.get('tags',[])
        remember_old_tags = [t for t in old_tags]
        new_tags = [t.strip() for t in tags.split(',')]
        for t in new_tags:
            if t not in old_tags:
                old_tags.append(t)
        vgroup['tags'] = old_tags
        holly_couch[id] = vgroup
        remember_tag_change(holly_couch, old_tags=remember_old_tags, new_tags=old_tags, visiting_group_id=id, visiting_group_name=vgroup['name'], changed_by=getLoggedInUserId(request))
        
        return dict(tags=old_tags)
    
    
    @expose("json")
    @validate(validators={'id':validators.UnicodeString, 'tag':validators.UnicodeString})        
    def delete_tag(self, id, tag):
        vgroup = common_couch.getVisitingGroup(holly_couch,  id)
        old_tags = vgroup.get('tags',[])
        new_tags = [t for t in old_tags if t.strip() != tag.strip()]
        vgroup['tags'] = new_tags
        holly_couch[id] = vgroup
        remember_tag_change(holly_couch, old_tags=old_tags, new_tags=new_tags, visiting_group_id=id, visiting_group_name=vgroup['name'], changed_by=getLoggedInUserId(request))

        return dict(tags=new_tags)
