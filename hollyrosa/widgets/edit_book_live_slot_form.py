"""
Copyright 2010-2017 Martin Eliasson

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
from formencode.validators import DateConverter

from hollyrosa.widgets.SingleSelectFieldMod import SingleSelectFieldMod

class EditBookLiveSlotForm(twf.Form):
	    
    class child(twf.TableLayout):
    
        slot_position = twc.Param('test options for now for single select field', default=['x','y'])

        
        def getSlotIdOptions():
            return slot_position
    
    
        booking_id = twf.HiddenField(validator=twc.Required)
        booking_day_id = twf.HiddenField(validator=twc.Required)
        subtype = twf.HiddenField(validator=twc.Required)
        activity_id = twf.HiddenField(validator=twc.Required)
        return_to_day_id = twf.HiddenField(validator=twc.Required)
        visiting_group_name = twf.TextField(validator=twc.StringLengthValidator(min=1), css_class="edit_name", size=40)
        visiting_group_display_name = twf.HiddenField(validator=twc.StringLengthValidator(min=1))        
        visiting_group_id = twf.HiddenField(validator=twc.Required)
        booking_date = twf.CalendarDatePicker('start_date', validator=DateConverter(month_style="iso"), date_format='%Y-%m-%d')
        
        slot_id = twf.SingleSelectField(validator=twc.Required, options=[])
        
        booking_end_date = twf.CalendarDatePicker('end_date', validator=DateConverter(month_style="iso"), date_format='%Y-%m-%d')
        
        booking_end_slot_id = SingleSelectFieldMod(validator=twc.Required, options=None, prompt_text=None, label="end time")
        
        content = twf.TextArea(twc.Required, css_class="edit_booking_content", rows=5, cols=30)
        block_after_book = twf.CheckBox()

	action = lurl('save_booked_live_booking_properties')


    #def prepare(self):
    # 	
    #    super(EditBookLiveSlotForm, self).prepare()
        

create_edit_book_live_slot_form = EditBookLiveSlotForm()

