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

/**
Modules that can be loaded:

**/
define(["common_menu", "page/tag_and_note", "dojo/dom-attr", "dojo/_base/array", "dojo/dom-construct", "dojo/_base/window", "dijit/Menu","dijit/MenuItem", "dijit/PopupMenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/io-query", "dojo/json", "dojo/cookie", "dojo/dom-style", "dojo/domReady!"],
  function(common_menu, tagAndNote, domAttr, array, domConstruct, win, Menu, MenuItem, PopupMenuItem, CheckedMenuItem, MenuSeparator, query, ioQuery, json, cookie, domStyle)
{

  function setup(page_config) {


    var menu = new Menu({
      targetNodeIds: ["vgroup_listing"],
      selector: "tr.name_menu",
      leftClickToOpen: common_menu.load_left_click_menu(),
      onOpen: function(evt) {
        var node = menu.currentTarget;
        var has_notes = node.attributes["hollyrosa:has_notes"].value;

        if (has_notes == 'True') {
          load_notes_menu_item.disabled = false;
        } else {
          load_notes_menu_item.disabled = true;
        }
      } // end function
    });


    common_menu.add_visiting_group_menu_item(menu, menu, "View vodb data...", page_config.show_vodb_group_url);
    common_menu.add_visiting_group_menu_item(menu, menu, "Edit vodb data...", page_config.edit_vodb_group_url);


    common_menu.add_visiting_group_menu_item(menu, menu, "Edit vodb sheet...", page_config.edit_vodb_group_sheet_url);
    common_menu.add_menu_separator(menu);

    common_menu.add_call_function_menu_item(menu, menu, "Add tags...",  tagAndNote.show_add_tag_dialog  );
    common_menu.add_visiting_group_add_note_menu_item(menu, menu, "Add note...", page_config.add_note_url);
    common_menu.add_visiting_group_add_note_menu_item(menu, menu, "Add attachment...", page_config.add_attachment_url);
    common_menu.add_menu_separator(menu);

    common_menu.add_visiting_group_menu_item(menu, menu, "List bookings of group...", page_config.view_bookings_of_visiting_group_id_url);

    var load_notes_menu_item = new MenuItem({
      label: "Load notes",
      onClick: function(evt) {
        var node = this.getParent().currentTarget;
        var vgroup_id = node.attributes["hollyrosa:vgid"].value;
        tagAndNote.loadNotesFor(vgroup_id, page_config.tag_and_note_config);

        //...this isn't bulletproof, should be in a callback after the notes have loaded.
        var node = menu.currentTarget;
        node.attributes["hollyrosa:has_notes"].value = "False";
      }
    });
    menu.addChild(load_notes_menu_item);

    common_menu.add_menu_separator(menu);
    common_menu.add_visiting_group_menu_item(menu, menu, "Show history...", page_config.show_history_url);


    // assembling the filter booking status menu
    var filter_menu = new Menu({
      targetNodeIds: ["bokn_status_menu"],
      leftClickToOpen: common_menu.load_left_click_menu()
    });

    common_menu.add_redirect_menu_item(filter_menu, filter_menu, "All vodb groups", '', page_config.vodb_groups_view_all_url);
    common_menu.add_redirect_menu_item(filter_menu, filter_menu, "All vodb groups today", '', page_config.vodb_groups_view_today_url);
    common_menu.add_menu_separator(filter_menu);

    common_menu.add_redirect_menu_item(filter_menu, filter_menu, "New Visiting Group", '', page_config.new_vodb_group_visiting_group_url);
    common_menu.add_redirect_menu_item(filter_menu, filter_menu, "New Staff Member", '', page_config.new_vodb_group_staff_url);
    common_menu.add_redirect_menu_item(filter_menu, filter_menu, "New Course", '', page_config.new_vodb_group_course_url);
    common_menu.add_menu_separator(filter_menu);








    var vodb_state_menu = new Menu();
    filter_menu.addChild(new PopupMenuItem({
      label: "Select on VODB status...",
      popup: vodb_state_menu,
      leftClickToOpen: common_menu.load_left_click_menu()
    }));

    var bokn_status_menu = new Menu();
    filter_menu.addChild(new PopupMenuItem({
      label: "Select on Program status...",
      popup: bokn_status_menu,
      leftClickToOpen: common_menu.load_left_click_menu()
    }));


    var tag_menu = new Menu();
    filter_menu.addChild(new PopupMenuItem({
      label: "Select Tags...",
      popup: tag_menu,
      leftClickToOpen: common_menu.load_left_click_menu()
    }));


    var date_range_menu = new Menu();
    filter_menu.addChild(new PopupMenuItem({
      label: "Select Date range...",
      popup: date_range_menu,
      leftClickToOpen: common_menu.load_left_click_menu()
    }));

    common_menu.add_menu_separator(filter_menu);




    var view_vgt_menu = new Menu();
    filter_menu.addChild(new PopupMenuItem({
      label: "Filter on Group Type...",
      popup: view_vgt_menu,
      leftClickToOpen: common_menu.load_left_click_menu()
    }));


    array.forEach(page_config.program_state_map, function(l) {
      common_menu.add_redirect_menu_item(filter_menu, bokn_status_menu, l[1], {program_state:l[0]}, page_config.view_program_state_url);
    });

    array.forEach(page_config.vodb_state_map, function(l) {
      common_menu.add_redirect_menu_item(filter_menu, vodb_state_menu, l[1], {'vodb_state':l[0]}, page_config.view_vodb_state_url);
    });


    array.forEach(tag_and_note_config.all_tags, function(l) {
      common_menu.add_redirect_menu_item(filter_menu, tag_menu, l, {tag:l}, tag_and_note_config.view_tags_url);
    });

    /* assembling the filter tag menu */

    var vgtgroups = page_config.visiting_group_type_list;
    var vgt_status = common_menu.load_ag_checkbox_status();

    array.forEach(vgtgroups, function(a) {
      common_menu.add_ag_checkbox_menu_item(view_vgt_menu, a[1], a[0], vgt_status, common_menu.update_visiting_group_type_visible_rows);
    });

    common_menu.update_visiting_group_type_visible_rows(vgt_status);

  }
  return {
    setup: setup
  }
});
