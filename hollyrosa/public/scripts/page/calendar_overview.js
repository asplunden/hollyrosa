/**
* Copyright 2010-2017 Martin Eliasson
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

/**
Modules that can be loaded:

**/
define(["common_menu", "dojo/dom-attr", "dojo/_base/array", "dojo/dom-construct", "dojo/_base/window", "dijit/Menu","dijit/MenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/io-query", "dojo/json", "dojo/cookie", "dojo/dom-style", "dojo/domReady!"],
  function(common_menu, domAttr, array, domConstruct, win, Menu, MenuItem, CheckedMenuItem, MenuSeparator, query, ioQuery, json, cookie, domStyle)
{

  function setup(page_config) {
    var menu = new Menu(page_config.menu_config);
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, 'Day overview', page_config.booking_day_url, ['booking_day_id'], {}, 'GET' );
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, 'Room overview', page_config.booking_live_url, ['booking_day_id'],  {subtype:'room'}, 'GET');
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, 'Staff overview', page_config.booking_live_url, ['booking_day_id'],  {subtype:'staff'}, 'GET');
    common_menu.add_menu_separator(menu);

    // TODO: for the edit controller, booking_day_id is now called bdayid, also check the day template
    common_menu.add_transfer_map_function_menu_item(menu, menu, "Edit day info...", page_config.calendar_edit_booking_day_url, ['booking_day_id']);
    common_menu.add_menu_separator(menu);

    // TODO: changed parameter name from at_date to bdate
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, "Visiting groups this day", page_config.visiting_group_view_at_date_url, ['date'], {},'GET');
    common_menu.add_menu_separator(menu);

    // TODO: day changed name to bdate
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, "Fladan schema", page_config.booking_fladan_day_url, ['date'], {ag: "activity_group.6"},'GET');
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, "Trapper schema", page_config.booking_fladan_day_url, ['date'], {ag: "activity_group.1"},'GET');
    common_menu.add_transfer_map_function_menu_item_2(menu, menu, 'All schema', page_config.booking_fladan_day_url, ['date'], {}, 'GET');
  }

  return {
    setup:setup
    };
});
