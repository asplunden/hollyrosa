{
   "_id": "_design/tag_statistics",
   "_rev": "3-bd93d42fb6fa0eb29600d55dbd0c153b",
   "language": "javascript",
   "views": {
       "tag_group_statistics": {
           "map": "function(doc) {if (doc.type=='visiting_group') {for (vg_tag_key in doc.tags) {vg_tag = doc.tags[vg_tag_key];for (vg_property_row_key in doc.visiting_group_properties){tmp_row = doc.visiting_group_properties[vg_property_row_key];tmp_from_date = new Date(tmp_row['from_date']);tmp_end_date = new Date(tmp_row['to_date']);var one_day = 1000*60*60*24;for (tmp_day = tmp_from_date; tmp_day <= tmp_end_date; tmp_day = new Date(tmp_day.getTime() + one_day)) {emit([[tmp_day.getYear()+1900,tmp_day.getMonth()+1,tmp_day.getDate()], vg_tag, tmp_row['property']], tmp_row['value']);}}}}}",
           "reduce": "function(key, values, rereduce) {\n    /* how will sum handle non-integer values?*/\n    var summ = 0;\n    for (var i=0; i<values.length; i=i+1) {    \n        if (! isNaN (values[i]-0)) {\n            summ = summ + new Number(values[i]);\n        }\n    }   \n    return summ;\n}"
       }
   }
}