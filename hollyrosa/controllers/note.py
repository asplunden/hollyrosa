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

import pylons
from tg import expose, flash, require, url, request, redirect,  validate
from repoze.what.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch,  genUID

import datetime,  StringIO,  time

#...this can later be moved to the VisitingGroup module whenever it is broken out
from tg import tmpl_context

from hollyrosa.widgets.edit_note_form import create_edit_note_form
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId

from hollyrosa.model.booking_couch import genUID, getNotesForTarget
from hollyrosa.controllers.booking_history import remember_note_change

__all__ = ['note']


class Note(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)
   
    @expose('hollyrosa.templates.edit_note')    
    def add_note(self, target_id):
        tmpl_context.form = create_edit_note_form
        note_o = DataContainer(text='', target_id=target_id, _id='')
        return dict(note=note_o)
        
   
    @expose('hollyrosa.templates.edit_note')    
    def edit_note(self, _id):
        tmpl_context.form = create_edit_note_form
        if _id == '':
            note_o = DataContainer(text='', target_id=target_id, _id='')
        else:
            note_o = holly_couch[_id] #DataContainer(text='', target_id=target_id, _id='')
        return dict(note=note_o)
        
    @expose("json")
    def get_notes_for_visiting_group(self, id):
        print 'load'
        notes = [n.doc for n in getNotesForTarget(id)]
        return dict(notes=notes, id=id)


    @expose()
    def save_note(self, target_id, _id, text):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if _id == '':
            note_o = dict(type='note', _id=genUID(type='note'), target_id=target_id, note_state=0, tags=list(), history=list(), text='')
            note_change='new'
        else:
            note_o = holly_couch[_id]
            history = note_o['history']
            if history == None:
                history = list()
            else:
                history.append([timestamp, note_o['text']])
            note_o['history'] = history
            note_change = 'changed'
            
        note_o['timestamp'] = timestamp
        note_o['last_changed_by'] = getLoggedInUserId(request)
        note_o['text'] = text
        holly_couch[note_o['_id']] = note_o
        
        remember_note_change(target_id=target_id, note_id=note_o['_id'], changed_by=getLoggedInUserId(request), note_change=note_change)

        # TODO: where do we go from here?
        redirect_to = '/'
        if 'visiting_group' in note_o['target_id']:
            redirect_to = '/visiting_group/show_visiting_group?id='+note_o['target_id']
        raise redirect(redirect_to)