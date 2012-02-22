{
   "_id": "_design/history",
   "_rev": "4-7d5e451afe0693103845b2ac63c1b736",
   "language": "javascript",
   "views": {
       "all_history": {
           "map": "function(doc) {\n\t\tif (doc.type=='booking_history') { \n\t\t  emit([doc.timestamp, doc.booking_id, doc.changed_by], doc); }; }"
       },
       "history_by_booking_id": {
           "map": "function(doc) { if (doc.type=='booking_history')  emit(doc.booking_id, doc); }"
       },
       "history_by_username": {
           "map": "function(doc) {  if (doc.type=='booking_history') {\n                                    emit(doc.changed_by, doc);\n                                 }\n                               }"
       }
   }
}