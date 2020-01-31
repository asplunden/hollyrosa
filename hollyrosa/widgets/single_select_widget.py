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
import tw2.core as twc
import tw2.forms as twf

__all__ = ['SingleSelectWidget']

class SingleSelectWidget(twf.SingleSelectField):
    inline_engine_name = "kajiki"
    template = """<div class="select is-small">
        <select py:attrs="w.attrs">
    <optgroup py:for="group, options in w.grouped_options"
              py:strip="not group"
              label="${group}" >
        <py:for each="attrs, desc in options">
            <option py:with="value=attrs.pop('value', '')"
                    value="${value}"
                    py:attrs="attrs"
                    py:content="desc"/>
        </py:for>
    </optgroup>
    </select></div>
    """

