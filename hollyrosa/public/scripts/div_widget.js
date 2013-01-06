/**
 * Copyright Notice
 **/


require(['dojo/_base/lang', 'dojox/grid/DataGrid', 'dojo/data/ItemFileWriteStore', 'dojox/grid/cells/dijit', 'dojo/date/stamp', 'dojo/date/locale', 'dojo/domReady!'],
  function(lang, DataGrid, ItemFileWriteStore, cells, stamp, locale, ready ){
    
    function formatDate(datum) {
        var d = stamp.fromISOString(datum);
        return locale.format(d, {selector: 'date', formatLength: 'short'});
    }

    function getDateValue(){
        /*Override the default getValue function for dojox.grid.cells.DateTextBox   */
        return stamp.toISOString(this.widget.get('value'));
    }
    
  
 
    var data = {
      identifier: "id",
      items: []
    };
    
    
    var data_list_2 = [
      { col_age: '0-7', col_group: 'Smabarn',       col_: 0, col3: '', col4: ''},
      { col_age: '8-9',  col_group: 'Sparare',      col2: 0, col3: '', col4: ''},
      { col_age: '10-11',  col_group: 'Upptackare', col2: 0, col3: '', col4: ''},
      { col_age: '12-15',  col_group: 'Aventyrare', col2: 0, col3: '', col4: ''},
      { col_age: '16-18',  col_group: 'Utmanare',   col2: 0, col3: '', col4: ''},
      { col_age: '18-25',  col_group: 'Rover',      col2: 0, col3: '', col4: ''},
      { col_age: '---',  col_group: 'Ledare',       col2: 0, col3: '', col4: ''}
    ];

    
    for(var i = 0, l = data_list_2.length; i < l; i++){
      data.items.push(lang.mixin({ id: i+1 }, data_list_2[i%l]));
    }
    
    
    var store = new ItemFileWriteStore({data: data});

    
    var layout = [[
      {'name': 'Age',                    field: 'col_age', 'width': '100px'},
      {'name': 'Group',                  field: 'col_group', 'width': '100px'},
      {'name': 'Number of participants', field: 'col2', 'width': '150px', editable: true},
      {'name': 'From date',              field: 'col3', 'width': '100px', editable: true, type: dojox.grid.cells.DateTextBox, formatter: formatDate, getValue: getDateValue},
      {'name': 'To date',                field: 'col4', 'width': '100px', editable: true, type: dojox.grid.cells.DateTextBox, formatter: formatDate, getValue: getDateValue}
    ]];

    /*create a new grid*/
    var grid = new DataGrid({
        id: 'age_group_gridx',
        store: store,
        structure: layout,
        rowSelector: '10px'});

    
    	grid.placeAt('age_group_div');
      grid.startup();
    
      
});