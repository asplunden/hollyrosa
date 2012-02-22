{
   "_id": "_design/all_activities",
   "_rev": "19-150837758b2c53b7a653abbf4ec85f6c",
   "language": "javascript",
   "views": {
       "all_activities": {
           "map": "function(doc) { if(doc.type=='activity') {\n  emit([doc.zorder, doc._id], null)}; \n\t}"
       },
       "all_activity_groups": {
           "map": "function(doc) { if(doc.type=='activity_group') {emit(doc.zorder, doc)};}"
       },
       "activity_titles": {
           "map": "function(doc) { if(doc.type=='activity') {emit([doc._id, doc.title], null)};}"
       },
       "erasure": {
           "map": "function(doc) { if(doc.type!='activity' && doc.type!='activity_group' && doc.type!='day_schema' && doc.type!='user' && doc.type!='visiting_group') {emit([doc._id, doc.title], null);}\nif (doc.type=='visiting_group') {emit(doc._id, doc);}\n\n}"
       }
   }
}