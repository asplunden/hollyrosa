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



forms used for validating input, but where there is no reasonable user feedback"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString

class ValidateScheduleBooking(TableForm):    
    show_errors = True
    class fields(WidgetsList):
        return_to_day_id = HiddenField(validator=UnicodeString)
        booking_id = HiddenField(validator=UnicodeString)
        booking_day_id = HiddenField(validator=UnicodeString)
        slot_row_position_id = HiddenField(validator=UnicodeString)


class ValidateUnscheduleBooking(TableForm):
    show_errors = True
    class fields(WidgetsList):
        return_to_day_id = HiddenField(validator=UnicodeString)
        booking_id = HiddenField(validator=UnicodeString)
        slot_row_position_id = HiddenField(validator=UnicodeString)
        
        
class ValidateCreateNewBookingRequest(TableForm):
    show_errors = True
    id = HiddenField(validator=UnicodeString)
    return_to_day_id = HiddenField()
    visiting_group_name = TextField(validator=UnicodeString(min=1))
    visiting_group_display_name = HiddenField(validator=UnicodeString(min=1))
    visiting_group_id = HiddenField(validator=UnicodeString)
    content = TextArea(validator=UnicodeString)
    activity_id = HiddenField(validator=UnicodeString)
    activity_name = TextField(validator=UnicodeString(min=1))
    requested_date = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"), date_format='%Y-%m-%d')
    valid_from = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"), date_format='%Y-%m-%d')  
    valid_to = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"), date_format='%Y-%m-%d')
    

class ValidateBookSlotForm(TableForm):
    id = HiddenField(validator=UnicodeString)
    return_to_day_id = HiddenField()
    visiting_group_name = TextField(validator=UnicodeString(min=1))
    visiting_group_display_name = HiddenField(validator=UnicodeString(min=1))
    visiting_group_id = HiddenField(validator=UnicodeString)
    content = TextArea(validator=UnicodeString)
       

create_validate_schedule_booking = ValidateScheduleBooking("create_validate_schedule_booking")
create_validate_unschedule_booking = ValidateUnscheduleBooking("create_validate_unschedule_booking")
create_validate_new_booking_request_form = ValidateCreateNewBookingRequest("create_validate_new_booking_request")
create_validate_book_slot_form = ValidateBookSlotForm("create_validate_book_slot")