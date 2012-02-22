{
   "_id": "_design/visiting_groups",
   "_rev": "36-802b9c1ae8216465ea1313cfcccd7795",
   "language": "javascript",
   "views": {
       "all_visiting_groups_by_date": {
           "map": "function(doc) {  \n  if (doc.type=='visiting_group') {\n      tmp_from_date = new Date(doc.from_date);\n      tmp_end_date = new Date(doc.to_date);\n        \n      var one_day = 1000*60*60*24;\n        \n      for (tmp_day = tmp_from_date; tmp_day <= tmp_end_date; tmp_day = new Date(tmp_day.getTime() + one_day)) {\n        emit(tmp_day.toDateString(), null);\n      }\n   }   \n}"
       },
       "bookings_of_visiting_group": {
           "map": "function(doc) {\n           if (doc.type=='booking') {\n\t  \nif (doc.booking_state > -100 ) {    if (doc.visiting_group_id != '') {\n                emit(doc.visiting_group_id, null);\n              }\n              emit(doc.visiting_group_name, null);\n\n\n           }\n    }    }"
       },
       "visiting_group_names": {
           "map": "function(doc) {  if (doc.type=='visiting_group') {\n                                    emit([doc.from_date, doc.to_date], [doc._id, doc.name]);\n                                 }\n                               }"
       },
       "all_names_among_bookings": {
           "map": "function(doc) {  if (doc.type=='booking') { if (doc.booking_state > -100)                                    emit([doc.booking_day_id, doc.visiting_group_name], 1);\n                                 }}",
           "reduce": "function(keys,values,rereduce) { return null }"
       },
       "visiting_group_by_name": {
           "map": "function(doc) {  if (doc.type=='visiting_group') {\nemit(doc.name, null);    }\n                               }"
       },
       "all_visiting_groups": {
           "map": "function(doc) {  if (doc.type=='visiting_group') {\n                                    emit([doc.from_date, doc._id], null);\n                                 }\n                               }"
       },
       "all_visiting_groups_by_boknstatus": {
           "map": "function(doc) {  if (doc.type=='visiting_group') {\n                                    emit([doc.boknstatus, doc.from_date], null);\n                                 }\n                               }"
       }
   }
}