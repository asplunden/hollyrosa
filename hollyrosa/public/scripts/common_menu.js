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

define(["dojo/dom-attr", "dojo/_base/array", "dojo/dom-construct", "dojo/_base/window", "dijit/Menu","dijit/MenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/io-query", "dojo/json", "dojo/cookie", "dojo/dom-style", "dojo/domReady!"], function(domAttr, array, domConstruct, win, Menu, MenuItem, CheckedMenuItem, MenuSeparator, query, ioQuery, json, cookie, domStyle) {


  /**
  * Make a form element and the end of the body, set invisible, add form elements (all can be hidden) and then post it / submit it.
  *
  * body_elem is a reference to the body element itself.
  */
  function make_form_and_post(action, values) {
    var body_elem = win.body();
    var form_elem = domConstruct.create('form', { method:'post', enctype:"multipart/form-data", action:action }, body_elem);
    for (var key in values) {
      domConstruct.create('input', { type:'hidden', name:key, value:values[key] }, form_elem);
    }
    form_elem.submit();
  }


  /**
   * Adds a menu separator to a menu
   **/
  function add_menu_separator(menu) {
    menu.addChild(new MenuSeparator());
  }


  /**
   * Adds a redirect menu item, redirect menu items are used for
   * changing the current windows addres and are basically GET
   * requests.
   *
   * Backend should make sure to guard agains pages that loads (GET) and
   * at the same time have a side effect.
   **/
  function add_redirect_menu_item(a_menu, a_sub_menu, a_name, a_params, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        if ('' != a_params) {
          window.location = a_url + '?' + ioQuery.objectToQuery(a_params);
        } else {
          window.location = a_url;
        }
      }
    }));
  }

  /**
   * Add a visiting group redirect menu item,
   *   this is a menu item which uses a visiting_group_id attribute when attaching
   *   the menu
   **/
  function add_vgid_redirect_menu_item(a_menu, a_sub_menu, a_name, a_vgid, a_url) {
    var l_params = {
      visiting_group_id: a_vgid
    }
    add_redirect_menu_item(a_menu, a_sub_menu, a_name, l_params, a_url);
  }


  function add_calc_sheet_redirect_menu_item(a_menu, a_sub_menu, a_name, a_vgid, a_live, change_schema, a_url) {
    console.log('add_calc_sheet_redirect_menu_item');
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var ioq = {
          visiting_group_id: a_vgid,
          live: a_live,
          change_schema: change_schema
        }
        make_form_and_post(a_url, ioq);
    }}));
  }


  function add_note_redirect_menu_item(a_menu, a_sub_menu, a_name, a_target_id, a_url) {
    var l_params = {
      target_id: a_target_id
    }
    add_redirect_menu_item(a_menu, a_sub_menu, a_name, l_params, a_url);
  }


  function add_list_bookings_redirect_menu_item(a_menu, a_sub_menu, a_name, a_vgroup_name, a_url) {
    var l_params = {
      name: a_vgroup_name,
      hide_comment: 1
    }
    add_redirect_menu_item(a_menu, a_sub_menu, a_name, l_params, a_url);
  }

/******* booking state menu *********/

/**
 * Adds a change booking state menu item.
 * Since changing booking state changes server side state, it should be a POST
 * request which is solved with make_form_and_post call.
 **/
