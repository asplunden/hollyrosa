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

# http://wiki.moxiecode.com/index.php/TinyMCE:Control_reference

from tg import lurl

#from tw.api import WidgetsList
import tw2.core as twc
import tw2.forms as twf
####from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField,  CheckBox

#...for form validation
#from tw2.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString,  Email
from tw2.tinymce import MarkupConverter # TinyMCE
from tw2.tinymce import TinyMCEWidget

class EditActivityForm(twf.Form):
    
    ####show_errors = True
    ####class fields(WidgetsList):
    
    class child(twf.TableLayout):
        id = twf.HiddenField()
        title = twf.TextField(validator=twc.Required,  css_class="edit_name")
        description = TinyMCEWidget(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
                                                                   ))
        tags = twf.TextField(validator=twc.Required)
        external_link = twf.TextField(validator=twc.Required)
        internal_link = twf.TextField(validator=twc.Required)
        print_on_demand_link = twf.TextField(validator=twc.Required)
        capacity = twf.TextField(validator=twc.StringLengthValidator(min=4)) # TODO: should be inteteger here
        default_booking_state = twf.HiddenField()
        activity_group_id = twf.SingleSelectField(validator=twc.Required, options=[]) # TODO: what to do with options
        gps_lat  = twf.TextField(validator=twc.Required)
        gps_long = twf.TextField(validator=twc.Required)
        equipment_needed = twf.CheckBox()
        education_needed  = twf.CheckBox()
        certificate_needed = twf.CheckBox()
        bg_color = twf.TextField(validator=twc.Required)
        guides_per_slot = twf.TextField() ##### validator=UnicodeString(size=4, validator=Int)
        guides_per_day = twf.TextField() #### validator=UnicodeString(size=4, validator=Int)
        
        
    action = lurl('save_activity_properties')
        

create_edit_activity_form = EditActivityForm() #####"create_edit_activity_form")
