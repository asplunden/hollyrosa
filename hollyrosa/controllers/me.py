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

from hollyrosa.controllers.common import has_level
from hollyrosa.lib.base import BaseController
from tg import expose, require, abort
from tg.predicates import Any

__all__ = ['me']


class Me(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    @expose('hollyrosa.templates.me')
    @require(
        Any(has_level('staff'), has_level('pl'), has_level('view'), msg='Only logged in users may view me properties'))
    def settings(self):
        return dict()
