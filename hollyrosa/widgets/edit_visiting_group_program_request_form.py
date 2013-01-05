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
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea,  HiddenField,  CheckBox

from hollyrosa.widgets.visiting_group_program_request_widget import VisitingGroupProgramRequestWidget
from hollyrosa.widgets.div_widget import DivWidget

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString,  Email
from tw.tinymce import TinyMCE, MarkupConverter


class EditVisitingGroupProgramRequestForm(TableForm):
    
    show_errors = True

    class fields(WidgetsList):
        id = HiddenField(validator=UnicodeString())
        title = TextField(validator=UnicodeString(min=1),  css_class="edit_name")
        info = TinyMCE(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
                                                                   ))
        contact_person = TextField(validator=UnicodeString())
        contact_person_email = TextField(validator=UnicodeString())
        contact_person_phone = TextField(validator=UnicodeString())
        from_date = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')
        
        to_date = CalendarDatePicker(validator=DateConverter(month_style="yyyy-mm-dd"),  date_format='%Y-%m-%d')
        
        
        grid_a = DivWidget(value='xyz')
        grid_b = VisitingGroupProgramRequestWidget(value='xxx')
        

create_edit_visiting_group_program_request_form = EditVisitingGroupProgramRequestForm("create_edit_visiting_group_program_request_form")


#
# deltar i miniscout ?
# deltar i 60 degrees north ? 
#
# skriv ut ref.nr.
#
# fromdate
# todate
# ---
# age group matrix with dates and numbers and names
#
# ---
# 
# program request rows ...
# 
# datum - fm/em/kvall/annat - age-groups (crosses) - activity // how do we confirm this ???
#
# We will use this system one or two years, then move on, but we need your help,
#
# Dojo grid needed... how to achieve it? Dojo form from start to finnish ?
# Handcrafted form ?
# How to add Dojo form to python form ??? 
# Maybe we need to write a custom dojo grid widget and use it as widget in widget ?

#
#