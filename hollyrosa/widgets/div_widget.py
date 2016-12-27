"""
Copyright 2013, 2014, 2015, 2016 Martin Eliasson

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



forms used for validating input, but where there is no reasonable user feedback"""

from tw.api import Widget, JSLink, CSSLink
from tw.forms.fields import FormField

#...for form validation
#from tw.forms.validators import Int, NotEmpty, DateConverter,  UnicodeString


__all__ = ["DivWidget"]


# declare your static resources here

## JS dependencies can be listed at 'javascript' so they'll get included
## before
dojo_js = JSLink(link='/scripts/dojo-release-1.8.0/dojo/dojo.js', javascript=[])
my_js = JSLink(link='/scripts/div_widget.js', javascript=[dojo_js])

my_css = CSSLink(link='/css/div_widget.css')
ext_dojo_css = CSSLink(link='/scripts/dojo-release-1.8.0/dojox/grid/resources/tundraGrid.css')
#more_css = CSSLink(link='/scrips/dojo-release-1.8.0/dojox/resources/dojo.css";')

#modname='hollyrosa', filename='/static/css/div_widget.css', 


class DivWidget(FormField):
    template = """<div id="${id}">${value} <input type="hidden" name="${id}_input" id="${id}_input" value=""/></div>"""
    javascript = [my_js]
    css = [ext_dojo_css, my_css ] #, more_css]
    id ="age_group_div"
	
    def __init__(self, id=None, parent=None, children=[], **kw):
        """Initialize the widget here. The widget's initial state shall be
        determined solely by the arguments passed to this function; two
        widgets initialized with the same args. should behave in *exactly* the
        same way. You should *not* rely on any external source to determine
        initial state."""
        super(DivWidget, self).__init__(id, parent, children, **kw)

    def update_params(self, d):
        """This method is called every time the widget is displayed. It's task
        is to prepare all variables that are sent to the template. Those
        variables can accessed as attributes of d."""
        super(DivWidget, self).update_params(d)