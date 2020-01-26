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

import logging, datetime
log = logging.getLogger(__name__)

from tg import expose, flash, require, url, request, redirect, validate, abort, tmpl_context
from tg.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch

import bleach


#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, getLoggedInUserId, cleanHtml, languages_map, default_language
from hollyrosa.widgets.edit_activity_form import create_edit_activity_form

from hollyrosa.model.booking_couch import genUID
from hollyrosa.controllers.booking_history import remember_tag_change
from hollyrosa.model.booking_couch import getNotesForTarget
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
    def view_activity(self, activity_id=None, language=None):

        _language = language if language != None else default_language

        activity = common_couch.getActivity(getHollyCouch(), activity_id)
        activity_group = common_couch.getActivityGroup(getHollyCouch(), activity['activity_group_id'])

        #...replace missing fields with empty string
        for tmp_field in ['print_on_demand_link','external_link','internal_link','guides_per_slot','guides_per_day','equipment_needed','education_needed']:
            if not activity.has_key(tmp_field):
                activity[tmp_field] = u''

        if not 'language_versions' in activity:
            activity['language_versions'] = {}

        if (language != None) and (language in activity['language_versions']):
            title = activity['language_versions'][language].get('title', '')
            description = activity['language_versions'][language].get('description', '')
        else:
            title = activity['title']
            description = activity['description']

        if default_language not in activity['language_versions']:
            activity['language_versions'][default_language] = {}

        activity_booking_info_id = activity.get('booking_info_id','')
        if activity_booking_info_id != '':
            notes = [n.doc for n in getNotesForTarget(getHollyCouch(), activity_id)]

            # only show note with corresponding language
            if language != None:
                notes = [note for note in notes if 'language' in note and note['language'] == language]
            else:
                notes = [note for note in notes if 'language' not in note or note['language'] == default_language]
        else:
            notes = list()

        return dict(activity=activity, title=title, description=description, activity_group=activity_group, notes=notes, languages_map=languages_map, default_language=default_language, language=_language)


    @expose('hollyrosa.templates.edit_activity')
    @validate(validators={'activity_id':validators.UnicodeString(not_empty=True), 'language':validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may change activity information'))
    def edit_activity(self, activity_id=None, language=None, **kw):
        """
        When editing the non-default language, we want to edit other title and description than the underlying data
        We must take care of this when saving
        """
        tmpl_context.form = create_edit_activity_form

        if None == activity_id:
            if language != None and language != default_language:
                language_versions = {}
                language_versions[language] = dict(description="", title="")

            activity = dict(id=None,  title=u'', description=u'', activity_group_id='', language_versions=language_versions)
        #elif id=='':
        #    activity = dict(id=None,  title=u'', description=u'', activity_group_id='', language_versions=language_versions)
        else:
            try:
                activity = common_couch.getActivity(getHollyCouch(), activity_id)
                activity['id'] = activity_id

                # if we found the activity and language is given and language is not default language,
                # change the title and description fields so we edit the choosen language
                if language != None and language != default_language:
                    activity['title'] = activity.get('language_versions', {}).get(language, {}).get('title', activity['title'])
                    activity['description'] = activity.get('language_versions', {}).get(language, {}).get('description', activity['description'])

            except:
                # If we are creating a new activity, we always create one with nu language_versions and edit the default_language
                activity = dict(id=activity_id, title=u'', description=u'', default_booking_state=0, activity_group_id='', language_versions={}, language=default_language)

        #...what about sanitizing colors like #fff to #ffffff
        if activity['bg_color'][0] == '#' and len(activity['bg_color']) == 4:
            a = activity['bg_color'][1]
            b = activity['bg_color'][2]
            c = activity['bg_color'][3]
            activity['bg_color'] = u"%c%c%c%c%c%c%c" % ('#', a, a, b, b, c, c)

        activity['language'] = language

        return dict(activity=activity)


    @validate(form=create_edit_activity_form, error_handler=edit_activity)
    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), msg='Only staff members may change activity properties'))
    def save_activity_properties(self, id=None, title=None, external_link='', internal_link='', print_on_demand_link='', description='', tags='', capacity=0, default_booking_state=0, activity_group_id=1,  gps_lat=0,  gps_long=0,  equipment_needed=False, education_needed=False,  certificate_needed=False,  bg_color='', guides_per_slot=0,  guides_per_day=0, language=None ):
        ensurePostRequest(request, name=__name__)

        is_new = None == id or '' == id
        if is_new:
            activity = dict(type='activity') # TODO: need to set subtype on activity or is it handled by group belonging?
            id = genUID(type='activity')

        else:
            activity = common_couch.getActivity(getHollyCouch(),  id)

        # if language is None or language is default language, save to title and description, otherwise save to the language_versions
        if language == None or language == default_language:
            activity['title'] = title
            activity['description'] = cleanHtml(description)
        else:
            language_versions = activity.get('language_versions', {})
            language_edited = language_versions.get(language, {})
            language_edited['title'] = title
            language_edited['description'] = cleanHtml(description)
            language_versions[language] = language_edited
            activity['language_versions'] = language_versions

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

        getHollyCouch()[id] = activity
        raise redirect('/activity/view_activity',  activity_id=id, language=language)
