# -*- coding: utf-8 -*-

"""
Copyright 2010-2018 Martin Eliasson

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


import logging, datetime, time, random, string
log = logging.getLogger(__name__)

from tg import expose, flash, require, url, request, redirect, validate, abort, tmpl_context, lurl
from tg.predicates import Any, is_user, has_permission
from formencode import validators

import webob

from marrow.mailer import Message

from hollyrosa.model import getHollyCouch, getMailer
from hollyrosa.model.booking_couch import genUID
from hollyrosa.model.booking_couch import getAllEmailAddresses, getEmailAddressStateByEmail, getEmailAddressByEmail

from hollyrosa.lib.base import BaseController

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, getLoggedInUserId, cleanHtml, ensurePostRequest

from hollyrosa.model.booking_couch import genUID
from hollyrosa.model.booking_couch import getAllEmailAddresses, getEmailAddressStateByEmail
from hollyrosa.controllers import common_couch
from hollyrosa.controllers.common_couch import createEmailAddress, createEmailAddressState, getEmailAddress, createEmailAddressWrongEmailReport
from hollyrosa.controllers.email_address_state_enums import EmailAddressStateEnum


__all__ = ['email_address']


class EmailAddress(BaseController):
    def view(self, url):
        """Abort the request with a 404 HTTP status code."""
        abort(404)


    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    #@validate(validators={'email_address_id':validators.UnicodeString(not_empty=True), 'global_state':validators.Int(not_empty=True) 'comment':validators.UnicodeString(not_empty=False)})
    @expose('hollyrosa.templates.email_address.email_address_management')
    def manage(self):
        log.debug('manage email addresses')
        return dict()



    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    #@validate(validators={'email_address_id':validators.UnicodeString(not_empty=True), 'global_state':validators.Int(not_empty=True) 'comment':validators.UnicodeString(not_empty=False)})
    @expose('json')
    def get_email_addresses(self):
        log.debug('get_email_addresses')
        email_addresses = [d.doc for d in getAllEmailAddresses(getHollyCouch())]
        return dict(email_addresses=email_addresses)


    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    @validate({'email_address':validators.Email(not_empty=True) })
    @expose('json')
    def add_email_address(self, email_address):
        # TODO when we create an email address, check if addreess already exists, if it does, do not create it.
        #      However, if no states exists for the email, than create an initial state
        log.debug('add_email_address')
        ensurePostRequest(request, 'add_email_address')

        existing_addresses = getEmailAddressByEmail(getHollyCouch(), email_address)

        if len(existing_addresses) > 0:
            log.warning('email adress {} already exists'.format(email_address))

            #...todo maybe create a very first state
            # TODO find a better exception
            raise webob.exc.HTTPUnprocessableEntity(comment='The email adress {} you tried to add already exists'.format(email_address))

        new_email_address = createEmailAddress(email_address=email_address)
        new_email_address_id = genUID(type='email_address')
        getHollyCouch()[new_email_address_id] = new_email_address

        timestamp = time.time()

        new_email_address_state = createEmailAddressState(new_email_address_id, time.time(), secret_token='', state=10, user_id=getLoggedInUserId(request))
        new_email_address_state_id = genUID(type='email_address_state')
        getHollyCouch()[new_email_address_state_id] = new_email_address_state
        return dict(new_email_address=new_email_address)


    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    @validate({'email_address_id':validators.UnicodeString(not_empty=True) })
    @expose('json')
    def get_email_address_state_WHICH_ONE(self, email_address_id):
        r = list(getEmailAddressStateByEmail(getHollyCouch(), email_address_id, limit=1))

        new_email_address = createEmailAddress(email_address=email_address)
        new_email_address_id = genUID(type='email_address')
        holly_couch[new_email_address_id] = new_email_address

        new_email_address_state = createEmailAddressState(new_email_address_id, time.time(), secret_token='', state=10, user_id=getLoggedInUserId(request))
        new_email_address_state_id = genUID(type='email_address_state')
        holly_couch[new_email_address_state_id] = new_email_address_state
        return dict(new_email_address=new_email_address)

    @expose('json')
    def get_email_address_state(self, email_address_id):
        r = list(getEmailAddressStateByEmail(holly_couch, email_address_id, limit=1))

        #...we should have only one email address state now.
        if len(r) > 0:
            x = r[0]
            email_address_state = dict(state=x.key[2], timestamp=x.key[1], email_address=x.doc, email_address_id=x.key[0] )
            #email_address_states = [dict(e=d.doc, k=d.key, adrid=d.value) for d in r]
            found = True
        else:
            email_address_state = dict(state=0, timestamp=0, email_address='', email_address_id=email_address_id )
            found = False
        return dict(email_address_state=email_address_state, email_address_id=email_address_id, found=found)


    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    @validate({'email_address':validators.Email(not_empty=True) })
    @expose('json')
    def request_email_address_confirmation(self, email_address):
        log.debug('request_email_address_confirmation')

        ensurePostRequest(request, 'request_email_address_confirmation')

        holly_couch = getHollyCouch()

        existing_addresses = getEmailAddressByEmail(holly_couch, email_address)

        #...add email request state with secret
        user_id = getLoggedInUserId(request) # TODO is it really called user_id in code ?
        timestamp = time.time()


        # TODO: what do we do if there is more than one email address matching ????
        for tmp_item in existing_addresses:
            tmp_email_address = tmp_item.key
            tmp_confirmation_token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(76))
            log.debug('creating request for {}'.format(tmp_email_address))
            new_email_address_state = createEmailAddressState(tmp_item.value, timestamp, secret_token=tmp_confirmation_token, state=20, user_id=user_id)
            new_email_address_state_id = genUID(type='email_address_state')
            holly_couch[new_email_address_state_id] = new_email_address_state


            #...send all those emails
            #...in the long run we dont want to do this synchronously
            mailer = getMailer()
            log.debug('Mailer: {}'.format(mailer))
            message = Message(author='"Hollyrosa" <hollyrosa@program.vassaro.net>', to=email_address) # TODO: set Message-ID and track it ?
            message.subject = "[ Hollyrosa ] Confirmation of Email Adress Required"
            message.plain = """This is an automatically generated message from Hollyrosa program booking system.

            You have recieved this message because someone tried to create an email address in the Hollyrosa booking system.

            To be able to use the email address within Hollyrosa, you must now confirm that this is indeed your email by clicking the following CONFIRM link: {0}

            In case you did not request to use this email address in Hollyrosa, you may either ignore this message or kindly inform us by clicking the following REJECT link: {1}

            Thanks
            The Hollyrosa Crew

            """.format(lurl('/email_address/confirm_email_address', params={'email_address':tmp_email_address, 'confirmation_token': tmp_confirmation_token}), lurl('/email_address/reject_email_address', params={'email_address':email_address, 'confirmation_token': tmp_confirmation_token}))

            message.rich = """<html>
            <head>
            </head>
            <body>
            <h1>Hollyrosa Program Booking System</h1>
            <h2>Email Address Confiormation</h2>
            <p>This is an automatically generated message from Hollyrosa program booking system.</p>

            <p>You have recieved this message because someone tried to create an email address in the Hollyrosa booking system.</p>

            <p>To be able to use the email address within Hollyrosa, you must now confirm that this is indeed your email by clicking the following <strong><a href="{0}">CONFIRM link</a></strong>.</p>

            <p>In case you did not request to use this email address in Hollyrosa, you may either ignore this message or kindly inform us by clicking the following <strong><a href="{1}">REJECT link</a></strong>.</p>

            <p><i>Thanks</i><br/>
            <i>The Hollyrosa Crew</i>
            </p>
            </body>
            </html>""".format(lurl('/email_address/confirm_email_address', params={'email_address':tmp_email_address, 'confirmation_token': tmp_confirmation_token}), lurl('/email_address/reject_email_address', params={'email_address':email_address, 'confirmation_token': tmp_confirmation_token}))
            mailer.start()
            mailer.send(message)
            mailer.stop()

        return dict(ok=True)


    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    @validate({'email_address_id':validators.UnicodeString(not_empty=True), 'global_state':validators.Int(not_empty=True), 'comment':validators.UnicodeString(not_empty=False)})
    @expose('json')
    def set_email_address_state(self, email_address_id, state=None, comment=''):
        log.debug('set_email_address_state to {}'.format(state))

        ensurePostRequest(request, 'set_email_address_state')

        holly_couch = getHollyCouch()
        tmp_item = getEmailAddress(holly_couch, email_address_id)
        #...add email request state with secret
        user_id = getLoggedInUserId(request) # TODO is it really called user_id in code ?
        timestamp = time.time()

        new_email_address_state = createEmailAddressState(tmp_item['_id'], timestamp, secret_token='', state=state, user_id=user_id, comment=comment)
        new_email_address_state_id = genUID(type='email_address_state')
        holly_couch[new_email_address_state_id] = new_email_address_state
        return dict(ok=True)


    @require(Any(has_level('pl'), has_level('goose'), msg='Only pl may administer emails'))
    @validate({'email_address_id':validators.UnicodeString(not_empty=True), 'global_state':validators.Int(not_empty=True), 'comment':validators.UnicodeString(not_empty=False)})
    @expose('json')
    def set_email_address_global_state(self, email_address_id, global_state=None, comment=''):
        log.debug('set_email_address_global_state to {}'.format(state))

        ensurePostRequest(request, 'set_email_address_global_state')

        holly_couch = getHollyCouch()

        #...TODO same as activaete, refactor
        tmp_item = getEmailAddress(holly_couch, email_address_id)
        tmp_item['global_state'] = global_state

        holly_couch[email_address_id] = tmp_item

        user_id = getLoggedInUserId(request) # TODO is it really called user_id in code ?

        return dict(ok=True)

    #---these three calls below should return HTML rather than JSON because they are to be clicked from email

    @expose('hollyrosa.templates.email_address.email_address_report_confirmation')
    @validate({'email_address':validators.Email(not_empty=True) })
    def report_wrong_email_address(self, email_address):
        log.debug('report_wrong_email_address')

        existing_addresses = getEmailAddressByEmail(getHollyCouch(), email_address)

        #...add email request state with secret
        user_id = getLoggedInUserId(request) # TODO is it really called user_id in code ?
        timestamp = time.time()
        for tmp_item in existing_addresses:

            # TODO: we shouldnt touch state, just report it in a different log. Might need human moderation. Errorneous reporting without confirmation token should not be trusted.

            log.debug('reporting wrong email for {}'.format(tmp_item.key))
            new_report=createEmailAddressWrongEmailReport(email_address=email_address, timestamp=time.time())
            new_report_id = genUID(type='email_address_report')
            getHollyCouch()[new_report_id] = new_report

        return dict()



    @expose('hollyrosa.templates.email_address.email_address_confirmation_answer')
    @validate({'email_address':validators.Email(not_empty=True), 'confirmation_token':validators.UnicodeString(not_empty=True)})
    def confirm_email_address(self, email_address, confirmation_token):
        log.debug('confirm_email_address')
        existing_addresses = getEmailAddressByEmail(getHollyCouch(), email_address)

        #...add email request state with secret
        user_id = getLoggedInUserId(request) # TODO is it really called user_id in code ?
        timestamp = time.time()

        for tmp_item in existing_addresses:

            # TODO: we must find the confirmation token for each, so we must find the very latest email address state
            latest_state_as_list = list(getEmailAddressStateByEmail(getHollyCouch(), tmp_item.value, limit=1))

            if len(latest_state_as_list) == 0:
                log.warning('trying to look up email address states for {} but found nothing'.format(email_address))
                raise webob.exc.HTTPUnprocessableEntity(comment='Token not accpeted for the email adress {} you tried to confirm'.format(email_address))


            stored_confirmation_token = latest_state_as_list[0].doc['secret_token']
            #print '*********', stored_confirmation_token, confirmation_token, latest_state_as_list[0].value
            if stored_confirmation_token != confirmation_token:
                log.warning('token mismatch when trying to confirm email address {}'.format(email_address))
                return dict(confirmed=False, rejected=False, trouble=True)
                #raise webob.exc.HTTPUnprocessableEntity(comment='Token not accpeted for the email adress {} you tried to confirm'.format(email_address))


            log.debug('confirming email for {}'.format(tmp_item.key))
            new_email_address_state = createEmailAddressState(tmp_item.value, timestamp, secret_token=confirmation_token, state=EmailAddressStateEnum.confirmed, user_id=user_id)
            new_email_address_state_id = genUID(type='email_address_state')
            getHollyCouch()[new_email_address_state_id] = new_email_address_state

        return dict(confirmed=True, rejected=False, trouble=False)


    @expose('hollyrosa.templates.email_address.email_address_confirmation_answer')
    @validate({'email_address':validators.Email(not_empty=True), 'confirmation_token':validators.UnicodeString(not_empty=True)})
    def reject_email_address(self, email_address, confirmation_token):
        log.debug('reject_email_address')
        existing_addresses = getEmailAddressByEmail(getHollyCouch(), email_address)

        #...add email request state with secret
        user_id = getLoggedInUserId(request) # TODO is it really called user_id in code ?
        timestamp = time.time()
        for tmp_item in existing_addresses:

            # TODO: we must find the confirmation token for each, so we must find the very latest email address state
            latest_state_as_list = list(getEmailAddressStateByEmail(getHollyCouch(), tmp_item.value, limit=1))

            if len(latest_state_as_list == 0):
                log.warning('trying to look up email address states for {} but found nothing'.format(email_address))
                raise webob.exc.HTTPUnprocessableEntity(comment='Token not accpeted for the email adress {} you tried to confirm'.format(email_address))

            stored_confirmation_token = latest_state_as_list[0]['secret_token']

            if stored_confirmation_token != confirmation_token:
                log.warning('token mismatch when trying to confirm email address {}'.format(email_address))
                #raise webob.exc.HTTPUnprocessableEntity(comment='Token not accpeted for the email adress {} you tried to confirm'.format(email_address))
                return dict(rejected=False, confirmed=False, trouble=True)


            log.debug('rejecting email for {}'.format(tmp_item.key))
            new_email_address_state = createEmailAddressState(tmp_item.value, timestamp, secret_token='', comment="rejected by the user who received the email", state=EmailAddressStateEnum.nonconfirmed, user_id=user_id)
            new_email_address_state_id = genUID(type='email_address_state')
            getHollyCouch()[new_email_address_state_id] = new_email_address_state
            return dict(rejected=True, confirmed=False, trouble=False)
