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

import tw2.core as twc
import tw2.forms as twf
import tw2.dynforms as twd

from tg import lurl

from tw2.tinymce import TinyMCEWidget, MarkupConverter
from formencode.validators import DateConverter

class EditVodbGroupForm(twd.CustomisedTableForm):
    class child(twf.TableLayout):
        vodb_group_id = twf.HiddenField(validator=twc.Required)
        subtype = twf.HiddenField(validator=twc.Required) 
        name = twf.TextField(validator=twc.StringLengthValidator(min=4), css_class="edit_name", size=40)
        boknr = twf.TextField(validator=twc.Required)

        info = TinyMCEWidget(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
))
        from_date = twf.CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
        to_date = twf.CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
        vodb_contact_name = twf.TextField(validator=twc.Required)
        vodb_contact_email = twf.TextField(validator=twc.EmailValidator)
        vodb_contact_phone = twf.TextField(validator=twc.Required)
        vodb_contact_address = twf.TextArea(validator=twc.StringLengthValidator(min=4))
        camping_location = twf.TextField(validator=twc.Required)

        class visiting_group_properties(twd.GrowingGridLayout):
            propery_id = twf.HiddenField('property_id')
            property = twf.TextField('property',  size=10)
            value = twf.TextField('value',  size=4)
            unit = twf.TextField('unit',  size=8)
            description = twf.TextField('description')
            from_date = twf.CalendarDatePicker('from_date', validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
            to_date = twf.CalendarDatePicker('to_date', validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')

    action = lurl('save_vodb_group_properties')
create_edit_vodb_group_form = EditVodbGroupForm()
