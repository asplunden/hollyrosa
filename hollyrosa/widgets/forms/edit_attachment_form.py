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

import tw2.core as twc
import tw2.forms as twf

from tg import lurl


class EditAttachmentForm(twf.Form):
    class child(twf.TableLayout):
        # attachment_id was previously recid but should it be note id?
        attachment_id = twf.HiddenField(validator=twc.Required)
        target_id = twf.HiddenField(validator=twc.Required)

        text = twf.TextField(validator=twc.Required, css_class="input is-small")
        attachment = twf.FileField()

    action = lurl('save_attachment')


create_edit_attachment_form = EditAttachmentForm()
