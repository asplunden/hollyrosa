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

class EditBookSlotForm(twf.Form):
    class child(twf.TableLayout):
        id = twf.HiddenField(validator=twc.Required)
        booking_day_id = twf.HiddenField(validator=twc.Required)
        slot_id = twf.HiddenField(validator=twc.Required)
        activity_id = twf.HiddenField(validator=twc.Required)
        return_to_day_id = twf.HiddenField(validator=twc.Required)
        visiting_group_name = twf.TextField(validator=twc.StringLengthValidator(min=1))
        visiting_group_display_name = twf.HiddenField(validator=twc.Required)
        visiting_group_id = twf.HiddenField(validator=twc.Required)
        # TODO: set height and width
        content = twf.TextArea(validator=twc.Required, css_class="edit_booking_content", rows=5, cols=35, id="booking_content")
        block_after_book = twf.CheckBox()
        
    action = lurl('save_booked_booking_properties')
        
create_edit_book_slot_form = EditBookSlotForm()
