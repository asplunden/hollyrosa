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

import pylons
from tg import expose, flash, require, url, request, redirect,  validate
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch,  genUID
from hollyrosa.controllers import common_couch

from formencode import validators

import datetime,  StringIO,  time

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context

from hollyrosa.widgets.edit_note_form import create_edit_note_form
from hollyrosa.widgets.edit_attachment_form import create_edit_attachment_form
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId

from hollyrosa.model.booking_couch import genUID, getNotesForTarget
from hollyrosa.controllers.booking_history import remember_note_change

from tg import request, response
from tg.controllers import CUSTOM_CONTENT_TYPE

__all__ = ['note']


class Note(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
   
    @expose('hollyrosa.templates.edit_note')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))  
    def add_note(self, target_id):
        tmpl_context.form = create_edit_note_form
        note_o = DataContainer(text='', target_id=target_id, _id='')
        return dict(note=note_o)
        
        
    @expose('hollyrosa.templates.edit_attachment')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))  
    def add_attachment(self, target_id):
        tmpl_context.form = create_edit_attachment_form
        attachment_o = DataContainer(text='', target_id=target_id, _id='')
        return dict(attachment=attachment_o)
        
   
    @expose('hollyrosa.templates.edit_note')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def edit_note(self, note_id=None, visiting_group_id=None):
        tmpl_context.form = create_edit_note_form
        if note_id == '':
            note_o = DataContainer(text='', target_id=target_id, _id='')
        else:
            note_o = common_couch.getNote(holly_couch,  note_id) 
        return dict(note=note_o)
        
        
    @expose('hollyrosa.templates.edit_attachment')
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def edit_attachment(self, note_id=None, visiting_group_id=None):
        attachment_id=note_id
        tmpl_context.form = create_edit_attachment_form
        if attachment_id == '':
            attachment_o = DataContainer(text='', target_id=target_id, _id='')
        else:
            attachment_o = common_couch.getAttachment(holly_couch,  attachment_id)
        return dict(attachment=attachment_o)
        
    @expose("json")
    #@require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def get_notes_for_visiting_group(self, id):
        notes = [n.doc for n in getNotesForTarget(holly_couch, id)]
        return dict(notes=notes, id=id)


    @expose()
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def save_note(self, target_id, _id, text):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if _id == '':
            note_o = dict(type='note', _id=genUID(type='note'), target_id=target_id, note_state=0, tags=list(), history=list(), text='')
            note_change='new'
            note_o['timestamp'] = timestamp
        else:
            note_o = common_couch.getNote(holly_couch,  _id)
            history = note_o['history']
            if history == None:
                history = list()
            else:
                history.append([timestamp, note_o['text']])
            note_o['history'] = history
            note_change = 'changed'
            
        
        note_o['last_changed_by'] = getLoggedInUserId(request)
        note_o['text'] = text
        holly_couch[note_o['_id']] = note_o
        
        remember_note_change(holly_couch, target_id=target_id, note_id=note_o['_id'], changed_by=getLoggedInUserId(request), note_change=note_change)

        # TODO: where do we go from here?
        redirect_to = '/'
        if 'visiting_group' in note_o['target_id']:
            redirect_to = '/visiting_group/show_visiting_group?visiting_group_id='+note_o['target_id']
        raise redirect(redirect_to)
        
        
    @expose()
    @require(Any(is_user('user.erspl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def save_attachment(self, target_id, _id, text, attachment):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if _id == '':
            attachment_o = dict(type='attachment', _id=genUID(type='attachment'), target_id=target_id, attachment_state=0, tags=list(), history=list(), text='')
            attachment_change='new'
            attachment_o['timestamp'] = timestamp
        else:
            attachment_o = common_couch.getAttachment(holly_couch,  _id)
            history = attachment_o['history']
            if history == None:
                history = list()
            else:
                history.append([timestamp, attachment_o['text']])
            attachment_o['history'] = history
            attachment_change = 'changed'
        
        attachment_o['last_changed_by'] = getLoggedInUserId(request)
        attachment_o['text'] = text
        holly_couch[attachment_o['_id']] = attachment_o
        
        file = request.POST['attachment']

        if file != '':
            holly_couch.put_attachment(attachment_o, attachment.file, filename=attachment.filename)
        
        # TODO FIX BELOW
        #remember_attachment_change(holly_couch, target_id=target_id, attachment_id=attachment_o['_id'], changed_by=getLoggedInUserId(request), attachment_change=attachment_change)

        # TODO: where do we go from here?
        redirect_to = '/'
        if 'visiting_group' in attachment_o['target_id']:
            redirect_to = '/visiting_group/show_visiting_group?visiting_group_id='+attachment_o['target_id']
        raise redirect(redirect_to)
        
        
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    @validate(validators={"attachment_id":validators.UnicodeString(), "doc_id":validators.UnicodeString()})
    @require(Any(is_user('root'), has_level('pl'), has_level('staff'), msg='Only staff members may view visiting group attachments'))   
    def download_attachment(self, attachment_id, doc_id):
        response.content_type='x-application/download'
        response.headerlist.append(('Content-Disposition','attachment;filename=%s' % doc_id))        
                
        return holly_couch.get_attachment(attachment_id, doc_id).read()