function add_change_booking_state_menu_item(a_menu, a_sub_menu, state_name, state_value, a_all, a_url) {

  a_sub_menu.addChild(new MenuItem({
    label: state_name,
    onClick: function(evt) {
      var node = a_menu.currentTarget;
      var bid = node.attributes["hollyrosa:bid"].value;

      var ioq = {
        booking_id: bid,
        state: state_value,
        all: a_all
      };
      make_form_and_post(a_url, ioq);

    }}));
  }


  /**
   * Adds a menu item to bookings in main booking view.
   * The last parameter is method and it should be 'GET' or 'POST'
   * depending on what fits best.
   **/
  function add_booking_op_menu_item(a_menu, a_sub_menu, a_name, a_url, method) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var bid = node.attributes["hollyrosa:bid"].value;
        var ioq = {
          booking_id: bid,
          return_to_day_id: node.attributes["hollyrosa:bdayid"].value
        };
        if (method == 'GET') {
          window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
        } else {
          make_form_and_post(a_url, ioq);
        }
      }
    }));
  }


  function add_user_management_op_menu_item(a_menu, a_sub_menu, a_name, a_url, method) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var user_id = node.attributes["hollyrosa:userid"].value;
        var ioq = {
          user_id: user_id
        };
        if (method == 'GET') {
          window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
        } else {
          make_form_and_post(a_url, ioq);
        }
      }
    }));
  }


  function add_change_user_level_menu_item(a_menu, a_sub_menu, a_state_name, level_value, a_all, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_state_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var user_id = node.attributes["hollyrosa:userid"].value;

        var ioq = {
          user_id: user_id,
          level: level_value
        };
        make_form_and_post(a_url, ioq)
      }
    }));
  }


  /**
   * A call function menu item is a menu item which takes a functions as a parameter (the last one)
   * and calls that fucntion with the event that is associated with the selection of the menu item.
   * This basically allows the function (callback) to pick info from the target node attributes.
   */
  function add_call_function_menu_item(a_menu, a_sub_menu, a_name, a_func) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;

        a_func(node);
      }
    }));
  }


  /**
   * This is a helper function that wraps  add_call_function_menu_item() and picks out the node
   * that the event that is associated with the menu click. BAsically, the node on which the menu was shown.
   * Then, for each oaram name in param_list, the hollyrosa:<param_name> attribute is obtained from
   * the node and set as parameter in a POST request.
   **/
  function add_transfer_map_function_menu_item(a_menu, a_sub_menu, a_name, a_url, param_list) {
    return add_call_function_menu_item(a_menu, a_sub_menu, a_name, function(evt) {
      var node = a_menu.currentTarget;
      var ioq = {};
      array.forEach(param_list, function(param_name) {
        ioq[param_name] = node.attributes["hollyrosa:"+param_name].value;
      });

      make_form_and_post(a_url, ioq)
    });
  }


  /**
   * This is a helper function that wraps  add_call_function_menu_item() and picks out the node
   * that the event that is associated with the menu click. BAsically, the node on which the menu was shown.
   * Then, for each oaram name in param_list, the hollyrosa:<param_name> attribute is obtained from
   * the node and set as parameter in a request with METHOD POST or GET depending on a_method string.
   *
   * Also, a_init_params is a dict with pre-filled params.
   **/
  function add_transfer_map_function_menu_item_2(a_menu, a_sub_menu, a_name, a_url, a_param_list, a_init_params, a_method) {
    return add_call_function_menu_item(a_menu, a_sub_menu, a_name, function(evt) {
      var node = a_menu.currentTarget;
      var ioq = a_init_params;
      array.forEach(a_param_list, function(param_name) {
        ioq[param_name] = node.attributes["hollyrosa:"+param_name].value;
      });
      if (a_method == 'GET') {
        window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
      } else {
        make_form_and_post(a_url, ioq)
      }
    });
  }


  function add_booking_op_menu_item_for_block(a_menu, a_sub_menu, a_name, a_url, a_subtype) {
    var menu_item =new MenuItem({
      label: a_name,
      onOpen: function(evt) {  },
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var sid = node.attributes["hollyrosa:sid"].value;
        var ioq = {
          slot_id: sid,
          subtype:a_subtype,
          booking_day_id: node.attributes["hollyrosa:bdayid"].value
        };
        make_form_and_post(a_url, ioq)
      }
    });

    a_sub_menu.addChild(menu_item);
    return menu_item;
  }

  /* TODO: The following fucntions can be made similar, becuae its only the dict that differs and the params read from the element */
  function add_visiting_group_menu_item(a_menu, a_sub_menu, a_name, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var vgid = node.attributes["hollyrosa:vgid"].value;
        var ioq = {
          visiting_group_id: vgid
        };
        window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
      }
    }));
  }

  function add_visiting_group_add_note_menu_item(a_menu, a_sub_menu, a_name, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var vgid = node.attributes["hollyrosa:vgid"].value;
        var ioq = {
          target_id: vgid
        };
        window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
      }
    }));
  }


  function add_visiting_group_edit_note_menu_item(a_menu, a_sub_menu, a_name, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var vgid = node.attributes["hollyrosa:vgid"].value;
        var nid = node.attributes["hollyrosa:nid"].value;
        var ioq = {
          visiting_group_id: vgid,
          note_id: nid
        };
        window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
      }
    }));
  }


  function add_visiting_group_list_bookings_menu_item(a_menu, a_sub_menu, a_name, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var vgname = node.attributes["hollyrosa:vgname"].value;
        var ioq = {
          name: vgname
        };

        window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
      }
    }));
  }



  /**
   * Loads actitivty group checkbox status from the cookie visible_ag
   *
   * TODO: dont use cookies, use some local store instead (dojo has no full support for this yet),
   * but perhaps we can use cookies for old brosers and dstore for modern browsers ???
   **/
  function load_ag_checkbox_status(){
    var cdata = cookie('visible_ag');
    var jdata;

    if (cdata == undefined) {
      jdata = {};
    } else {
      try {
        jdata = json.parse(cdata);
      }
      catch(SyntaxError) {
        jdata = {};
      }
    }
    return jdata;
  }


  /**
   * Saves checkbox status for activity groups.
   * TODO: dont use cookie ...
   **/
  function save_ag_checkbox_status(a_checkbox_status) {
    cookie('visible_ag', json.stringify(a_checkbox_status), {expires:5});
  }


  /**
   * Iterates through all rows and check if the should be shown or not.
   **/
  function update_activity_group_visible_rows(a_ag_status) {

    //...we now have a list of agc ids to show, all other should be hidden
    var elems = query("[hollyrosa:acgid]");
    array.forEach(elems, function(elem) {
      var agc_val = domAttr.get(elem, 'hollyrosa:acgid');
      if (a_ag_status[agc_val]) {
        domStyle.set(elem, 'display', 'block');
      } else if (null == a_ag_status[agc_val]) {
        domStyle.set(elem, 'display', 'block');
      } else {
        domStyle.set(elem, 'display', 'none');
      }
    });
  }

  /**
   * TODO: who uses this fn ?
   **/
  function update_visiting_group_type_visible_rows(a_vgt_status) {
    //...we now have a list of agc ids to show, all other should be hidden
    var elems = query("[hollyrosa:vgtid]");
    array.forEach(elems, function(elem) {
      var vgt_val = domAttr.get(elem, 'hollyrosa:vgtid');
      if (a_vgt_status[vgt_val]) {
        domStyle.set(elem, 'display', 'table-row');
      } else if (null == a_vgt_status[vgt_val]) {
        domStyle.set(elem, 'display', 'table-row');
      } else {
        domStyle.set(elem, 'display', 'none');
      }
    });
  }

  /**
   * Adds a checkbox menu item, used so we can select activity rows from a menu.
   *
   **/
  function add_ag_checkbox_menu_item(a_menu, a_name, a_id, a_ag_status, update_func) {
    var l_is_checked = true;
    if (a_id in a_ag_status) {
      l_is_checked = a_ag_status[a_id];
    }
    a_menu.addChild(new CheckedMenuItem({
      label: a_name,
      checked:  l_is_checked,
      onChange: function(selected) {
        //...create new ag_status. well, map ag id to true/false

        a_ag_status[a_id] = selected;
        save_ag_checkbox_status(a_ag_status);
        update_func(a_ag_status);
      }
    }));
  }


  /**
   * Load left click menu, what is the difference from load activity groups cookie?
   * TODO: switch from cookies to some dstore
   **/
  function load_left_click_menu(){
    var cdata = cookie('left_click_menu');
    var jdata;

    if (cdata == undefined) {
      jdata = false;
    } else {
      try {
        jdata = json.parse(cdata);
      }
      catch(SyntaxError) {
        console.log('SyntaxError when parsing JSON data for cookie left click menu');
        jdata = false;
      }
    }
    return jdata;
  }

  /**
   * TODO: move constants and config data to separate module
   **/
  var state_change_list = [
    {name:"> Disapprove", state:-10},
    {name:"> Preliminary", state:0},
    {name:"> Stand-by", state:5},
    {name:"> Booked", state:10},
    {name:"> Approve", state:20},
    {name:"> Drop-in", state:30} //,
    //        	{name:"Delete booking", state:-100}
  ];

  /*** program status code ****/

  var program_state_change_list = [
    {name:"> Canceled", state:-10},
    {name:"> New", state:0},
    {name:"> Created", state:5},
    {name:"> Preliminary", state:10},
    {name:"> Confirmed", state:20},
    {name:"> Island", state:50} //,
    //        	{name:"Delete booking", state:-100}
  ];

  var user_level_change_list = [
    {name:"> None", level:""},
    {name:"> Viewer", level:"viewer"},
    {name:"> Staff", level:"staff"},
    {name:"> PL", level:"pl"}
  ];

  //...TODO: better load via ajax
  program_state_map = [["0","new"],["5","created"],["10","preliminary"],["50","island"],["20","confirmed"],["-10","canceled"],["-100","deleted"]];
  vodb_state_map = [["0","new"],["5","created"],["10","preliminary"],["50","island"],["20","confirmed"],["-10","canceled"],["-100","deleted"]];


  function add_change_program_state_menu_item(a_menu, a_sub_menu, a_state_name, state_value, a_all, a_url) {
    a_sub_menu.addChild(new MenuItem({
      label: a_state_name,
      onClick: function(evt) {
        var node = a_menu.currentTarget;
        var vgid = node.attributes["hollyrosa:vgid"].value;

        var ioq = {
          visiting_group_id: vgid,
          state: state_value
        };
        make_form_and_post(a_url, ioq)
      }
    }));
  }


  return {
    add_redirect_menu_item:add_redirect_menu_item,
    add_call_function_menu_item:add_call_function_menu_item,
    add_vgid_redirect_menu_item:add_vgid_redirect_menu_item,
    add_note_redirect_menu_item:add_note_redirect_menu_item,
    add_list_bookings_redirect_menu_item:add_list_bookings_redirect_menu_item,
    add_change_booking_state_menu_item:add_change_booking_state_menu_item, state_change_list:state_change_list,
    add_booking_op_menu_item:add_booking_op_menu_item, add_visiting_group_menu_item:add_visiting_group_menu_item,
    add_user_management_op_menu_item:add_user_management_op_menu_item, add_change_user_level_menu_item:add_change_user_level_menu_item,
    add_visiting_group_add_note_menu_item:add_visiting_group_add_note_menu_item,
    add_visiting_group_list_bookings_menu_item:add_visiting_group_list_bookings_menu_item,
    add_booking_op_menu_item_for_block:add_booking_op_menu_item_for_block,
    add_menu_separator:add_menu_separator,
    add_visiting_group_edit_note_menu_item:add_visiting_group_edit_note_menu_item,
    add_ag_checkbox_menu_item:add_ag_checkbox_menu_item,
    load_ag_checkbox_status:load_ag_checkbox_status,
    update_activity_group_visible_rows:update_activity_group_visible_rows,
    load_left_click_menu:load_left_click_menu,
    add_change_program_state_menu_item:add_change_program_state_menu_item,
    program_state_change_list:program_state_change_list,
    vodb_state_change_list:program_state_change_list, user_level_change_list:user_level_change_list,
    add_calc_sheet_redirect_menu_item:add_calc_sheet_redirect_menu_item,
    program_state_map:program_state_map, vodb_state_map:vodb_state_map,
    update_visiting_group_type_visible_rows:update_visiting_group_type_visible_rows,
    add_transfer_map_function_menu_item:add_transfer_map_function_menu_item,
    add_transfer_map_function_menu_item_2:add_transfer_map_function_menu_item_2
  };
});
