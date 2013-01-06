/**
 * Copyright Notice
 **/


require(['dojo/_base/lang', 'dojox/grid/DataGrid', 'dojo/data/ItemFileWriteStore', 'dojox/grid/cells/dijit', 'dojo/date/stamp', 'dojo/date/locale', 'dojo/domReady!'],
  function(lang, DataGrid, ItemFileWriteStore, cells, stamp, locale, ready){
    
      function formatDate(datum){
        /*Format the value in store, so as to be displayed.*/
        
        
        var d = stamp.fromISOString(datum);
        return locale.format(d, {selector: 'date', formatLength: 'short'});
      }

    function getDateValue(){
        /*Override the default getValue function for dojox.grid.cells.DateTextBox   */
        return stamp.toISOString(this.widget.get('value'));
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
    var store = new ItemFileWriteStore({data: data});

    /*set up layout*/
    var layout = [[
      {'name': 'Date', 'field': 'col_date', 'width': '50px', editable: true, type: dojox.grid.cells.DateTextBox, formatter: formatDate, getValue: getDateValue},
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

    /*append the new grid to the div*/
    grid2.placeAt("program_request_div");

    /*Call startup() to render the grid*/
    grid2.startup();
});