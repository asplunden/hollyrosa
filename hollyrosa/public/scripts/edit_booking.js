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

 
define(["dojo/_base/array", "dojo/query", "dojo/dom", "dojo/dom-construct", "dojo/request/xhr", "dojo/ready"], function(array, query, dom, domConstruct, xhr, ready) {


function set_form_field_value(form_field_id, value){
    var form_field = dom.byId(form_field_id);
    form_field.value = value;
}


function set_visiting_group_form_values(visiting_group) {
    dom.byId("visiting_group_data_name").innerHTML = visiting_group['name'];
    dom.byId("visiting_group_data_info").innerHTML = '<p><i>'+visiting_group['tags']+'</p></i>'+'<b>bokn.nr: </b>' + visiting_group['boknr'] + '<br/><b>bokn.status: </b>' + visiting_group['boknstatus'] +'<br/><b>location: </b>' + visiting_group['camping_location'] + '<br/>' + visiting_group['info'];
    dom.byId("visiting_group_data_fromdate").innerHTML = visiting_group['from_date'];
    dom.byId("visiting_group_data_todate").innerHTML = visiting_group['to_date'];
    dom.byId("visiting_group_data_contact").innerHTML = visiting_group['contact_person'];
    dom.byId("visiting_group_data_phone").innerHTML = visiting_group['contact_person_phone'];
    dom.byId("visiting_group_data_email").innerHTML = visiting_group['contact_person_email'];
}


function create_visiting_group_properties_table_headings(table) {
    tr = domConstruct.create("tr", null, table);
    th = domConstruct.create("th", { innerHTML: "property" }, table);
    th = domConstruct.create("th", { innerHTML: "value" }, table);
    th = domConstruct.create("th", { innerHTML: "unit" }, table);
    th = domConstruct.create("th", { innerHTML: "description" }, table);
    th = domConstruct.create("th", { innerHTML: "from date" }, table);
    th = domConstruct.create("th", { innerHTML: "to date" }, table);
 }


function update_visiting_group_data(data) {
    var visiting_group = data['visiting_group'];
    
    set_visiting_group_form_values(visiting_group);

    var elemCont = dom.byId("visiting_group_data");
    var table = dom.byId("visiting_group_properties_table");
    var properties = data['properties'] 
	 
    //...clean property table
    var elems_to_destroy = query('#visiting_group_properties_table >');
    array.forEach(elems_to_destroy, function(g){
    	domConstruct.destroy(g);
    });

    //...create heading
    create_visiting_group_properties_table_headings(table);
    
    array.forEach(properties, function(g){
        tr = domConstruct.create("tr", null, table);
        td = domConstruct.create("td", {}, table);
        ahref = domConstruct.create("a", {href:'javascript:transfer_to_content("\$\$' + g['property'] +'");', innerHTML: '\$'+g['property']}, td);
        td = domConstruct.create("td", { innerHTML: g['value'] }, table);
        td = domConstruct.create("td", { innerHTML: g['unit'] }, table);
        td = domConstruct.create("td", { innerHTML: g['description'] }, table);
        td = domConstruct.create("td", { innerHTML: g['from_date'] }, table);
        td = domConstruct.create("td", { innerHTML: g['to_date'] }, table);
    });
}



return {set_form_field_value:set_form_field_value, update_visiting_group_data:update_visiting_group_data};


});