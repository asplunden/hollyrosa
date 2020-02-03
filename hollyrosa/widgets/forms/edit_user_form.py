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

from tg import lurl
import tw2.core as twc
import tw2.forms as twf


class EditUserForm(twf.Form):
    class child(twf.TableLayout):
        user_id = twf.HiddenField(validator=twc.Required)
        user_name = twf.TextField(validator=twc.StringLengthValidator(min=4), css_class="input is-small")
        display_name = twf.TextField(validator=twc.StringLengthValidator(min=4), css_class="input is-small")

    action = lurl('save_user')


create_edit_user_form = EditUserForm()
