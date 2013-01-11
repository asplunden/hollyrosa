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


require(['dojo/_base/lang', 'dojox/grid/DataGrid', 'dojo/data/ItemFileWriteStore', 'dojox/grid/cells/dijit', 'dojo/date/stamp', 'dojo/date/locale', 'dojo/dom','dojo/on', 'dojo/domReady!'],
  function(lang, DataGrid, ItemFileWriteStore, cells, stamp, locale, dom, on, ready){
    
      function formatDate(datum){
        /*Format the value in store, so as to be displayed.*/
        
        
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
  
  
    /*set up data store*/
    var data = {
      identifier: "id",
      items: []
    };
    
    
        

    var data_list_2 = [
      { col_date: '', col_time:'', col_ag: '', col_program: ''}
    ];


    
    for(var i = 0, l = data_list_2.length; i < 35; i++){
      data.items.push(lang.mixin({ id: i+1 }, data_list_2[i%l]));
    }
    var store = new ItemFileWriteStore({
    	data: data
      });
      
      
    store._saveEverything = function(a_saveCompleteCallback /*Your callback to call when save is completed */,
                                a_saveFailedCallback /*Your callback to call if save fails*/,
                                a_newFileContentString /*The generated JSON data to send somewhere*/){
                                	//alert(a_newFileContentString);
                                	var inp = dom.byId('program_request_div_input');
                                	inp.value = a_newFileContentString;
                                	a_saveCompleteCallback();
                                	}   

    /*set up layout*/
    var layout = [[
      {'name': 'Date', 'field': 'col_date', 'width': '100px', editable: true, type: dojox.grid.cells.DateTextBox, formatter: formatDate, getValue: getDateValue},
      {'name': 'Time', 'field': 'col_time', 'width': '50px', editable:true, type: dojox.grid.cells.Select, options: [ 'FM', 'EM', 'Evening' ], values: [ '0', '1', '2' ]},      
      {'name': 'Program', 'field': 'col_program', 'width': '100px', editable: true, type: dojox.grid.cells.Select, options: ['-', 'Trapper', 'Sammarbetsgläntan', 'Storbåt','Optimist','Kanot','Flottbygge','Hinderbana'], values: [ '0', '1', '2','3','4','5','6' ]},
      {'name': 'Småbarn', 'field': 'col_sma', 'width': '60px', editable:true, type: dojox.grid.cells.Bool},  
      {'name': 'Spårare', 'field': 'col_spar', 'width': '60px', editable:true, type: dojox.grid.cells.Bool},
      {'name': 'Upptäckare', 'field': 'col_uppt', 'width': '60px', editable:true, type: dojox.grid.cells.Bool},
      {'name': 'Äventyrare', 'field': 'col_aven', 'width': '60px', editable:true, type: dojox.grid.cells.Bool},
      {'name': 'Utmanare', 'field': 'col_utm', 'width': '60px', editable:true, type: dojox.grid.cells.Bool},  
      {'name': 'Rover', 'field': 'col_rov', 'width': '60px', editable:true, type: dojox.grid.cells.Bool},
      {'name': 'Note', 'field': 'col_note', 'width': '200px', editable:true}
    ]];

    /*create a new grid*/
    var grid2 = new DataGrid({
        id: 'visiting_group_program_request_gridx',
        store: store,
        structure: layout,
        rowSelector: '10px'});


    function on_save_grid_to_input() {
    	//...find dojo store and serialize it. Should be simple. Then write serialized data into 
    	//alert('storing 2...');
    	store.save(saveCompleteCallback, saveFailedCallback);
    	
    	//   somef input div. Wonder if the div widget can be accompanyed by an input widget?
    	};
    	
    grid2.placeAt("program_request_div");
    grid2.startup();
    
    //alert('ready in div_widget  2');
    var submitt_button = dom.byId('create_edit_visiting_group_program_request_form_submit');
    on(submitt_button, 'click', on_save_grid_to_input);
});