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
import datetime
import logging

from hollyrosa.controllers import booking_day, calendar, booking_history, workflow, visiting_group, tools, note, tag
from hollyrosa.controllers import user, me, visiting_group_program_request, vodb_group, program_layer, activity, \
    email_address
from hollyrosa.controllers.error import ErrorController
from hollyrosa.lib.base import BaseController
from hollyrosa.model import getHollyCouch
from tg import expose, flash, lurl, request, redirect
from tg.exceptions import HTTPFound
from tg.i18n import ugettext as _

__all__ = ['RootController']

log = logging.getLogger(__name__)


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

    error = ErrorController()

    activity = activity.Activity()

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

    email_address = email_address.EmailAddress()

    @expose('hollyrosa.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('hollyrosa.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

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

        # ...make a note here of last login
        # TODO: getter in holly couch
        user_o = getHollyCouch().get('user.' + userid)
        user_o['last_login'] = str(datetime.datetime.now())
        user_o['active'] = True

        getHollyCouch()['user.' + userid] = user_o

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
