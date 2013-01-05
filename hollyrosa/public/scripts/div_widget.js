/**
 * Copyright Notice
 **/


require(['dojo/_base/lang', 'dojox/grid/DataGrid' , 'dojo/data/ItemFileWriteStore' , 'dojo/dom' , 'dojo/domReady!'],
  function(lang, DataGrid, ItemFileWriteStore, Button, dom){
    /*set up data store*/
    var data = {
      identifier: "id",
      items: []
    };
    
    
    var data_list = [
      { col1: "normal", col2: false, col3: 'But are not followed by two hexadecimal', col4: 29.91},
      { col1: "important", col2: false, col3: 'Because a % sign always indicates', col4: 9.33},
      { col1: "important", col2: false, col3: 'Signs can be selectively', col4: 19.34}
    ];
    

    var data_list_2 = [
      { ag: 'Småbarn (0-7)', col1: "normal", col2: 0, col3: '', col4: ''},
      { ag: 'Spårare (8-9)', col1: "important", col2: 0, col3: '', col4: ''},
      { ag: 'Upptäckare (10-11)', col1: "important", col2: 0, col3: '', col4: ''},
      { ag: 'Äventyrare (12-15)', col1: "important", col2: 0, col3: '', col4: ''},
      { ag: 'Utmanare (16-18)', col1: "important", col2: 0, col3: '', col4: ''},
      { ag: 'Rover (18-25)', col1: "important", col2: 0, col3: '', col4: ''},
      { ag: 'Ledare', col1: "important", col2: 0, col3: '', col4: ''}
    ];


   /*
    var rows = 60;
    for(var i = 0, l = data_list.length; i < rows; i++){
      data.items.push(lang.mixin({ id: i+1 }, data_list[i%l]));
    }*/
    
    for(var i = 0, l = data_list_2.length; i < l; i++){
      data.items.push(lang.mixin({ id: i+1 }, data_list_2[i%l]));
    }
    var store = new ItemFileWriteStore({data: data});

    /*set up layout*/
    var layout = [[
      {'name': 'Age group', 'field': 'ag', 'width': '200px'},
      {'name': 'Number of participants', 'field': 'col2', 'width': '150px', editable: true},
      {'name': 'From date', 'field': 'col3', 'width': '100px', editable: true},
      {'name': 'To date', 'field': 'col4', 'width': '100px', editable: true, type: dojox.grid.cells.DateTextBox}
    ]];

    /*create a new grid*/
    var grid = new DataGrid({
        id: 'grid',
        store: store,
        structure: layout,
        rowSelector: '20px'});

    /*append the new grid to the div*/
    grid.placeAt("age_group_div");

    /*Call startup() to render the grid*/
    grid.startup();
});