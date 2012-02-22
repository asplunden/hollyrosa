{
   "_id": "_design/notes",
   "_rev": "17-44016f8ff40285fc68767e86c93dd668",
   "language": "javascript",
   "views": {
       "notes_by_target_datesorted": {
           "map": "function(doc) {\n    if (doc.type=='note') {emit([doc.target_id, doc.timestamp], null); }}"
       },
       "notes_by_target": {
           "map": "function(doc) {\n    if (doc.type=='note') {emit(doc.target_id, null); }}"
       },
       "notes_for_list_bookings": {
           "map": "function(doc) {\n    if ((doc.type=='activity') || (doc.type=='activity_group')) { if(doc.booking_info_id != null) emit(doc._id, {_id:doc.booking_info_id}); }}"
       },
       "number_of_notes_per_target": {
           "map": "function(doc) {\n    if (doc.type=='note') {emit(doc.target_id, 1); }}",
           "reduce": "function(keys, values, rereduce) { return sum(values);}"
       }
   }
}