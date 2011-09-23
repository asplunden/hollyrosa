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



forms used for validating input, but where there is no reasonable user feedback"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString

class ValidateScheduleBooking(TableForm):    
    show_errors = True
    class fields(WidgetsList):
        booking_day_id = HiddenField(validator=Int)
        booking_id = HiddenField(validator=Int)


class ValidateUnscheduleBooking(TableForm):
    show_errors = True
    class fields(WidgetsList):
        booking_day_id = HiddenField(validator=Int)
        booking_id = HiddenField(validator=Int)
        slot_row_position_id = HiddenField(validator=Int)

create_validate_schedule_booking = ValidateScheduleBooking("create_validate_schedule_booking")
create_validate_unschedule_booking = ValidateUnscheduleBooking("create_validate_unschedule_booking")
