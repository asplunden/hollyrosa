# -*- coding: utf-8 -*-

"""
Copyright 2010-2020 Martin Eliasson

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

import tw2.core as twc
import tw2.forms as twf

from hollyrosa.widgets.tinymce_4_widget import TinyMCE4Widget

from hollyrosa.model import getHollyCouch
from hollyrosa.model.booking_couch import getAllActivityGroups
from hollyrosa.widgets.single_select_widget import SingleSelectWidget

def _getActivityGroupOptions():
    """
    return a list of all available activity groups
    """
    activity_groups = list()
    for x in getAllActivityGroups(getHollyCouch()):
        activity_groups.append((x.value['_id'], x.value['title']))
    return activity_groups


class EditActivityForm(twf.Form):
    class child(twf.TableLayout):
        id = twf.HiddenField()
        language = twf.HiddenField(validator=twc.Required)
        title = twf.TextField(validator=twc.Required, css_class="edit_name input is-medium")
        description = TinyMCE4Widget()
        tags = twf.TextField(css_class="input is-small")
        external_link = twf.UrlField(css_class="input is-small")
        internal_link = twf.UrlField(css_class="input is-small")
        print_on_demand_link = twf.UrlField(css_class="input is-small")
        capacity = twf.NumberField(validator=twc.IntValidator, css_class="input is-small")
        default_booking_state = twf.HiddenField()
        activity_group_id = SingleSelectWidget(validator=twc.Required,
                                                  options=twc.Deferred(_getActivityGroupOptions))
        gps_lat = twf.TextField(css_class="input is-small")
        gps_long = twf.TextField(css_class="input is-small")
        equipment_needed = twf.CheckBox(css_class="checkbox is-small")
        education_needed = twf.CheckBox(css_class="checkbox is-small")
        certificate_needed = twf.CheckBox(css_class="checkbox is-small")
        bg_color = twf.ColorField(validator=twc.Required, css_class="input is-small")
        guides_per_slot = twf.NumberField(validator=twc.IntValidator, css_class="input is-small")
        guides_per_day = twf.NumberField(validator=twc.IntValidator, css_class="input is-small")

    action = lurl('save')


create_edit_activity_form = EditActivityForm()
