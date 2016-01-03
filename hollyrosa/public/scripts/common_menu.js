/*
 * Copyright 2011, 2012, 2013, 2014, 2015, 2016 Martin Eliasson
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
		
    function add_menu_separator(menu) {
    	menu.addChild(new MenuSeparator());
    }
    
    
	function add_redirect_menu_item(a_menu, a_sub_menu, a_name, a_params, a_url) {
      a_sub_menu.addChild(new MenuItem({
      	label: a_name,
         onClick: function(evt) {
                if ('' != a_params) {
                    window.location = a_url + '?' + ioQuery.objectToQuery(a_params); 
                    } else {
                    window.location = a_url; 
                    }
           }}));
   }
   
   
	function add_vgid_redirect_menu_item(a_menu, a_sub_menu, a_name, a_vgid, a_url) {
		var l_params = {
      	visiting_group_id: a_vgid
         }
      add_redirect_menu_item(a_menu, a_sub_menu, a_name, l_params, a_url); 
	}
    
    function add_calc_sheet_redirect_menu_item(a_menu, a_sub_menu, a_name, a_vgid, a_live, change_schema, a_url) {
		var l_params = {
      	visiting_group_id: a_vgid,
        live: a_live,
        change_schema: change_schema
         }
      add_redirect_menu_item(a_menu, a_sub_menu, a_name, l_params, a_url); 
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
               window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
           }}));
   }    
   
   
	function add_booking_op_menu_item(a_menu, a_sub_menu, a_name, a_url) {
        a_sub_menu.addChild(new MenuItem({
               label: a_name,
               onClick: function(evt) {
                   var node = a_menu.currentTarget;
                   var bid = node.attributes["hollyrosa:bid"].value;
                   var ioq = {
                       booking_id: bid,
                       return_to_day_id: node.attributes["hollyrosa:bdayid"].value
                   };
               window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
               }
           })); 
	}
	
	
	function add_user_management_op_menu_item(a_menu, a_sub_menu, a_name, a_url) {
        a_sub_menu.addChild(new MenuItem({
               label: a_name,
               onClick: function(evt) {
                   var node = a_menu.currentTarget;
                   var user_id = node.attributes["hollyrosa:userid"].value;
                   var ioq = {
                       user_id: user_id
                   };
               window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
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
               window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
           }}));
   }    	
    
    
    function add_call_function_menu_item(a_menu, a_sub_menu, a_name, a_func) {
        a_sub_menu.addChild(new MenuItem({
            label: a_name,
            onClick: function(evt) {
                var node = a_menu.currentTarget;
                
                a_func(node);
                }
           }));
    }
    
	
	function add_booking_op_menu_item_for_block(a_menu, a_sub_menu, a_name, a_url, a_subtype) {
   	var menu_item =new MenuItem({
               label: a_name,
               onOpen: function(evt) { console.log(evt); },
               onClick: function(evt) {
                   var node = a_menu.currentTarget;
                   var sid = node.attributes["hollyrosa:sid"].value;
                   var ioq = {
                       slot_id: sid,
                       subtype:a_subtype,
                       booking_day_id: node.attributes["hollyrosa:bdayid"].value
                   };
               console.log(a_url + '?' + ioQuery.objectToQuery(ioq));
               window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
               }
           });
           
        a_sub_menu.addChild(menu_item);
    	return menu_item; 
	}

/* The following fucntions can be made similar, becuae its only the dict that differs and the params read from the element */
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
   		
   		
	function save_ag_checkbox_status(a_checkbox_status) {
		cookie('visible_ag', json.stringify(a_checkbox_status), {expires:5});		
	}
		

	function update_activity_group_visible_rows(a_ag_status) {    
       //...we now have a list of agc ids to show, all other should be hidden
       var elems = query("[hollyrosa:acgid]");
       array.forEach(elems, function(elem) {
           var agc_val = domAttr.get(elem, 'hollyrosa:acgid');
           if (a_ag_status[agc_val]) {
               dojo.style(elem, {display: 'block'});
           } else if (null == a_ag_status[agc_val]) {
               dojo.style(elem, {display: 'block'});
            } else {
                dojo.style(elem, {display: 'none'});
            }
        });
    }
    
    function update_visiting_group_type_visible_rows(a_vgt_status) {    
        //...we now have a list of agc ids to show, all other should be hidden
        var elems = query("[hollyrosa:vgtid]");
        array.forEach(elems, function(elem) {
            var vgt_val = domAttr.get(elem, 'hollyrosa:vgtid');
            if (a_vgt_status[vgt_val]) {
                dojo.style(elem, {display: 'table-row'});
            } else if (null == a_vgt_status[vgt_val]) {
                dojo.style(elem, {display: 'table-row'});
            } else {
                dojo.style(elem, {display: 'none'});
            }
        });
     }
	
	
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
            	//update_activity_group_visible_rows(a_ag_status);
					update_func(a_ag_status);             
               }}
           ))} 
	
       
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
				jdata = false;      
      		}
			}
			return jdata; 
   	}	 

   
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
               window.location = a_url + '?' + ioQuery.objectToQuery(ioq);
           }}));
   }
	
    //...better load via ajax
    program_state_map = [["0","new"],["5","created"],["10","preliminary"],["50","island"],["20","confirmed"],["-10","canceled"],["-100","deleted"]];
    vodb_state_map = [["0","new"],["5","created"],["10","preliminary"],["50","island"],["20","confirmed"],["-10","canceled"],["-100","deleted"]];
    
	
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
        update_visiting_group_type_visible_rows:update_visiting_group_type_visible_rows
		  };
	});
	
