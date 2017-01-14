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

#...for form validation
from tw2.tinymce import MarkupConverter # TinyMCE
from tw2.tinymce import TinyMCEWidget

from hollyrosa.model import holly_couch
from hollyrosa.model.booking_couch import getAllActivityGroups

def getActivityGroupOptions():
    activity_groups = list()
    for x in getAllActivityGroups(holly_couch):
        activity_groups.append((x.value['_id'], x.value['title']))   
    return activity_groups

class EditActivityForm(twf.Form):
    
    class child(twf.TableLayout):
        
        
        id = twf.HiddenField()
        title = twf.TextField(validator=twc.Required,  css_class="edit_name")
        description = TinyMCEWidget(validator=MarkupConverter, mce_options = dict(theme='advanced',  
                                                                   theme_advanced_toolbar_align ="left",  
                                                                   theme_advanced_buttons1 = "formatselect,fontselect, bold,italic,underline,strikethrough,bullist,numlist,outdent,indent,forecolor,backcolor,separator,cut,copy,paste,separator, undo,separator,link,unlink,removeformat", 
                                                                   theme_advanced_buttons2 = "",
                                                                   theme_advanced_buttons3 = ""
                                                                   ))
        tags = twf.TextField()#validator=twc.String)
        external_link = twf.TextField()#validator=twc.Required)
        internal_link = twf.TextField()#validator=twc.Required)
        print_on_demand_link = twf.TextField()#validator=twc.Required)
        capacity = twf.TextField(validator=twc.IntValidator) # TODO: should be inteteger here
        default_booking_state = twf.HiddenField()
        activity_group_id = twf.SingleSelectField(validator=twc.Required, options=twc.Deferred(getActivityGroupOptions)) # TODO: what to do with options, see perhaps http://code.runnable.com/U-tO4xSN7Ch6wWS7/turbogears-forms-fill-singleselect-value-for-python
        gps_lat  = twf.TextField()#validator=twc.Required)
        gps_long = twf.TextField()#validator=twc.Required)
        equipment_needed = twf.CheckBox()
        education_needed  = twf.CheckBox()
        certificate_needed = twf.CheckBox()
        bg_color = twf.TextField(validator=twc.Required)
        guides_per_slot = twf.TextField(validator=twc.IntValidator)
        guides_per_day = twf.TextField(validator=twc.IntValidator)
        
        
    action = lurl('save_activity_properties')
        

create_edit_activity_form = EditActivityForm() #####"create_edit_activity_form")
