/**
 * Copyright 2010, 2011, 2012 Martin Eliasson
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

/* for booking_day.html */
function set_visible_ag_rows(acg_id, v) {
    var elems = dojo.query("[hollyrosa:acgid]");
    dojo.forEach(elems, function(elem) {
        var agc_val = dojo.attr(elem, 'hollyrosa:acgid');
        if (agc_val == acg_id) {
            dojo.style(elem, {display: v});
            }
    } );
 }


function set_form_field_value(form_field_id, value){
    var form_field = dojo.byId(form_field_id);
    form_field.value = value;
}



function navigation_calendar_is_disabled(x) {
    var test_date = dojo.date.locale.format(x, {datePattern: "yyyy-MM-dd", selector: "date"});
    return test_date < "2011-06-11" || test_date > "2011-08-14"; 
}


function set_visiting_group_form_values(visiting_group) {
    dojo.byId("visiting_group_data_name").innerHTML = visiting_group['name'];
    dojo.byId("visiting_group_data_info").innerHTML = '<p><i>'+visiting_group['tags']+'</p></i>'+'<b>bokn.nr: </b>' + visiting_group['boknr'] + '<br/><b>bokn.status: </b>' + visiting_group['boknstatus'] +'<br/><b>location: </b>' + visiting_group['camping_location'] + '<br/>' + visiting_group['info'];
    dojo.byId("visiting_group_data_fromdate").innerHTML = visiting_group['from_date'];
    dojo.byId("visiting_group_data_todate").innerHTML = visiting_group['to_date'];
    dojo.byId("visiting_group_data_contact").innerHTML = visiting_group['contact_person'];
    dojo.byId("visiting_group_data_phone").innerHTML = visiting_group['contact_person_phone'];
    dojo.byId("visiting_group_data_email").innerHTML = visiting_group['contact_person_email'];
}



function create_visiting_group_properties_table_headings(table) {
    tr = dojo.create("tr", null, table);
    th = dojo.create("th", { innerHTML: "property" }, table);
    th = dojo.create("th", { innerHTML: "value" }, table);
    th = dojo.create("th", { innerHTML: "unit" }, table);
    th = dojo.create("th", { innerHTML: "description" }, table);
    th = dojo.create("th", { innerHTML: "from date" }, table);
    th = dojo.create("th", { innerHTML: "to date" }, table);
 }
 
 
 function transfer_date(to_ement, date) {
    e.value = date;
}




function transfer_to_booking_request_fromdate() {
    var e = dojo.byId('visiting_group_data_fromdate');
    var value = e.innerHTML;
    transfer_from_date(value);
}


function transfer_to_booking_request_todate() {
    var e = dojo.byId('visiting_group_data_todate');
    var value = e.innerHTML;
    transfer_to_date(value);
}


/* from multi book and used by sanity check among others*/

/* from edit booked booking  */

 function on_update_visiting_group_data(data) {
    var visiting_group = data['visiting_group'];
    
    set_visiting_group_form_values(visiting_group);

    var elemCont = dojo.byId("visiting_group_data");
    var table = dojo.byId("visiting_group_properties_table");
    var properties = data['properties']
    
    //...clean property table
    dojo.forEach(dojo.query("#visiting_group_properties_table >"), function(g){
    dojo.destroy(g);
    });

    //...create heading
    create_visiting_group_properties_table_headings(table);
    
    dojo.forEach(properties, function(g){
        tr = dojo.create("tr", null, table);
        td = dojo.create("td", {}, table);
        ahref = dojo.create("a", {href:'javascript:transfer_to_content("\$\$' + g['property'] +'");', innerHTML: '\$'+g['property']}, td);
        td = dojo.create("td", { innerHTML: g['value'] }, table);
        td = dojo.create("td", { innerHTML: g['unit'] }, table);
        td = dojo.create("td", { innerHTML: g['description'] }, table);
        td = dojo.create("td", { innerHTML: g['from_date'] }, table);
        td = dojo.create("td", { innerHTML: g['to_date'] }, table);
    });
}



/*
function on_update_visiting_group_data(data) {
    var visiting_group = data['visiting_group'];
    set_visiting_group_form_values(visiting_group);
    
    var elemCont = dojo.byId("visiting_group_data");
    var table = dojo.byId("visiting_group_properties_table");
    var properties = data['properties']
    
    //...clean property table
    dojo.forEach(dojo.query('visiting_group_properties_table >'), function(g){
    dojo.destroy(g);
    });

    //...create heading
    create_visiting_group_properties_table_headings(table);
    
    //...add data rows
    dojo.forEach(properties, function(g){
        tr = dojo.create("tr", null, table);
        td = dojo.create("td", {}, table);
        ahref = dojo.create("a", {href:'javascript:transfer_to_content("\$\$' + g['property'] +'");', innerHTML: '\$'+g['property']}, td);
        
        td = dojo.create("td", { innerHTML: g['value'] }, table);
        td = dojo.create("td", { innerHTML: g['unit'] }, table);
        td = dojo.create("td", { innerHTML: g['description'] }, table);
        
        td = dojo.create("td", {}, table);
        ahref = dojo.create("a", {href:'javascript:transfer_from_date("' + g['fromdate'] +'");', innerHTML: g['fromdate']}, td);
       
        td = dojo.create("td", {}, table);
        ahref = dojo.create("a", {href:'javascript:transfer_to_date("' + g['todate'] +'");', innerHTML: g['todate']}, td);
    });
}
*/
