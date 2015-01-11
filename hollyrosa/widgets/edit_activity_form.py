"""
Copyright 2010-2015 Martin Eliasson

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

# http://wiki.moxiecode.com/index.php/TinyMCE:Control_reference

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField,  CheckBox

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString,  Email
from tw.tinymce import TinyMCE, MarkupConverter


class EditActivityForm(TableForm):
    
    show_errors = True

    class fields(WidgetsList):
        id = HiddenField(validator=UnicodeString())
        title = TextField(validator=UnicodeString(min=1),  css_class="edit_name")
        description = TinyMCE(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
                                                                   ))
        tags = TextField(validator=UnicodeString())
        external_link = TextField(validator=UnicodeString())
        internal_link = TextField(validator=UnicodeString())
        print_on_demand_link = TextField(validator=UnicodeString())
        capacity = TextField(size=4, validator=Int)
        default_booking_state = HiddenField()
        activity_group_id = SingleSelectField(validator=UnicodeString())
        gps_lat  = TextField(validator=UnicodeString())
        gps_long = TextField(validator=UnicodeString())
        equipment_needed = CheckBox()
        education_needed  = CheckBox()
        certificate_needed = CheckBox()
        bg_color = TextField(validator=UnicodeString())
        guides_per_slot = TextField(validator=UnicodeString(size=4, validator=Int))
        guides_per_day = TextField(validator=UnicodeString(size=4, validator=Int))
        
        
        
        

create_edit_activity_form = EditActivityForm("create_edit_activity_form")
