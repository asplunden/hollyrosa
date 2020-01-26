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


class EmailAddressStateEnum(object):
    notset = 0
    created = 10
    need_confirmation = 20
    confirmation_sent = 30
    confirmed = 40
    active = 50
    inactive = -10
    terminated = -100
    nonconfirmed = 25


    _lookup = {}
    _lookup[notset] = 'not set'
    _lookup[created] = 'creted'
    _lookup[need_confirmation] = 'need confirmation'
    _lookup[confirmation_sent] = 'confirmation sent'
    _lookup[confirmed] = 'confirmed'
    _lookup[active] = 'active'
    _lookup[inactive] = 'inactive'
    _lookup[terminated] = 'terminated'
    _lookup[nonconfirmed] = 'not confirmed'

    @classmethod
    def lookupName(cls, state):
        return cls._lookup[state]

    @classmethod
    def nextState(cls, curr, next):
        #...just accept allowed state changes
        if curr == cls.notset:
            if next == cls.created:
                return cls.created
            else:
                return cls.notset

        elif curr == cls.created:
            if next in [cls.confirmed, cls.need_confirmation]:
                return next
            else:
                return curr

        elif curr == cls.need_confirmation:
            if next in [cls.confirmation_sent]:
                return next
            else:
                return curr

        elif curr == cls.confirmation_sent:
            if next in [cls.nonconfirmed, cls.confirmed]:
                return next
            else:
                return curr

        elif curr == cls.nonconfirmed:
            if next in [cls.confirmation_sent, cls.terminated]:
                return next
            else:
                return curr

        elif curr == cls.confirmed:
            if next in [cls.active, cls.terminated]:
                return next
            else:
                return curr

        elif curr == cls.inactive:
            if next in [cls.active, cls.terminated]:
                return next
            else:
                return curr

        elif curr == cls.terminated:
            if next in [cls.created]:
                return next
            else:
                return curr
