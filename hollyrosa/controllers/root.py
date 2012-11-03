# -*- coding: utf-8 -*-
"""
Main Controller

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

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from hollyrosa.lib.base import BaseController
from hollyrosa.controllers.error import ErrorController
from hollyrosa.controllers import booking_day,  booking_history, workflow, visiting_group, tools, note, tag, user, me

from hollyrosa import model
from hollyrosa.controllers.secure import SecureController

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
    secc = SecureController()
    
    ##admin = Catwalk(model, DBSession)
    
    error = ErrorController()
    
    booking = booking_day.BookingDay()

    calendar = booking_day.Calendar()
    
    visiting_group = visiting_group.VisitingGroup()
    
    history = booking_history.History()
    
    workflow = workflow.Workflow()
    
    tools = tools.Tools()
    
    note = note.Note()

    tag = tag.Tag()
    
    user = user.User()
    
    me = me.Me()
    
    
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
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
