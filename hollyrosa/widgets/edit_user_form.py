"""
Copyright 2010, 2011, 2012, 2013, 2014, 2015, 2016 Martin Eliasson

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
from tw.forms import TableForm, TextField, TextArea, HiddenField, CheckBox

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter, UnicodeString


class EditUserForm(TableForm):
    
    show_errors = True

    class fields(WidgetsList):
        _id = HiddenField(validator=UnicodeString)
        user_name = TextField(validator=UnicodeString)
        display_name = TextField(validator=UnicodeString)
        
        
create_edit_user_form = EditUserForm("create_edit_user_form")
