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
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField
#from tw.dojo import Dojo

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter, UnicodeString


class EditNewBookingRequestForm(TableForm):

    class fields(WidgetsList):
        
        id = HiddenField(validator=Int)
        #booking_day_id = HiddenField()
        return_to_day_id = HiddenField()
        visiting_group_name =  TextField(validator=UnicodeString(min=1),  css_class="edit_name",  size=40)
        visiting_group_id = SingleSelectField(validator=Int)
        content = TextArea(validator=UnicodeString)
        activity_id = SingleSelectField(validator=Int)
        requested_date = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')
        valid_from = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')              #date_format='%Y-%m-%d')
        valid_to = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')                        #date_format='%Y-%m-%d')
        
        

create_edit_new_booking_request_form = EditNewBookingRequestForm("create_edit_new_booking_request_form")
