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

from hollyrosa.widgets.components.tinymce_4_widget import TinyMCE4Widget
from hollyrosa.widgets.components.single_select_widget import SingleSelectWidget

from hollyrosa.controllers.common import languages_map


def _getPreferredLanguageOptions():
    """
    return a list of all supported languages for activity pages etc.

    if there ever is a need lookup from database, see how edit_activity_form does it
    """
    return languages_map.items()


class EditVisitingGroupForm(twd.CustomisedTableForm):
    class child(twf.TableLayout):
        visiting_group_id = twf.HiddenField(validator=twc.Required)
        subtype = twf.HiddenField(validator=twc.Required)
        name = twf.TextField(validator=twc.StringLengthValidator(min=1), css_class="edit_name input is-medium", size=40)
        info = TinyMCE4Widget()
        from_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small", required=True)
        to_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small", required=True)
        contact_person = twf.TextField(label_text="contact person:", css_class="input is-small")
        contact_person_email = twf.TextField(validator=twc.EmailValidator, css_class="input is-small")
        contact_person_phone = twf.TextField(css_class="input is-small")
        boknr = twf.TextField(css_class="input is-small")
        password = twf.TextField(css_class="input is-small")
        camping_location = twf.TextField(css_class="input is-small")
        language = SingleSelectWidget(validator=twc.Required, options=twc.Deferred(_getPreferredLanguageOptions))

        class visiting_group_properties(twd.GrowingGridLayout):
            extra_reps = 1
            property_id = twf.HiddenField()
            property = twf.TextField(size=10, css_class="input is-small")
            value = twf.TextField(size=4, css_class="input is-small")
            unit = twf.TextField(size=8, css_class="input is-small")
            description = twf.TextField(css_class="input is-small")
            from_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")  # required=True
            to_date = twf.CalendarDatePicker(date_format='%Y-%m-%d', css_class="input is-small")  # required=True

    action = lurl('save_visiting_group_properties')


create_edit_visiting_group_form = EditVisitingGroupForm()
