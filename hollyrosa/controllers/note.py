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


from tg import expose, flash, require, url, request, redirect,  validate, abort
from tg.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch, genUID
from hollyrosa.controllers import common_couch

from formencode import validators

import datetime,  StringIO, time, logging

log = logging.getLogger()

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context

from hollyrosa.widgets.edit_note_form import create_edit_note_form
from hollyrosa.widgets.edit_attachment_form import create_edit_attachment_form

from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId, ensurePostRequest, cleanHtml

from hollyrosa.model.booking_couch import genUID, getNotesForTarget
from hollyrosa.controllers.booking_history import remember_note_change

from tg import request, response
##from tg.controllers import CUSTOM_CONTENT_TYPE

__all__ = ['note']


class Note(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)

    @expose('hollyrosa.templates.edit_note')
    @require(Any(has_level('staff'), has_level('pl'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def add_note(self, target_id):
        tmpl_context.form = create_edit_note_form
        note_o = dict(text='', target_id=target_id, note_id='')
        return dict(note=note_o)


    @expose('hollyrosa.templates.edit_attachment')
    @require(Any(has_level('staff'), has_level('pl'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def add_attachment(self, target_id):
        tmpl_context.form = create_edit_attachment_form
        attachment_o = dict(text='', target_id=target_id, attachment_id='')
        return dict(attachment=attachment_o)


    @expose('hollyrosa.templates.edit_note')
    @require(Any(has_level('staff'), has_level('pl'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def edit_note(self, note_id=None, visiting_group_id=None):
        tmpl_context.form = create_edit_note_form
        if note_id == '':
            note_o = DataContainer(text='', target_id=visiting_group_id, note_id='')
        else:
            note_o = common_couch.getNote(getHollyCouch(),  note_id)
        return dict(note=note_o)


    @expose('hollyrosa.templates.edit_attachment')
    @require(Any(has_level('staff'), has_level('pl'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def edit_attachment(self, note_id=None, visiting_group_id=None):
        attachment_id=note_id
        tmpl_context.form = create_edit_attachment_form
        if attachment_id == '':
            attachment_o = dict(text='', target_id=visiting_group_id, note_id='')
        else:
            attachment_o = common_couch.getAttachment(getHollyCouch(),  attachment_id)
        return dict(attachment=attachment_o)

    @expose("json")
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def get_notes_for_visiting_group(self, id):
        notes = [n.doc for n in getNotesForTarget(getHollyCouch(), id)]
        return dict(notes=notes, id=id)


    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def save_note(self, target_id, note_id, text):
        log.info('save_note()')
        ensurePostRequest(request, __name__)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if note_id == '' or note_id == None:
            note_o = dict(type='note', note_id=genUID(type='note'), target_id=target_id, note_state=0, tags=list(), history=list(), text='')
            note_change='new'
            note_o['timestamp'] = timestamp
        else:
            note_o = common_couch.getNote(getHollyCouch(), note_id)
            history = note_o['history']
            if history == None:
                history = list()
            else:
                history.append([timestamp, note_o['text']])
            note_o['history'] = history
            note_change = 'changed'


        note_o['last_changed_by'] = getLoggedInUserId(request)
        note_o['text'] = cleanHtml(text)
        getHollyCouch()[note_o['note_id']] = note_o

        remember_note_change(getHollyCouch(), target_id=target_id, note_id=note_o['note_id'], changed_by=getLoggedInUserId(request), note_change=note_change)

        # TODO: where do we go from here?
        redirect_to = '/'
        if 'visiting_group' in note_o['target_id']:
            redirect_to = '/visiting_group/show_visiting_group?visiting_group_id='+note_o['target_id']
        raise redirect(redirect_to)


    @expose()
    @require(Any(is_user('root'), has_level('staff'), has_level('pl'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def save_attachment(self, target_id, text, attachment, _id='', **kwargs):
        log.info("save_attachment()")
        ensurePostRequest(request, __name__)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if _id == '':
            attachment_o = dict(type='attachment', _id=genUID(type='attachment'), target_id=target_id, attachment_state=0, tags=list(), history=list(), text='')
            attachment_change='new'
            attachment_o['timestamp'] = timestamp
        else:
            attachment_o = common_couch.getAttachment(getHollyCouch(),  _id)
            history = attachment_o['history']
            if history == None:
                history = list()
            else:
                history.append([timestamp, attachment_o['text']])
            attachment_o['history'] = history
            attachment_change = 'changed'

        attachment_o['last_changed_by'] = getLoggedInUserId(request)
        attachment_o['text'] = cleanHtml(text)
        getHollyCouch()[attachment_o['_id']] = attachment_o

        file = request.POST['attachment']

        if file != '':
            getHollyCouch().put_attachment(attachment_o, attachment.file, filename=attachment.filename)

        # TODO FIX BELOW
        #remember_attachment_change(getHollyCouch(), target_id=target_id, attachment_id=attachment_o['_id'], changed_by=getLoggedInUserId(request), attachment_change=attachment_change)

        # TODO: where do we go from here?
        redirect_to = '/'
        if 'visiting_group' in attachment_o['target_id']:
            redirect_to = '/visiting_group/show_visiting_group?visiting_group_id='+attachment_o['target_id']
        raise redirect(redirect_to)


    @expose()
    @validate(validators={"attachment_id":validators.UnicodeString(), "doc_id":validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only staff members may view visiting group attachments'))
    def download_attachment(self, attachment_id, doc_id):
        response.content_type='x-application/download'
        log.debug(u'Trying to download attachment="%s" filename="%s"' % (attachment_id, doc_id))
        headers = ('Content-Disposition', ('attachment;filename=%s' % doc_id).replace(u' ',u'_').replace(u'å',u'a').replace(u'ö',u'o').encode('ascii', 'replace'))
        response.headerlist.append(headers)
        return getHollyCouch().get_attachment(attachment_id, doc_id).read()

    @expose()
    @validate(validators={"note_id":validators.UnicodeString(), "visiting_group_id":validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members may delete notes and attachments'))
    def delete_note(self, note_id, visiting_group_id):
        log.debug(u'Trying to delete note with id="%s" visting_group_id="%s"' % (note_id, visiting_group_id))
        note_o = common_couch.getCouchDBDocument(getHollyCouch(), note_id, doc_type=None)
        if note_o['target_id'] != visiting_group_id:
            abort(403) # TODO: NOT ALLOWED TO DO THIS, FORBIDDEN.
        if note_o['type'] == 'attachment':
            note_o['attachment_state'] = -100
        elif note_o['type'] == 'note':
            note_o['note_state'] = -100
        getHollyCouch()[note_id] = note_o

        # TODO: add to history
        raise redirect(request.referrer)
