/**
 * Copyright 2010-2015 Martin Eliasson
 *
 * This file is part of Hollyrosa
 *
 * Hollyrosa is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Hollyrosa is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.
 **/
 
define(["dojo/dom-attr", "dojo/_base/array", "dijit/Menu","dijit/MenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/io-query", "dojo/json", "dojo/cookie"], function(domAttr, array, Menu, MenuItem, CheckedMenuItem, MenuSeparator, query, ioQuery, json, cookie) {

	function get_url_from_dict(a_url, a_params) {
		if ('' != a_params) {
			return a_url + '?' + ioQuery.objectToQuery(a_params);
		} else {
			window.location = a_url;
		}
	}
		
	
	return {
		get_url_from_dict:get_url_from_dict
		};
	});
	
