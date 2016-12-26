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

import tw2.core as twc
import tw2.forms as twf
import tw2.dynforms as twd

from tg import lurl

from tw2.tinymce import TinyMCEWidget, MarkupConverter
from formencode.validators import DateConverter


        

class EditVisitingGroupForm(twd.CustomisedTableForm):
    class child(twf.TableLayout):
        visiting_group_id = twf.HiddenField(validator=twc.Required)
        subtype = twf.HiddenField(validator=twc.Required) 
        name = twf.TextField(validator=twc.StringLengthValidator(min=1),  css_class="edit_name",  size=40)
        info = TinyMCEWidget(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""))

        from_date = twf.CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
        to_date = twf.CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
        contact_person = twf.TextField(validator=twc.Required, label_text="contact person:")
        contact_person_email = twf.TextField(validator=twc.EmailValidator)
        contact_person_phone = twf.TextField(validator=twc.Required)
        boknr = twf.TextField(validator=twc.Required)
        password = twf.TextField(validator=twc.Required)
        camping_location = twf.TextField(validator=twc.Required)

        class visiting_group_properties(twd.GrowingGridLayout):
            extra_reps = 1
            property_id = twf.HiddenField()
            property = twf.TextField(size=10)
            value = twf.TextField(size=4)
            unit = twf.TextField(size=8)
            description = twf.TextField()
            from_date = twf.CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
            to_date = twf.CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')

    action = lurl('save_visiting_group_properties')

create_edit_visiting_group_form = EditVisitingGroupForm()
