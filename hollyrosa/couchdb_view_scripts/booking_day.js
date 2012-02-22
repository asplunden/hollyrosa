{
   "_id": "_design/booking_day",
   "_rev": "19-30729a4d2844775626e4410c87ead33a",
   "language": "javascript",
   "views": {
       "all_booking_days": {
           "map": "function(doc) {\n          if (doc.type=='booking_day') {\n                emit(doc.date, null); };\n      }"
       },
       "non_deleted_bookings_of_booking_day": {
           "map": "function(doc) {\n                 if (doc.type=='booking') {\n\t      if ((doc.booking_day_id != '') && (doc.booking_state > -100)) \n                    {\n                emit(doc.booking_day_id, doc);\n              }\n           }\n        }"
       },
       "unscheduled_bookings_by_date": {
           "map": "function(doc) {  \n  if (doc.type=='booking') {\n    if ((doc.booking_day_id=='') && (doc.booking_state > -100)) {\n        \n        tmp_from_date = new Date(doc.valid_from);\n        tmp_end_date = new Date(doc.valid_to);\n        \n        var one_day = 1000*60*60*24;\n        \n        for (tmp_day = tmp_from_date; tmp_day <= tmp_end_date; tmp_day = new Date(tmp_day.getTime() + one_day)) {\n            emit(tmp_day.toDateString(), doc);\n        }\n     }\n  }   \n}"
       },
       "unscheduled_bookings_by_visiting_group_name": {
           "map": "function(doc) {  if (doc.type=='booking') {\n                 if ((doc.booking_day_id=='') && (doc.booking_state > -100)) { \n                      emit([doc.visiting_group_name], doc); }                                }\n                               }"
       },
       "slot_state_of_booking_day": {
           "map": "function(doc) {  if (doc.type=='slot_state') { emit(doc.booking_day_id, doc); }     }"
       },
       "slot_id_of_booking": {
           "map": "function(doc) {  if (doc.type=='booking') { emit(doc.slot_id, null); }     }"
       },
       "slot_state_of_slot_id": {
           "map": "function(doc) {  if (doc.type=='slot_state') { emit(doc.slot_id, null); }     }"
       },
       "slot_state_of_slot_id_and_booking_day_id": {
           "map": "function(doc) {  if (doc.type=='slot_state') { emit([doc.slot_id, doc.booking_day_id], null); }     }"
       }
   }
}