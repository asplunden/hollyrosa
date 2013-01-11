/*
 * Copyright 2013 Martin Eliasson
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


require(['dojo/_base/lang', 'dojox/grid/DataGrid', 'dojo/data/ItemFileWriteStore', 'dojox/grid/cells/dijit', 'dojo/date/stamp', 'dojo/date/locale', 'dojo/dom','dojo/on','dojo/domReady!'],
  function(lang, DataGrid, ItemFileWriteStore, cells, stamp, locale, dom, on, ready ){
    
    function formatDate(datum) {
        var d = stamp.fromISOString(datum);
        return locale.format(d, {selector: 'date', formatLength: 'short'});
    }

    function getDateValue(){
        /*Override the default getValue function for dojox.grid.cells.DateTextBox   */
        return stamp.toISOString(this.widget.get('value'));
    }
    
    
    function saveCompleteCallback(){
    	alert('save done');
    	}

	function saveFailedCallback() {
		alert('save failed');
		}
  
 
    var data = {
      identifier: "property",
      items: []
    };
    
    
    var data_list_2 = [
      { property: 'barn', unit:'smabarn',  age: '0-7',  age_group: 'Smabarn',      value: 0, from_date: '', to_date: ''},
      { property: 'spar', unit:'spar',     age: '8-9',  age_group: 'Sparare',      value: 0, from_date: '', to_date: ''},
      { property: 'uppt', unit:'uppt',     age: '10-11',  age_group: 'Upptackare', value: 0, from_date: '', to_date: ''},
      { property: 'aven', unit:'aven',     age: '12-15',  age_group: 'Aventyrare', value: 0, from_date: '', to_date: ''},
      { property: 'utm',  unit:'utm',      age: '16-18',  age_group: 'Utmanare',   value: 0, from_date: '', to_date: ''},
      { property: 'rover', unit:'rover',   age: '18-25',  age_group: 'Rover',      value: 0, from_date: '', to_date: ''},
      { property: 'led', unit:'ledare',    age: '---',  age_group: 'Ledare',       value: 0, from_date: '', to_date: ''}
    ];

    
    for(var i = 0, l = data_list_2.length; i < l; i++){
      data.items.push(lang.mixin({ id: i+1 }, data_list_2[i%l]));
    }
    
    
    var store = new ItemFileWriteStore({
    	data: data
      });

    store._saveEverything = function(a_saveCompleteCallback /*Your callback to call when save is completed */,
                                a_saveFailedCallback /*Your callback to call if save fails*/,
                                a_newFileContentString /*The generated JSON data to send somewhere*/){
                                	//alert(a_newFileContentString);
                                	var inp = dom.byId('age_group_div_input');
                                	inp.value = a_newFileContentString;
                                	a_saveCompleteCallback();
                                	}   
    
    var layout = [[
      {'name': 'Age',                    field: 'age', 'width': '100px'},
      {'name': 'Group',                  field: 'age_group', 'width': '100px'},
      {'name': 'Number of participants', field: 'value', 'width': '150px', editable: true},
      {'name': 'From date',              field: 'from_date', 'width': '100px', editable: true, type: dojox.grid.cells.DateTextBox, formatter: formatDate, getValue: getDateValue},
      {'name': 'To date',                field: 'to_date', 'width': '100px', editable: true, type: dojox.grid.cells.DateTextBox, formatter: formatDate, getValue: getDateValue}
    ]];

    /*create a new grid*/
    var grid = new DataGrid({
        id: 'age_group_gridx',
        store: store,
        structure: layout,
        rowSelector: '10px'});

    function on_save_grid_to_input() {
    	//...find dojo store and serialize it. Should be simple. Then write serialized data into 
    	//alert('storing...');
    	store.save(saveCompleteCallback, saveFailedCallback);
    	
    	//   somef input div. Wonder if the div widget can be accompanyed by an input widget?
    	};
    	
    grid.placeAt('age_group_div');
    grid.startup();
    
    //alert('ready in div_widget');
    //var age_group_div = dom.byId('save_age_group_grid');
    var submitt_button = dom.byId('create_edit_visiting_group_program_request_form_submit');
    //on(age_group_div, 'click', on_save_grid_to_input);
    on(submitt_button, 'click', on_save_grid_to_input);
      
});