{
   "_id": "_design/statistics",
   "_rev": "15-b5584666c6d5b170ac46ed91062ae57a",
   "language": "javascript",
   "views": {
       "age_group_statistics": {
           "map": "function(doc) {\n    if (doc.type=='visiting_group') {\n    \n        /* properties have different time spans, so we neew to iterate through tham */\n        for (vg_property_row_key in doc.visiting_group_properties) {\n            tmp_row = doc.visiting_group_properties[vg_property_row_key];  \n            tmp_from_date = new Date(tmp_row['from_date']);\n            tmp_end_date = new Date(tmp_row['to_date']);\n            var one_day = 1000*60*60*24;\n        \n            for (tmp_day = tmp_from_date; tmp_day <= tmp_end_date; tmp_day = new Date(tmp_day.getTime() + one_day)) {\n                emit([[tmp_day.getYear()+1900,tmp_day.getMonth()+1,tmp_day.getDate()], tmp_row['property']], tmp_row['value']);\n            \n            }\n        }\n    }\n}",
           "reduce": "function(key, values, rereduce) {\n    /* how will sum handle non-integer values?*/\n    var summ = 0;\n    for (var i=0; i<values.length; i=i+1) {    \n        if (! isNaN (values[i]-0)) {\n            summ = summ + new Number(values[i]);\n        }\n    }   \n    return summ;\n}"
       }
   }
}