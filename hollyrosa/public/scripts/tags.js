/*
* Copyright 2010-2017 Martin Eliasson
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


define(["dojo/_base/array", "dijit/registry","dijit/Menu","dijit/MenuItem", 'dijit/Dialog', 'dijit/form/Form', 'dijit/form/TextBox', "dijit/form/Button", "dijit/layout/ContentPane", 'dojox/layout/TableContainer',    "dojo/query!css2", "dojo/dom", "dojo/dom-style", "dojo/dom-construct", "dojo/request/xhr", "dojo/on", "dojo/keys", "dojo/ready"],
function(array, registry, Menu, MenuItem, dijitDialog, dijitForm, dijitTextBox, dijitButton, contentPane, tableContainer, query, dom, domStyle, domConstruct, xhr, on, keys, ready){


  /**
  * Updates all tags by simply destroying all existing tags and repopulating.

  * Finds all element that looks like tags in node with id node_id.
  * All found tags parent node is destroyed (tags are element withing a list item
  * so we also want to destroy the list item)
  *
  * Next, new tags are created as a-elements within li-element with properties
  * attached to the ul element having id node_id
  *
  * All tags are found in the data object as an array in the tags attribute,
  * the data object comes from an ajax request.
  **/
  function updateTags(data, visiting_group_id, node_id) {
    var query_str = '#'+node_id+' .hollytag';
    var all_tags = query(query_str);

    array.forEach(all_tags, function(t) {domConstruct.destroy(t.parentElement) } );

    var tags = data['tags'];
    var ul_tag_list = dom.byId(node_id);

    for (t in tags) {
      domConstruct.create("span", {innerHTML: tags[t]+' <a href="javascript:;" class="hollytag">(X)</a>', 'hollyrosa:vgid':visiting_group_id, 'class':'tag is-info is-small'}, ul_tag_list);
    }
  }


  /**
  * Callback function that hides the dialog where the usrr may enter tags.
  **/
  function updateTagsCloseDialog(data, visiting_group_id, node_id, tag_dialog) {
    updateTags(data, visiting_group_id, node_id) ;
    tag_dialog.hide();
  }



  /**
  * Creates a dialog to allow the user to add tags.
  * This dialog is probably where useful to study in order to create moe nice dialogs in the futute.
  *
  **/
  function createAddTagDialog(ajax_url, on_tags_added) { // callback that XHR calls with the result, it needs to know the target node id thoug...

    //..create the dialog
    var tag_dialog = new dijitDialog({
      title: "Add Tags",
      style: ""
    });

    //...add a dijit form in the dialog
    var tag_form = new dijitForm();

    //...attach a text input to the form
    var tag_text_input = new dijitTextBox({
      name: "tags",
      label: "Tags",
      value: "",
      placeHolder: "type in your tags"
    }, 'tags').placeAt(tag_form.containerNode);

    //...create a local function to handle form submit,
    //   it is POSTing the form value after trimming to hollyrosa backend system.
    //   On successful submit, on_tags_added is called with parameters so the returned
    //   list of tags is shown on the correct group and so tag dialog is closed.
    //   The tag dialog doesent close until the AJAX has returned.
    function tag_form_submit_handler() {
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


      var add_tag_button = new dijitButton({
        label: "Add",
        onClick: tag_form_submit_handler
      }, "add_tag_button_node").placeAt(tag_form.containerNode);

      tag_dialog.set('content', tag_form);

      //...setting up key event handler so we can react to return pressed
      var inputs = query("input");

      //...add en event listener on keydown so we can block the form submit on enter
      on(add_tag_button, "keydown", function(event) {
        switch(event.keyCode) {
          //...prevent default keeps the form from submiting when the enter button is pressed on the submit button
          case keys.ENTER:
            event.preventDefault();

          // submit the form
          //console.log("form submitted!");
          //tag_form_submit_handler();
            break;
          default:
            console.log("some other key: " + event.keyCode);
        }
      });

      return tag_dialog;
    }


    /**
    * Shows the add tag dialog
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

    }});
