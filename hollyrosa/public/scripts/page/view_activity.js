/**
* Copyright 2010-2020 Martin Eliasson
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


define(["common_menu", "dojo/dom", "dojo/dom-attr", "dojo/_base/array", "dojo/dom-construct", "dojo/_base/window", "dijit/Menu","dijit/MenuItem", "dijit/PopupMenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/io-query", "dojo/json", "dojo/cookie", "dojo/dom-style", "dojo/domReady!"],
  function(common_menu, domAttr, dom, array, domConstruct, win, Menu, MenuItem, PopupMenuItem, CheckedMenuItem, MenuSeparator, query, ioQuery, json, cookie, domStyle)
  {

    function setup(page_config) {
      var view_activity_menu = new Menu({
        targetNodeIds: ["view_activity_menu"],
        leftClickToOpen: common_menu.load_left_click_menu()
      });

      common_menu.add_transfer_map_function_menu_item(view_activity_menu, view_activity_menu, "Edit activity...", page_config.edit_activity_url, ['activity_id']);
      common_menu.add_transfer_map_function_menu_item(view_activity_menu, view_activity_menu, "Edit special booking info note...", page_config.edit_special_info_note_url, ['note_id']);
      common_menu.add_menu_separator(view_activity_menu);
      common_menu.add_transfer_map_function_menu_item(view_activity_menu, view_activity_menu, "Open internal link", page_config.internal_link_url, []);
      common_menu.add_transfer_map_function_menu_item(view_activity_menu, view_activity_menu, "Open external link", page_config.external_link_url, []);
      common_menu.add_call_function_menu_item(view_activity_menu, view_activity_menu, "Open print on demand link", function(node) { page_config.printOnDemand();} );
    }

  return {
    setup:setup
  }
})
