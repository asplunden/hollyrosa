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

import tw2.core as twc
import tw2.forms as twf
import tw2.dynforms as twd

from tg import lurl

from tinymce_4_widget import TinyMCE4Widget


class EditVodbGroupForm(twd.CustomisedTableForm):
    class child(twf.TableLayout):
        vodb_group_id = twf.HiddenField()
        subtype = twf.HiddenField()
        name = twf.TextField(validator=twc.StringLengthValidator(min=4), css_class="edit_name input is-medium", size=40)
        boknr = twf.TextField(css_class="input is-small")
        info = TinyMCE4Widget()
        from_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', required=True, css_class="input is-small")
        to_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', required=True, css_class="input is-small")
        vodb_contact_name = twf.TextField(css_class="input is-small")
        vodb_contact_email = twf.TextField(validator=twc.EmailValidator, css_class="input is-small")
        vodb_contact_phone = twf.TextField(css_class="input is-small")
        vodb_contact_address = twf.TextArea(css_class="input is-small")
        camping_location = twf.TextField(css_class="input is-small")

        class visiting_group_properties(twd.GrowingGridLayout):
            extra_reps = 1
            propery_id = twf.HiddenField('property_id')
            property = twf.TextField('property', size=10, css_class="input is-small")
            value = twf.TextField('value', size=4, css_class="input is-small")
            unit = twf.TextField('unit', size=8, css_class="input is-small")
            description = twf.TextField('description', css_class="input is-small")
            from_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")
            to_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")

    action = lurl('save_vodb_group_properties')


create_edit_vodb_group_form = EditVodbGroupForm()
