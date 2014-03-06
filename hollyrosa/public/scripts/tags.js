/*
 * Copyright 2012, 2013, 2014 Martin Eliasson
 *
 * This file is part of Hollyrosa
 *
 * Hollyrosa is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Hollyrosa is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.
 **/

 
define(["dojo/_base/array", "dijit/registry","dijit/Menu","dijit/MenuItem","dojo/query!css2", "dojo/dom", "dojo/dom-style", "dojo/dom-construct", "dojo/request/xhr", "dojo/ready"], function(array, registry, Menu, MenuItem, query, dom, domStyle, domConstruct, xhr, ready){

function updateTags(data) {
    var all_tags = query('.tag');
    
    array.forEach(all_tags, function(t) {domConstruct.destroy(t.parentElement) } );
    
    var tags = data['tags'];
    var ul_tag_list = dom.byId("taglist");

    for (t in tags) {
      domConstruct.create("li", {innerHTML:tags[t]+' <a href="javascript:;" class="tag">(X)</a>'}, ul_tag_list);
    }
    dom.byId('tag_input').value = '';
    domStyle.set(dom.byId('add_tag_form'), 'visibility','hidden');
}


function add_visiting_group_tags_XHR(ajax_url, visiting_group_id, tags) {   
    xhr(ajax_url, {
    query: {'id': visiting_group_id, 'tags': tags},
    handleAs: "json",
    method: "GET"}).then( updateTags );
}


return {
updateTags:updateTags,
  
getTags:function get_visiting_group_tags_from_XHR(ajax_url, visiting_group_id) {
    xhr(ajax_url, {
    query: {id: visiting_group_id},
    handleAs: "json",
    method: "GET"}).then( updateTags );    
},


deleteTag:function delete_visiting_group_tag_XHR(ajax_url, visiting_group_id, tag) {
    xhr(ajax_url, {
    query: {'id': visiting_group_id, 'tag': tag},
    handleAs: "json",
    method:"GET"}).then( updateTags );
},


addTags:function addTags(ajax_url, visiting_group_id, element_id) {
    var input = dom.byId(element_id);
    var text = input.value;
    add_visiting_group_tags_XHR(ajax_url, visiting_group_id, text);
},

showTagsForm:function showTagsForm() {
    var tags_form = dom.byId('add_tag_form');
    domStyle.set(tags_form, 'visibility','visible');
}

}});
