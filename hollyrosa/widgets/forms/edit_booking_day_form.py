"""
Copyright 2010-2016 Martin Eliasson

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

from hollyrosa.widgets.components.tinymce_4_widget import TinyMCE4Widget


class EditVisitingGroupForm(twf.Form):
    class child(twf.TableLayout):
        recid = twf.HiddenField(validator=twc.Required)  #### TODO: former id was _id but no longer allowed name
        title = twf.TextField(validator=twc.Required, css_class="input is-medium")
        note = TinyMCE4Widget()
        num_program_crew_members = twf.TextField(validator=twc.IntValidator, css_class="input is-small")
        num_fladan_crew_members = twf.TextField(validator=twc.IntValidator, css_class="input is-small")

    action = lurl('save_booking_day_properties')


create_edit_booking_day_form = EditVisitingGroupForm()
