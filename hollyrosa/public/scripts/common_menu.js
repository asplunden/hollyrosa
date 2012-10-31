/*
 * Copyright 2012, 2011, 2012 Martin Eliasson
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
 
 define(["dijit/Menu","dijit/MenuItem","dojo/query!css2", "dojo/io-query"], function(Menu, MenuItem, query, ioQuery) {
		
		//var node = a_menu.currentTarget;
      //var vgid = node.attributes["hollyrosa:bid"].value;
            
	function add_redirect_menu_item(a_menu, a_sub_menu, a_name, a_params, a_url) {
      a_sub_menu.addChild(new MenuItem({
      	label: a_name,
         onClick: function(evt) {   
               window.location = a_url + '?' + ioQuery.objectToQuery(a_params);
           }}));
   }
   
   
	function add_vgid_redirect_menu_item(a_menu, a_sub_menu, a_name, a_vgid, a_url) {
		var l_params = {
      	visiting_group_id: a_vgid
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
	
	
	function add_booking_op_menu_item_for_block(a_menu, a_sub_menu, a_name, a_url) {
   	var menu_item =new MenuItem({
               label: a_name,
               onOpen: function(evt) { console.log(evt); },
               onClick: function(evt) {
                   var node = a_menu.currentTarget;
                   var sid = node.attributes["hollyrosa:sid"].value;
                   var ioq = {
                       slot_id: sid,
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
	
	
	

       
       
       

   
   var state_change_list = [
         {name:"> Disapprove", state:-10}, 
    		{name:"> Preliminary", state:0},
        	{name:"> Stand-by", state:5},
        	{name:"> Booked", state:10}, 
        	{name:"> Approve", state:20}, 
        	{name:"> Drop-in", state:30}, 
        	{name:"Delete booking", state:-100}
    ];
	
	return {
		add_redirect_menu_item:add_redirect_menu_item, 
	   add_vgid_redirect_menu_item:add_vgid_redirect_menu_item, 
	   add_note_redirect_menu_item:add_note_redirect_menu_item, 
	   add_list_bookings_redirect_menu_item:add_list_bookings_redirect_menu_item, 
	add_change_booking_state_menu_item:add_change_booking_state_menu_item, state_change_list:state_change_list, add_booking_op_menu_item:add_booking_op_menu_item, add_visiting_group_menu_item:add_visiting_group_menu_item,
	add_visiting_group_add_note_menu_item:add_visiting_group_add_note_menu_item, 
	add_visiting_group_list_bookings_menu_item:add_visiting_group_list_bookings_menu_item,
	add_booking_op_menu_item_for_block:add_booking_op_menu_item_for_block };
	});
	