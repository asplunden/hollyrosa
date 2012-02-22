{
   "_id": "_design/tags",
   "_rev": "5-6984417891d354ed18098128fdcce4b0",
   "language": "javascript",
   "views": {
       "all_tags": {
           "map": "function(doc) {   for (t in doc.tags) {   emit(doc.tags[t], {_id:doc._id}); } }",
           "reduce": "function(keys,values,rereduce) { return length(values);}"
       },
       "documents_by_tag": {
           "map": "function(doc) {   for (t in doc.tags) {   emit(doc.tags[t], {_id:doc._id}); } }"
       }
   }
}