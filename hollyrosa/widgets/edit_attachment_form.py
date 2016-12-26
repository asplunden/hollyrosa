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



#from tw.api import WidgetsList
#from tw.forms import TableForm, TextField, TextArea, HiddenField, CheckBox, FileField


#...for form validation
#from tw.forms.validators import Int, NotEmpty, DateConverter, UnicodeString

import tw2.core as twc
import tw2.forms as twf

from tg import lurl

class EditAttachmentForm(twf.Form):
    
    #show_errors = True

    #class fields(WidgetsList):
    class Children(twf.TableLayout):
        recid = twf.HiddenField(validator=twc.Required())
        target_id = twf.HiddenField(validator=twc.Required())

        text = twf.TextField(validator=twc.Required())
        attachment = twf.FileField()
        
    action = lurl('save_attachment')

create_edit_attachment_form = EditAttachmentForm() #"create_edit_attachment_form")
