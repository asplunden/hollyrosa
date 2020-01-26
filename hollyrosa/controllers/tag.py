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

import logging

from formencode import validators
from hollyrosa.controllers import common_couch
from hollyrosa.controllers.booking_history import remember_tag_change
# ...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, getLoggedInUserId, ensurePostRequest
from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch
from tg import expose, require, request, validate, abort
from tg.predicates import Any

__all__ = ['tag']

log = logging.getLogger(__name__)


class Tag(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    @expose("json")
    @validate(validators={'id': validators.UnicodeString})
    def get_tags(self, id):
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), id)
        tags = vgroup.get('tags', [])
        return dict(tags=tags)

    @expose("json")
    @require(Any(has_level('staff'), has_level('pl'), msg='Only PL and staff members may change tags'))
    @validate(validators={'id': validators.UnicodeString, 'tags': validators.UnicodeString})
    def add_tags(self, id, tags):
        log.info("add_tags()")
        ensurePostRequest(request, __name__)
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), id)
        old_tags = vgroup.get('tags', [])
        remember_old_tags = [t for t in old_tags]
        new_tags = [t.strip() for t in tags.split(',')]
        for t in new_tags:
            if t not in old_tags:
                old_tags.append(t)
        vgroup['tags'] = old_tags
        getHollyCouch()[id] = vgroup
        remember_tag_change(getHollyCouch(), old_tags=remember_old_tags, new_tags=old_tags, visiting_group_id=id,
                            visiting_group_name=vgroup['name'], changed_by=getLoggedInUserId(request))

        return dict(tags=old_tags)

    @expose("json")
    @require(Any(has_level('staff'), has_level('pl'), msg='Only PL and staff members may change tags'))
    @validate(validators={'id': validators.UnicodeString, 'tag': validators.UnicodeString})
    def delete_tag(self, id, tag):
        log.info("delete_tag()")
        ensurePostRequest(request, __name__)
        vgroup = common_couch.getVisitingGroup(getHollyCouch(), id)
        old_tags = vgroup.get('tags', [])
        new_tags = [t for t in old_tags if t.strip() != tag.strip()]
        vgroup['tags'] = new_tags
        getHollyCouch()[id] = vgroup
        remember_tag_change(getHollyCouch(), old_tags=old_tags, new_tags=new_tags, visiting_group_id=id,
                            visiting_group_name=vgroup['name'], changed_by=getLoggedInUserId(request))

        return dict(tags=new_tags)
