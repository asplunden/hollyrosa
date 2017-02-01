/**
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

/**
Modules that can be loaded:

**/
define(["tags", "dojo/dom-attr", "dojo/_base/array", "dojo/dom-construct", "dojo/_base/window", "dijit/Menu","dijit/MenuItem", "dijit/CheckedMenuItem", "dijit/MenuSeparator", "dojo/query", "dojo/on", "dojo/io-query", "dojo/dom", "dojo/json", "dojo/cookie", "dojo/dom-style", "dojo/request/xhr", "dojo/domReady!"],
  function(tags, domAttr, array, domConstruct, win, Menu, MenuItem, CheckedMenuItem, MenuSeparator, query, on, ioQuery, dom, json, cookie, domStyle, xhr)
  {
    function updateNotes(data, tag_and_note_config) {
      var vgroup_id = data['id'];
      var load_note_link = dom.byId('load_notes_for_' + vgroup_id);
      domConstruct.destroy(load_note_link);

      var notes = data['notes'];
      for (n in notes) {
        note = notes[n];
        var notes_for_id = 'notes_for_' + note['target_id'];

        e = dom.byId(notes_for_id);
        var note_div = domConstruct.create("div", {innerHTML: note['text'], class:note['type']+'2'}, e);
        if (note['type'] == 'attachment') {
          var note_div2 = domConstruct.create("div", {}, note_div);

          var attachments = note['_attachments'];
          var keys = Object.keys(attachments);
          array.forEach(keys, function(key) {
            var ioq = {
              attachment_id: note._id,
              doc_id: key
            };

            var ul = domConstruct.create("ul", {}, note_div2);
            var li = domConstruct.create("li", {}, ul);

            domConstruct.create("a", {href:tag_and_note_config.download_attachment_url + '?' + ioQuery.objectToQuery(ioq), innerHTML: key}, li);
          });
        }
      }
    }


    /// TODO: need to fix this deleteTagHelper so it
    function deleteTagHelper(evt, tag_and_note_config) {
      var tag_elem = evt.target.parentElement;
      var inner_text = tag_elem.textContent;
      inner_text = inner_text.replace(' (X)','');
      var visiting_group_id = tag_elem.attributes['hollyrosa:vgid'].value;
      tags.deleteTag(tag_and_note_config.delete_tag_url, visiting_group_id, tag_elem.parentElement.id, inner_text);
    }


    var tag_dialog; //= tags.createAddTagDialog(tag_and_note_config.add_tag_url, tags.updateTagsCloseDialog );


    function show_add_tag_dialog(node_id) {
      var visiting_group_id = node_id.attributes['hollyrosa:vgid'].value;
      tags.showAddTagDialog(tag_dialog, visiting_group_id, node_id.attributes['hollyrosa:taglist_node_id'].value);
    }


    function loadNotesFor(id, tag_and_note_config) {
      xhr(tag_and_note_config.get_notes_for_visiting_group_url, {
        query: {id: id},
        handleAs: 'json',
        method: "GET"
      }).then( function(data){  updateNotes(data, tag_and_note_config) } );
    }

    function setup(tag_and_note_config) {
      on(win.doc, '.tag:click', function(evt) { deleteTagHelper(evt, tag_and_note_config)});

      var tag_ul_elems = query('.tag_list');

      array.forEach(tag_ul_elems, function(ul_tag_elem) {
        var node_id = ul_tag_elem.id;
        var vgid = ul_tag_elem.attributes['hollyrosa:vgid'].value;
        tags.getTags(tag_and_note_config.get_tags_url, vgid, node_id ) ;
      });

      tag_dialog = tags.createAddTagDialog(tag_and_note_config.add_tag_url, tags.updateTagsCloseDialog );
    }

    return {
      show_add_tag_dialog: show_add_tag_dialog,
      loadNotesFor: loadNotesFor,
      setup: setup,
      tag_dialog: tag_dialog
    }
  }
);
