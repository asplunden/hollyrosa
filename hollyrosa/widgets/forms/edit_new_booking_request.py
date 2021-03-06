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

class EditNewBookingRequestForm(twf.Form):
    class child(twf.TableLayout):
        id = twf.HiddenField()
        return_to_day_id = twf.HiddenField()
        visiting_group_name = twf.TextField(validator=twc.StringLengthValidator(min=1), css_class="input is-medium")
        visiting_group_display_name = twf.HiddenField()
        visiting_group_id = twf.HiddenField()
        booking_content = twf.TextArea(rows=5, cols=30, css_class="textarea")
        activity_id = twf.HiddenField()
        activity_name = twf.TextField(twc.Required, rows=30, cols=5, css_class="input is-small")
        requested_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")
        valid_from = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")
        valid_to = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")

    action = lurl('save_new_booking_request')


create_edit_new_booking_request_form = EditNewBookingRequestForm()
