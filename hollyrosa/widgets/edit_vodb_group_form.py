"""
Copyright 2010, 2011, 2012, 2013 Martin Eliasson

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
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField,  Label
from tw.dynforms import GrowingTableFieldSet,  CustomisedForm
#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString,  Email
from tw.tinymce import TinyMCE, MarkupConverter

# http://toscawidgets.org/documentation/tw.dynforms/widgets/index.html

class ParamsGrowingTableFieldSet(GrowingTableFieldSet):
    children = [
        HiddenField('id'), 
        TextField('property',  size=10),
        TextField('value',  size=4),
        TextField('unit',  size=8), 
        TextField('description'), 
        CalendarDatePicker('from_date', validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d'), 
        CalendarDatePicker('to_date', validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')]
        


class EditVodbGroupForm(TableForm):
    show_errors = True
    
    class fields(WidgetsList):
        _id = HiddenField(validator=UnicodeString())
        subtype = HiddenField(validator=UnicodeString()) 
        name = TextField(validator=UnicodeString(min=1),  css_class="edit_name",  size=40)
        boknr = TextField(validator=UnicodeString())
        
        info = TinyMCE(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
))
        from_date = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')
        to_date = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')
        vodb_contact_name = TextField(validator=UnicodeString())
        vodb_contact_email = TextField(validator=Email(resolve_domain=False))
        vodb_contact_phone = TextField(validator=UnicodeString())
        vodb_contact_address = TextArea(validator=UnicodeString(), rows=4)
        
        camping_location = TextField(validator=UnicodeString())
        
        visiting_group_properties = ParamsGrowingTableFieldSet()

create_edit_vodb_group_form = EditVodbGroupForm("create_edit_vodb_group_form")
