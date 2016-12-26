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

#from tw2.core import WidgetsList
import tw2.core as twc
from tw2.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField,  Label
from tw2.dynforms import GrowingTableFieldSet,  CustomisedForm
#...for form validation
from tw2.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString,  Email
from tw2.tinymce import TinyMCE, MarkupConverter

# http://toscawidgets.org/documentation/tw.dynforms/widgets/index.html

class ParamsGrowingTableFieldSet(GrowingTableFieldSet):
    children = [
        HiddenField('id'), 
        TextField('property',  size=10),
        TextField('value',  size=4),
        TextField('unit',  size=8), 
        TextField('description'), 
        CalendarDatePicker('from_date', validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d'), 
        CalendarDatePicker('to_date', validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')]
        

#class EditVisitingGroupForm(CustomisedForm):
class EditVisitingGroupForm(TableForm):
    show_errors = True
    
    class fields(WidgetsList):
        _id = HiddenField(validator=UnicodeString())
        subtype = HiddenField(validator=UnicodeString()) 
        name = TextField(validator=UnicodeString(min=1),  css_class="edit_name",  size=40)
        info = TinyMCE(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
))
        
        from_date = CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
        to_date = CalendarDatePicker(validator=DateConverter(month_style="iso"),  date_format='%Y-%m-%d')
        contact_person = TextField(validator=UnicodeString(),  label_text="contact person:")
        contact_person_email = TextField(validator=Email(resolve_domain=False))
        contact_person_phone = TextField(validator=UnicodeString())
        boknr = TextField(validator=UnicodeString())
        password = TextField(validator=UnicodeString())
        camping_location = TextField(validator=UnicodeString())
        
        visiting_group_properties = ParamsGrowingTableFieldSet()

create_edit_visiting_group_form = EditVisitingGroupForm("create_edit_visiting_group_form")
