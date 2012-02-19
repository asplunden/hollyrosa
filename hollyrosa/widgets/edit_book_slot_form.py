"""
Copyright 2010, 2011 Martin Eliasson

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

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField,  Label,  CheckBox

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString


class EditBookSlotForm(TableForm):
    
    show_errors = True

    class fields(WidgetsList):
        id = HiddenField(validator=UnicodeString)
        booking_day_id = HiddenField(validator=UnicodeString)
        slot_id = HiddenField(validator=UnicodeString)
        activity_id = HiddenField(validator=UnicodeString)
        return_to_day_id = HiddenField(validator=UnicodeString)
        visiting_group_name = TextField(validator=UnicodeString(min=1),  css_class="edit_name",  size=40)
        visiting_group_id = SingleSelectField(validator=UnicodeString)
        content = TextArea(validator=UnicodeString)
        block_after_book = CheckBox()
        
create_edit_book_slot_form = EditBookSlotForm("create_edit_book_slot_form")
