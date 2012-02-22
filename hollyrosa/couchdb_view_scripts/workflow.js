{
   "_id": "_design/workflow",
   "_rev": "23-874cbf703d600b294ef8813ae7c660a8",
   "language": "javascript",
   "views": {
       "all_scheduled_bookings": {
           "map": "function(doc) { if (doc.type=='booking') { if (doc.booking_day_id != '' && doc.booking_day_id != null) { emit(doc.booking_day_id, null); } }; }"
       },
       "all_unscheduled_bookings": {
           "map": "function(doc) { if (doc.type=='booking') { if (doc.booking_day_id == '') {  if (doc.booking_state > -100 ) {  emit(doc.booking_id, null); } } } }"
       },
       "all_bookings_by_booking_state": {
           "map": "function(doc) {  if (doc.type=='booking') { if (doc.booking_day_id != '') { emit(doc.booking_state, null);  } } }"
       },
       "booking_day_map_info": {
           "map": "function(doc) {  if (doc.type=='booking_day') { emit(doc._id, [doc.date, doc.day_schema_id]);  } }"
       },
       "user_name_map": {
           "map": "function(doc) {  if (doc.type=='user') { emit(doc._id, doc.display_name);  } }"
       },
       "all_similar_bookings": {
           "map": "function(doc) { if (doc.type=='booking') { if (doc.booking_day_id != '' && doc.booking_day_id != null && doc.visiting_group_id != '' && doc.visiting_group_id != null) { if (doc.booking_state > -100) { emit([doc.visiting_group_id, doc.activity_id], null); } } }; }"
       }
   }
}