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
define(["common_menu", "dojo/dom", "dojo/dom-attr", "dojo/_base/array", "dojo/dom-construct", "dojo/_base/window", "dijit/Menu","dijit/MenuItem", "dijit/PopupMenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/io-query", "dojo/json", "dojo/cookie", "dojo/dom-style", "dojo/domReady!"],
  function(common_menu, domAttr, dom, array, domConstruct, win, Menu, MenuItem, PopupMenuItem, CheckedMenuItem, MenuSeparator, query, ioQuery, json, cookie, domStyle)
  {

    /**
    * Sets up the calendar navigation widget
    **/
    function setup_navigation_calendar(page_config) {

      var e = dom.byId('navigation_calendar');
      domAttr.set(e, 'dojoType', 'dijit.Calendar');

      //...set the name of the callback function to call when the calendar is clicked.
      domAttr.set(e, 'onChange', 'navigation_calendar_clicked');

      //...set name of callback function that tells if a date i disabled. I think this function is defined in std.js
      domAttr.set(e, 'isDisabledDate','navigation_calendar_is_disabled');
      parser.parse(e.parentNode);

      var tools_link_elem = dom.byId('toolslink');
      var href = domAttr.get(tools_link_elem, "href");
      domAttr.get(tools_link_elem, "href", href + "?day=" + page_config.booking_day_date );
    }


    function setup(page_config) {
      //...create menu that is attached to all bookings that live in a slot
      /* Menu for bookings in slots */
      var menu_booking_in_slot_config = {
        targetNodeIds: ["booking_day_overview"],
        selector: "div.slot_booking",
        leftClickToOpen: common_menu.load_left_click_menu(),
        onOpen: function(evt) {
          var node = menu.currentTarget;
          var locked = node.attributes["hollyrosa:lock"].value;

          if (locked == 'block') {
            menu_new_booking_choice.disabled=true;
            menu_block_slot_choice.disabled = true;
            menu_unblock_slot_choice.disabled = false;
          } else {
            menu_new_booking_choice.disabled=false;
            menu_block_slot_choice.disabled = false;
            menu_unblock_slot_choice.disabled = true;
          }
        }
      }

      var menu = new Menu(menu_booking_in_slot_config);
      var menu_new_booking_choice = common_menu.add_booking_op_menu_item_for_block(menu, menu, "New booking...", page_config.book_slot_url, 'program');
      common_menu.add_menu_separator(menu);
      common_menu.add_booking_op_menu_item(menu, menu, "View...", page_config.view_booked_booking_url, 'GET');
      common_menu.add_booking_op_menu_item(menu, menu, "Edit...", page_config.edit_booked_booking_url, 'GET');
      common_menu.add_booking_op_menu_item(menu, menu, "Unschedule", page_config.unschedule_booking_url, 'POST');
      common_menu.add_menu_separator(menu);

      //...add submenu with more entries
      var more = new Menu();
      menu.addChild(new PopupMenuItem({
        label: "More...",
        leftClickToOpen: common_menu.load_left_click_menu(),
        popup: more
      }));

      common_menu.add_booking_op_menu_item(menu, more, "Move...", page_config.move_booking_url, 'GET');
      common_menu.add_booking_op_menu_item(menu, more, "Prolong", page_config.prolong_booking_url, 'POST');
      common_menu.add_menu_separator(more);

      array.forEach(common_menu.state_change_list, function(x) {common_menu.add_change_booking_state_menu_item(menu, more, x['name'], x['state'], 0, page_config.set_state_url);});
      common_menu.add_menu_separator(more);

      common_menu.add_booking_op_menu_item(menu, more, "Multi-book...", page_config.multibook_url, 'GET');
      common_menu.add_booking_op_menu_item(menu, more, "Delete", page_config.delete_booking_url, 'POST');
      common_menu.add_menu_separator(menu);
      common_menu.add_visiting_group_list_bookings_menu_item(menu, menu, "List bookings of group...", page_config.visiting_group_view_bookings_of_name_url);
      common_menu.add_visiting_group_menu_item(menu, menu, "View visiting group...", page_config.show_visiting_group_url);


      common_menu.add_menu_separator(menu);
      var menu_block_slot_choice = common_menu.add_booking_op_menu_item_for_block(menu, menu, "Block slot", page_config.block_slot_url, 'program');
      var menu_unblock_slot_choice = common_menu.add_booking_op_menu_item_for_block(menu, menu, "Unblock slot", page_config.unblock_slot_url, 'program');


      /*..........................*/
      //...create menu that is attached to all slots that have no booking in them
      var book_menu = new Menu({
        targetNodeIds: ["booking_day_overview"],
        selector: "div.slot_empty",
        leftClickToOpen: common_menu.load_left_click_menu(),
        onOpen: function(evt) {
          var node = book_menu.currentTarget;
          var locked = node.attributes["hollyrosa:lock"].value;


          if (locked == 'block') {
            book_menu_new_booking_choice.disabled=true;
            book_menu_block_slot_choice.disabled = true;
            book_menu_unblock_slot_choice.disabled = false;
          } else {
            book_menu_new_booking_choice.disabled=false;
            book_menu_block_slot_choice.disabled = false;
            book_menu_unblock_slot_choice.disabled = true;
          }
        }
      });

      var book_menu_new_booking_choice = common_menu.add_booking_op_menu_item_for_block(book_menu, book_menu, "New booking...", page_config.book_slot_url, 'program');
      common_menu.add_menu_separator(book_menu);
      var book_menu_block_slot_choice = common_menu.add_booking_op_menu_item_for_block(book_menu, book_menu, "Block slot", page_config.block_slot_url, 'program');
      var book_menu_unblock_slot_choice = common_menu.add_booking_op_menu_item_for_block(book_menu, book_menu, "Unblock slot", page_config.unblock_slot_url, 'program');



      /******************* unschedule menu ********************/

      //...create menus for bookings which are listed as unscheduled
      var unschedule_menu = new Menu({
        targetNodeIds: ["unscheduled_bookings"],
        selector: "li.unscheduled_booking",
        leftClickToOpen: common_menu.load_left_click_menu()
      });

      common_menu.add_booking_op_menu_item(unschedule_menu, unschedule_menu, "View...", page_config.view_booked_booking_url, 'GET');
      common_menu.add_visiting_group_list_bookings_menu_item(unschedule_menu, unschedule_menu, "List bookings of group", page_config.visiting_group_view_bookings_of_name_url, 'GET');
      common_menu.add_booking_op_menu_item(unschedule_menu, unschedule_menu, "Edit...", page_config.edit_unscheduled_booking_url, 'GET');
      common_menu.add_booking_op_menu_item(unschedule_menu, unschedule_menu, "Delete...", page_config.delete_unscheduled_booking_url, 'POST');


      var schedule_more_menu = new Menu();
      unschedule_menu.addChild(new PopupMenuItem({
        label: "Schedule...",
        leftClickToOpen: common_menu.load_left_click_menu(),
        popup: schedule_more_menu
      }));

      /*********************************/

      //...crete the menu for the whole bage which mostly is used to select the activity groups to show.
      //var agroups = ${"[" + ','.join( ['["'+a.id + '", "' + a.title +'"]' for a in activity_groups]   )   + "]"};
      var ag_status = common_menu.load_ag_checkbox_status();

      var view_ag_menu = new Menu({
        targetNodeIds: ["view_ag_menu"],
        leftClickToOpen: common_menu.load_left_click_menu()
      });

      common_menu.add_transfer_map_function_menu_item(view_ag_menu, view_ag_menu, "Edit day info...", page_config.edit_booking_day_url, ['booking_day_id']);
      common_menu.add_menu_separator(view_ag_menu);

      array.forEach(page_config.agroups, function(a) {
        common_menu.add_ag_checkbox_menu_item(view_ag_menu, a[1], a[0], ag_status, common_menu.update_activity_group_visible_rows);
      });

      common_menu.update_activity_group_visible_rows(ag_status);
    }

    return {
      setup:setup,
      setup_navigation_calendar:setup_navigation_calendar
    }
  }
)
