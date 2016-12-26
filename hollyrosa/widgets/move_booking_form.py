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

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, HiddenField

#...for form validation
from tw.forms.validators import Int, NotEmpty, UnicodeString

class MoveBookingForm(TableForm):
    
    show_errors = True
    
    class fields(WidgetsList):
        id = HiddenField(validator=UnicodeString)
        return_to_day_id = HiddenField(validator=UnicodeString)
        activity_id = HiddenField(validator=UnicodeString)
        activity_name = SingleSelectField()
        
class ValidateMoveBookingForm(TableForm):
    show_errors = True
    id = HiddenField(validator=UnicodeString)
    return_to_day_id = HiddenField(validator=UnicodeString)
    activity_id = HiddenField(validator=UnicodeString)
    activity_name = SingleSelectField()
        
create_move_booking_form = MoveBookingForm("create_move_booking_form")
validate_move_booking_form = ValidateMoveBookingForm("validate_move_booking_form")
