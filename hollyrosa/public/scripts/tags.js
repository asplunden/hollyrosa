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

 
define(["dojo/_base/array", "dijit/registry","dijit/Menu","dijit/MenuItem", 'dijit/Dialog', 'dijit/form/Form', 'dijit/form/TextBox', "dijit/form/Button", "dijit/layout/ContentPane", 'dojox/layout/TableContainer',    "dojo/query!css2", "dojo/dom", "dojo/dom-style", "dojo/dom-construct", "dojo/request/xhr", "dojo/ready"], 
    function(array, registry, Menu, MenuItem, dijitDialog, dijitForm, dijitTextBox, dijitButton, contentPane, tableContainer, query, dom, domStyle, domConstruct, xhr, ready){


/**
 *
 **/
function updateTags(data, visiting_group_id, node_id) {
    var query_str = '#'+node_id+' .tag';
    var all_tags = query(query_str);
    
    array.forEach(all_tags, function(t) {domConstruct.destroy(t.parentElement) } );
    
    var tags = data['tags'];
    var ul_tag_list = dom.byId(node_id);

    for (t in tags) {
      domConstruct.create("li", {innerHTML:tags[t]+' <a href="javascript:;" class="tag">(X)</a>', 'hollyrosa:vgid':visiting_group_id}, ul_tag_list);
    }
}


/**
 *
 **/
function updateTagsCloseDialog(data, visiting_group_id, node_id, tag_dialog) {
    updateTags(data, visiting_group_id, node_id) ;
    tag_dialog.hide();
}


/**
 *
 **
function add_visiting_group_tags_XHR(ajax_url, visiting_group_id, tags) {
    tags = tags.trim();
    if ('' != tags) {
        xhr(ajax_url, {
        query: {'id': visiting_group_id, 'tags': tags},
        handleAs: "json",
        method: "POST"}).then( updateTags );
    } else {
        domStyle.set(dom.byId('add_tag_form'), 'visibility','hidden');
    }
}
*/

/**
 *
 **/
function createAddTagDialog(ajax_url, on_tags_added) { // callback that XHR calls with the result, it needs to know the target node id thoug...
    var tag_dialog = new dijitDialog({
        title: "Add Tags",
        style: ""
    });

    var tag_form = new dijitForm();
    var tag_text_input = new dijitTextBox({
        name: "tags",
        label: "Tags",
        value: "",
        placeHolder: "type in your tags"
    }, 'tags').placeAt(tag_form.containerNode);
    
    
    var add_tag_button = new dijitButton({
        label: "Add",
        onClick: function(){
            form_values = tag_form.getValues();
            tags = form_values['tags'];
            tags.trim();
            if ('' != tags) {
                xhr(ajax_url, {
                handleAs:"json",
                method:"POST",
                query: {'id':tag_dialog.hollyrosa_vgid, 'tags':tags}}).then( function(data) { on_tags_added(data, tag_dialog.hollyrosa_vgid, tag_dialog.hollyrosa_node_id, tag_dialog); } );
            } else { 
                tag_dialog.hide(); 
            }
            tag_form_values = tag_form.getValues();
            tag_form_values.tags = '';
            tag_form.setValues(tag_form_values);
        }
    }, "add_tag_button_node").placeAt(tag_form.containerNode); 
    
    tag_dialog.set('content', tag_form);
    
    return tag_dialog;
}


/**
 *
 **/
function showAddTagDialog(tag_dialog, visiting_group_id, node_id) {
    tag_dialog.hollyrosa_vgid =  visiting_group_id;
    tag_dialog.hollyrosa_node_id = node_id;
    tag_dialog.show();
}


return {
updateTagsCloseDialog:updateTagsCloseDialog,
updateTags:updateTags,
createAddTagDialog:createAddTagDialog,
showAddTagDialog:showAddTagDialog,
    
    
getTags:function get_visiting_group_tags_from_XHR(ajax_url, visiting_group_id, node_id) {
    xhr(ajax_url, {
    query: {id: visiting_group_id},
    handleAs: "json",
    method: "GET"}).then( function(data) { updateTags(data, visiting_group_id, node_id); } );    
},


deleteTag:function delete_visiting_group_tag_XHR(ajax_url, visiting_group_id, node_id, tag) {
    xhr(ajax_url, {
    query: {'id': visiting_group_id, 'tag': tag},
    handleAs: "json",
    method:"POST"}).then( function(data) {updateTags(data, visiting_group_id, node_id);} );
},

/*
addTags:function addTags(ajax_url, visiting_group_id, element_id) {
    var input = dom.byId(element_id);
    var text = input.value;
    add_visiting_group_tags_XHR(ajax_url, visiting_group_id, text);
},
*/

/*
showTagsForm:function showTagsForm() {
    var tags_form = dom.byId('add_tag_form');
    domStyle.set(tags_form, 'visibility','visible');
}
*/

}});
