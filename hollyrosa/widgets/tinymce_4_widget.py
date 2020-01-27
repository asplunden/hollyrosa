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

import logging

import tw2.core as twc
from hollyrosa.controllers.common import cleanHtml
from tw2.forms import TextArea

log = logging.getLogger(__name__)

__all__ = ['TinyMCE4Widget']

# link to folder and main file of tinymce. These must be placed in the public folder
# separately. Download from: http://download.tiny.cloud/tinymce/community/tinymce_4.9.7.zip , copy to public folder,
# unzip there and delete the zip file.

tinymce_dir = twc.DirLink(link="/scripts/tinymce/js/tinymce", filename='', modname='')
tinymce_js = twc.JSLink(link='/scripts/tinymce/js/tinymce/tinymce.min.js',
                        init=twc.js_function('tinymce.init'), filename='', modname='')


class HtmlConverter(twc.validation.Validator):
    """A validator for TinyMCE widget."""

    def __init__(self, **kw):
        twc.validation.Validator.__init__(self, **kw)

    def _to_python(self, value, state=None):
        value = super(HtmlConverter, self)._to_python(value, state)
        if value:
            value = cleanHtml(value)
            return value
        else:
            return None


class TinyMCE4Widget(TextArea):
    """
    A tinymce v4 widget. It is an ehnhanced textarea so no need for a template.
    """

    # this is where the JS resources are declared for the widget
    resources = [tinymce_js, tinymce_dir]
    include_dynamic_js_calls = True

    # setup the validator
    validator = HtmlConverter()

    # use all plugins except: pagebreak, wordcount, save, template
    default_options = dict(
        toolbar="formatselect fontselect | bold italic underline strikethrough bullist numlist outdent indent | "
                "forecolor backcolor | cut copy paste | undo | link unlink removeformat | image",
        menubar="edit view format insert",
        plugins=[
            'advlist autolink link image lists charmap print preview hr anchor spellchecker',
            'searchreplace visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
            'table contextmenu directionality emoticons paste textcolor'
        ],
    )

    def prepare(self):
        """
        Set options to default options and then set the 'selector' option to # + name of widget,
        tinymce.init must be given the option selector: #name

        Finally, call the tinymce.init script after widget is created, this causes a js call to be created in the
        html file that is generated.
        """
        super(TinyMCE4Widget, self).prepare()
        options = self.default_options.copy()
        options['selector'] = '#' + self.attrs['name']
        self.add_call(tinymce_js.init(options))
