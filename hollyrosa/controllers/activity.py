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
from hollyrosa.controllers.common import has_level, cleanHtml, languages_map, default_language, ensurePostRequest
from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch
from hollyrosa.model.booking_couch import genUID, getNotesForTarget
from hollyrosa.widgets.forms.edit_activity_form import create_edit_activity_form
from tg import expose, require, request, redirect, validate, abort, tmpl_context
from tg.predicates import Any, is_user

log = logging.getLogger(__name__)

__all__ = ['activity']


class Activity(BaseController):
    """
    Activity is used to view and edit activities.

    The added language versions feature where an activity can optionally be translated to more than one language is
    a little involved. To be backwards compatible, the optional translations are in a separate language_versions dict
    in an activity. Further, the default language is store in the already existing title and description attributes.

    Some activities have a special note attached which is used in the program listings page. For this to work with
    the new language versions, there have to be two more additions:

    1) notes must have an optional language attribute so all notes whos target_id is the activity is filtered using
    the activitys language taking default language into account.

    2) for the program listing to work, in an activity there have to be a dict language_booking_info_ids that for each
    language including the default one contaios the id of the relevant note. The old attribute booking_info_id and the
    new language_booking_info_ids MUST NOT EXIST AT THE SAME TIME
    """

    def view(self, url):
        """
        Accessing the path / must result in abort the request with a 404 HTTP status code.
        """
        abort(404)

    @expose('hollyrosa.templates.activity.view')
    @validate(validators={'activity_id': validators.UnicodeString(not_empty=True),
                          'language': validators.UnicodeString(not_empty=False)})
    def view(self,
             activity_id=None,
             language=None):
        """
        Viewing of a specific activity.

        :param activity_id: the id of the activity
        :param language: the language version or None or '' for the default language version
        """
        is_language_specified = language is not None and language != ''
        l_language = language if is_language_specified else default_language

        activity = common_couch.getActivity(getHollyCouch(), activity_id)
        activity_group = common_couch.getActivityGroup(getHollyCouch(), activity['activity_group_id'])

        # ...replace missing fields with empty string
        for attr_name in ['print_on_demand_link', 'external_link', 'internal_link', 'guides_per_slot', 'guides_per_day',
                          'equipment_needed', 'education_needed']:
            if attr_name not in activity:
                activity[attr_name] = u''

        if 'language_versions' not in activity:
            activity['language_versions'] = {}

        if is_language_specified and (language in activity['language_versions']):
            title = activity['language_versions'][language].get('title', '')
            description = activity['language_versions'][language].get('description', '')
        else:
            title = activity['title']
            description = activity['description']

        if default_language not in activity['language_versions']:
            activity['language_versions'][default_language] = {}

        activity_booking_info_id = activity.get('booking_info_id', '')
        if activity_booking_info_id != '' or 'language_booking_info_ids' in activity:
            notes = [n.doc for n in getNotesForTarget(getHollyCouch(), activity_id)]

            # only show note with corresponding language
            if is_language_specified:
                notes = [note for note in notes if ('language' in note and note['language'] == language) or (
                        language == default_language and 'language' not in note)]
            else:
                notes = [note for note in notes if 'language' not in note or note['language'] == default_language]
        else:
            notes = list()

        return dict(activity=activity,
                    title=title,
                    description=description,
                    activity_group=activity_group,
                    notes=notes,
                    languages_map=languages_map,
                    default_language=default_language,
                    language=l_language)

    @expose('hollyrosa.templates.activity.edit')
    @validate(
        validators={'activity_id': validators.UnicodeString(not_empty=True),
                    'language': validators.UnicodeString(not_empty=False)})
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may change activity information'))
    def edit(self, activity_id=None, language=None, **kw):
        """
        When editing the non-default language, we want to edit other title and description than the underlying data
        We must take care of this when saving.

        Only staff or pl may edit activities.
        """

        # use this form widget
        tmpl_context.form = create_edit_activity_form

        is_language_specified = language is not None and language != ''

        if activity_id is None:
            if is_language_specified and language != default_language:
                language_versions = {language: dict(description='', title='')}

            activity = dict(id=None, title=u'', description=u'', activity_group_id='',
                            language_versions=language_versions)
        else:
            try:
                activity = common_couch.getActivity(getHollyCouch(), activity_id)
                activity['id'] = activity_id

                # if we found the activity and language is given and language is not default language,
                # change the title and description fields so we edit the choosen language
                if is_language_specified and language != default_language:
                    activity['title'] = \
                        activity.get('language_versions', {}).get(language, {}).get('title', activity['title'])
                    activity['description'] = \
                        activity.get('language_versions', {}).get(language, {}).get('description',
                                                                                    activity['description'])

            except:
                # If we are creating a new activity, we always create one with nu language_versions
                # and edit the default_language
                activity = dict(id=activity_id, title=u'', description=u'', default_booking_state=0,
                                activity_group_id='', language_versions={}, language=default_language)

        # sanitizing colors like #fff to #ffffff
        if 'bg_color' in activity:
            if activity['bg_color'][0] == '#' and len(activity['bg_color']) == 4:
                a = activity['bg_color'][1]
                b = activity['bg_color'][2]
                c = activity['bg_color'][3]
                activity['bg_color'] = u"%c%c%c%c%c%c%c" % ('#', a, a, b, b, c, c)
        else:
            activity['bg_color'] = u'#ffffff'

        # set language property in the data returned from the view. This does not mean we save it
        activity['language'] = language if is_language_specified else default_language

        return dict(activity=activity)

    @validate(form=create_edit_activity_form, error_handler=edit)
    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'),
                 msg='Only staff members may change activity properties'))
    def save(self, id=None,
             title=None,
             description='',
             external_link='',
             internal_link='',
             print_on_demand_link='',
             tags='',
             capacity=0,
             default_booking_state=0,
             activity_group_id=1,
             gps_lat=0, gps_long=0,
             equipment_needed=False,
             education_needed=False,
             certificate_needed=False,
             bg_color='',
             guides_per_slot=0,
             guides_per_day=0,
             language=None):
        """
        Save the activity. Must be a post-request.

        :param id:
        :param title:
        :param external_link:
        :param internal_link:
        :param print_on_demand_link:
        :param description:
        :param tags:
        :param capacity:
        :param default_booking_state:
        :param activity_group_id:
        :param gps_lat:
        :param gps_long:
        :param equipment_needed:
        :param education_needed:
        :param certificate_needed:
        :param bg_color:
        :param guides_per_slot:
        :param guides_per_day:
        :param language:
        :return:
        """
        ensurePostRequest(request, name=__name__)

        is_new = id is None or id == ''

        if is_new:

            # TODO: need to set subtype on activity or is it handled by group belonging?
            activity = dict(type='activity')
            id = genUID(type='activity')

        else:
            # load the activity, later update properties and save
            activity = common_couch.getActivity(getHollyCouch(), id)

        # if language is None or language is default language, save to title and description, otherwise save
        # to the language_versions

        is_language_specified = language is not None and language != ''

        if not is_language_specified or language == default_language:
            activity['title'] = title
            activity['description'] = cleanHtml('' if description is None else description)
        else:
            language_versions = activity.get('language_versions', {})
            language_edited = language_versions.get(language, {})
            language_edited['title'] = title
            language_edited['description'] = cleanHtml('' if description is None else description)
            language_versions[language] = language_edited
            activity['language_versions'] = language_versions

        activity['external_link'] = external_link
        activity['internal_link'] = internal_link
        activity['print_on_demand_link'] = print_on_demand_link
        activity['tags'] = tags
        activity['capacity'] = capacity
        # activity.default_booking_state=default_booking_state
        activity['activity_group_id'] = activity_group_id
        # activity.gps_lat = gps_lat
        # activity.gps_long = gps_long
        activity['equipment_needed'] = equipment_needed
        activity['education_needed'] = education_needed
        activity['certificate_needed'] = certificate_needed
        activity['bg_color'] = bg_color
        activity['guides_per_slot'] = guides_per_slot
        activity['guides_per_day'] = guides_per_day

        # save the activity
        getHollyCouch()[id] = activity
        raise redirect('view', params={'activity_id': id, 'language': language}, scheme='https')
