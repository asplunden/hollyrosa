"""
Copyright 2010, 2011, 2012 Martin Eliasson

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
from tw.forms import TableForm, TextField, TextArea,  HiddenField,  CheckBox

#...for form validation
from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString
from tw.tinymce import TinyMCE, MarkupConverter


class EditNoteForm(TableForm):
    
    show_errors = True

    class fields(WidgetsList):
        _id = HiddenField(validator=UnicodeString)
        target_id = HiddenField(validator=UnicodeString)

        text = TinyMCE(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
                                                                   ))
        
        
        
        

create_edit_note_form = EditNoteForm("create_edit_note_form")
