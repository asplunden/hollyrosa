# -*- coding: utf-8 -*-
"""
Main Controller

Copyright 2010 - 2016 Martin Eliasson

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
import datetime

from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound

from tg import predicates

from hollyrosa.lib.base import BaseController
from hollyrosa.controllers.error import ErrorController
from hollyrosa.controllers import booking_day, calendar, booking_history, workflow, visiting_group, tools, note, tag, user, me, visiting_group_program_request, vodb_group,  program_layer

from hollyrosa import model

__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the hollyrosa application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    ##secc = SecureController()
    
    error = ErrorController()
    
    booking = booking_day.BookingDay()

    calendar = calendar.Calendar()
    
    visiting_group = visiting_group.VisitingGroup()
    
    history = booking_history.History()
    
    workflow = workflow.Workflow()
    
    tools = tools.Tools()
    
    note = note.Note()

    tag = tag.Tag()
    
    user = user.User()
    
    me = me.Me()
    
    vodb_group = vodb_group.VODBGroup()
    
    visiting_group_program_request = visiting_group_program_request.VisitingGroupProgramRequest()
    
    program_layer = program_layer.ProgramLayer()
    
    
    @expose('hollyrosa.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('hollyrosa.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('hollyrosa.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')

    @expose('hollyrosa.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('hollyrosa.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('hollyrosa.templates.login')
    def login(self, came_from=lurl('/'), failure=None, logins=0, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter), came_from=came_from, login=login)


    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login', params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        
        #...make a note here of last login
        # TODO: getter in holly couch
        user_o = model.holly_couch.get('user.'+userid)
        user_o['last_login'] = str(datetime.datetime.now())
        user_o['active'] = True
        model.holly_couch['user.'+userid] = user_o        

        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)
