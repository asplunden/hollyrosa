# -*- coding: utf-8 -*-
"""
Copyright 2010-2017 Martin Eliasson

This file is part of Hollyrosa

Hollyrosa is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Hollyrosa is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.

"""

import datetime, logging, json, time, types, copy


from tg import expose, flash, require, url, request, redirect,  validate
from tg.predicates import Any, is_user, has_permission
from hollyrosa.lib.base import BaseController
from hollyrosa.model import holly_couch

from hollyrosa.widgets.edit_vodb_group_form import create_edit_vodb_group_form

from tg import tmpl_context


log = logging.getLogger()

#...this can later be moved to the VisitingGroup module whenever it is broken out
from hollyrosa.controllers.common import has_level, DataContainer, getLoggedInUserId, reFormatDate, ensurePostRequest, sanitizeDate

from hollyrosa.model.booking_couch import genUID, getBookingDayOfDate, getSchemaSlotActivityMap, getVisitingGroupByBoknr, getAllVisitingGroups, getTargetNumberOfNotesMap, getAllTags, getNotesForTarget, getBookingsOfVisitingGroup, getBookingOverview, getBookingEatOverview, getDocumentsByTag, getVisitingGroupsByVodbState, getVisitingGroupsByBoknstatus, dateRange,  getVisitingGroupsByGroupType, getRoomBookingsOfVODBGroup,  getAllActivities, getVisitingGroupTypes, getVisitingGroupsAtDate
from hollyrosa.controllers.booking_history import remember_tag_change,  remember_booking_vgroup_properties_change
from hollyrosa.controllers.common import workflow_map, DataContainer, getLoggedInUserId,  change_op_map, getRenderContent, getRenderContentDict,  computeCacheContent, has_level
from hollyrosa.controllers.common import reFormatDate, bokn_status_map, vodb_status_map, makeVODBGroupObjectOfVGDictionary, vodb_eat_times_options, vodb_live_times_options, sanitizeDate, cleanHtml
from hollyrosa.controllers.visiting_group_common import populatePropertiesAndRemoveUnusedProperties,  updateBookingsCacheContentAfterPropertyChange, updateVisitingGroupComputedSheets, computeAllUsedVisitingGroupsTagsForTagSheet,  program_visiting_group_properties_template,  staff_visiting_group_properties_template,  course_visiting_group_properties_template
from hollyrosa.controllers.booking_history import remember_new_booking_request
from hollyrosa.controllers import common_couch

from formencode import validators

__all__ = ['VODBGroup']

vodb_live_times = [u'fm', u'em', u'evening']
vodb_eat_times = [u'breakfast', u'lunch', u'lunch_arrive', u'lunch_depart', u'dinner']

#vodb_live_cols =




class VODBGroup(BaseController):

    #
    #...list all groups...Borrow from Visiting group.... need to refactor out commons
    #   thinking that all groups share some very basic common stuff. at least they should in the long run
    #
    #   think about what in the template should be different...


    @expose('hollyrosa.templates.vodb_group_view_all')
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members and viewers may view visiting group properties'))
    def view_all(self):
        visiting_groups = [v.doc for v in getAllVisitingGroups(holly_couch)]
        remaining_visiting_groups_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        all_tags = [t.key for t in getAllTags(holly_couch)]
        all_tags_list =  '[' + ''.join(['"'+l+'", ' for l in all_tags]  ) +']'

        state_map_list = '['+ ','.join( ['["'+str(k)+'","'+v+'"]'  for (k,v) in bokn_status_map.items()]     ) +']'

        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=remaining_visiting_groups_map.keys(), program_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=all_tags, has_notes_map=has_notes_map, visiting_group_types=getVisitingGroupTypes(holly_couch), state_map_list=state_map_list, vodb_state_map=bokn_status_map)


    @expose('hollyrosa.templates.vodb_group_view_all')
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members and viewers may view visiting group properties'))
    def view_today(self):
        at_date = datetime.datetime.today().strftime('%Y-%m-%d')
        visiting_groups = [v.doc for v in getVisitingGroupsAtDate(holly_couch, at_date)]
        remaining_visiting_groups_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        all_tags = [t.key for t in getAllTags(holly_couch)]
        all_tags_list =  '[' + ''.join(['"'+l+'", ' for l in all_tags]  ) +']'

        state_map_list = '['+ ','.join( ['["'+str(k)+'","'+v+'"]'  for (k,v) in bokn_status_map.items()]     ) +']'

        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=remaining_visiting_groups_map.keys(), program_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=all_tags, has_notes_map=has_notes_map, visiting_group_types=getVisitingGroupTypes(holly_couch), state_map_list=state_map_list, vodb_state_map=bokn_status_map)


    @expose('hollyrosa.templates.vodb_group_view_all')
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members and viewers may view visiting group properties'))
    def view_tags(self, tag):
        # TODO>: rename and maybe only return visiting groups docs ?
        visiting_groups = [v.doc for v in getDocumentsByTag(holly_couch, tag)]
        remaining_visiting_groups_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        state_map_list = '['+ ','.join( ['["'+str(k)+'","'+v+'"]'  for (k,v) in bokn_status_map.items()]     ) +']'
        all_tags = [t.key for t in getAllTags(holly_couch)]
        all_tags_list =  '[' + ''.join(['"'+l+'", ' for l in all_tags]  ) +']'
        return dict(visiting_groups=visiting_groups,  remaining_visiting_group_names=remaining_visiting_groups_map.keys(), bokn_status_map=bokn_status_map,  vodb_state_map=bokn_status_map,  state_map_list=state_map_list, program_state_map=bokn_status_map,  reFormatDate=reFormatDate, all_tags=all_tags, has_notes_map=has_notes_map, visiting_group_types=getVisitingGroupTypes(holly_couch))


    @expose('hollyrosa.templates.vodb_group_view_all')
    @validate(validators={'program_state':validators.Int(not_empty=True)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_program_state(self,  program_state=None):
        #boknstatus=boknstatus[:4] # amateurish quick sanitation
        #visiting_groups = get_visiting_groups_with_boknstatus(boknstatus)
        visiting_groups =[v.doc for v in getVisitingGroupsByBoknstatus(holly_couch, program_state)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        all_tags = [t.key for t in getAllTags(holly_couch)]
        all_tags_list =  '[' + ''.join(['"'+l+'", ' for l in all_tags]  ) +']'
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=v_group_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=all_tags, has_notes_map=has_notes_map, visiting_group_types=getVisitingGroupTypes(holly_couch))


    @expose('hollyrosa.templates.vodb_group_view_all')
    @validate(validators={'vodb_state':validators.Int(not_empty=True)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_vodb_state(self,  vodb_state=None):
        visiting_groups =[v.doc for v in getVisitingGroupsByVodbState(holly_couch, vodb_state)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        state_map_list = '['+ ','.join( ['["'+str(k)+'","'+v+'"]'  for (k,v) in bokn_status_map.items()]     ) +']'
        all_tags = [t.key for t in getAllTags(holly_couch)]
        all_tags_list =  '[' + ''.join(['"'+l+'", ' for l in all_tags]  ) +']'
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=v_group_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, state_map_list=state_map_list, reFormatDate=reFormatDate, all_tags=all_tags, has_notes_map=has_notes_map, visiting_group_types=getVisitingGroupTypes(holly_couch))


    @expose('hollyrosa.templates.vodb_group_view_all')
    @validate(validators={'group_type':validators.UnicodeString(not_empty=True)})
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only staff members and viewers may view visiting group properties'))
    def view_group_type(self,  group_type=None):
        #boknstatus=boknstatus[:4] # amateurish quick sanitation
        #visiting_groups = get_visiting_groups_with_boknstatus(boknstatus)
        visiting_groups =[v.doc for v in getVisitingGroupsByGroupType(holly_couch, group_type)]
        v_group_map = dict()
        has_notes_map = getTargetNumberOfNotesMap(holly_couch)
        all_tags = [t.key for t in getAllTags(holly_couch)]
        all_tags_list =  '[' + ''.join(['"'+l+'", ' for l in all_tags]  ) +']'
        return dict(visiting_groups=visiting_groups, remaining_visiting_group_names=v_group_map.keys(), program_state_map=bokn_status_map, vodb_state_map=bokn_status_map, reFormatDate=reFormatDate, all_tags=all_tags, has_notes_map=has_notes_map, visiting_group_types=getVisitingGroupTypes(holly_couch))


    @expose('hollyrosa.templates.vodb_group_edit')
    @require(Any(has_level('pl'), has_level('pl'), has_level('staff'), msg='Only staff and pl may edit vodb group data'))
    def edit_group_data(self, visiting_group_id='', subtype='', **kwargs):
#        visiting_group_x = holly_couch[visiting_group_id]
        tmpl_context.form = create_edit_vodb_group_form

        is_new = ((None == visiting_group_id) or ('' == visiting_group_id))
        if is_new:
            properties_template = dict()

            if subtype == 'program':
                properties_template = program_visiting_group_properties_template

            if subtype == 'staff':
                properties_template = staff_visiting_group_properties_template

            if subtype =='course':
                properties_template = course_visiting_group_properties_template

            visiting_group = dict(name='', id=None, _id=None, info='', visiting_group_properties=properties_template, subtype=subtype, contact_person='', contact_person_email='', contact_person_phone='', boknr='')

        else:
            visiting_group_c = common_couch.getVisitingGroup(holly_couch, visiting_group_id)
            for k in ['vodb_contact_name', 'vodb_contact_email', 'vodb_contact_phone', 'vodb_contact_address']:
                if not visiting_group_c.has_key(k):
                    visiting_group_c[k] = ''
            if not visiting_group_c.has_key('subtype'):
                visiting_group_c['subtype'] = 'program'
            visiting_group = makeVODBGroupObjectOfVGDictionary(visiting_group_c)


#        #...add data if it doesent exist
#        if not visiting_group_x.has_key('vodb_status'):
#            visiting_group_x['vodb_status'] = 0

        return dict(vodb_group=visiting_group, reFormatDate=reFormatDate, bokn_status_map=workflow_map, is_new=is_new)


    def newOrExistingVgroupId(self, a_id):
        """returns the id if it exists or if a_id is empty or none, a new id is generated and returned."""
        is_new = False
        r_id = a_id

        if ((None == a_id) or (a_id == '')):
            is_new = True
            r_id = genUID(type='visiting_group')

        return is_new, r_id



    @expose()
    @validate(create_edit_vodb_group_form, error_handler=edit_group_data)
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members may change visiting group properties'))
    def save_vodb_group_properties(self, vodb_group_id='', boknr='', name='', info='', camping_location='', vodb_contact_name='', vodb_contact_phone='', vodb_contact_email='', vodb_contact_address='', from_date='', to_date='', subtype='', visiting_group_properties=None):
        ensurePostRequest(request, __name__)
        log.debug('save_vodb_group_properties')
        id = vodb_group_id
        is_new, vgroup_id = self.newOrExistingVgroupId(id)

        #...load or create new vgroup
        if is_new:
            log.info("saving new group")
#            program_state = 0
#            vodb_state = 0
            if not subtype in ['program','course','staff']:
                flash('error with subtype')
                raise redirect(request.referrer)

            visiting_group_o = dict(type='visiting_group',  subtype=subtype,  tags=[],  boknstatus=0,  vodbstatus=0)

        else:
            visiting_group_o = holly_couch[vgroup_id]


        #...fill in data
        visiting_group_o['name'] = name
        visiting_group_o['info'] = cleanHtml(info)
        visiting_group_o['from_date'] = sanitizeDate(from_date)[1] # TODO better error handling
        visiting_group_o['to_date'] = sanitizeDate(to_date)[1] # TODO better error handling
        visiting_group_o['vodb_contact_name'] = vodb_contact_name
        visiting_group_o['vodb_contact_email'] = vodb_contact_email
        visiting_group_o['vodb_contact_phone'] = vodb_contact_phone
        visiting_group_o['vodb_contact_address'] = vodb_contact_address
        visiting_group_o['boknr'] = boknr
        visiting_group_o['camping_location'] = camping_location

        # TODO: figure out the order of updating things if something goes wrong.

        #...update properties
        visiting_group_o['visiting_group_properties'] = populatePropertiesAndRemoveUnusedProperties(visiting_group_o, visiting_group_properties)

        updateBookingsCacheContentAfterPropertyChange(holly_couch, visiting_group_o,  getLoggedInUserId(request))
        vodb_tag_times_tags = computeAllUsedVisitingGroupsTagsForTagSheet(visiting_group_o['tags'], visiting_group_o.get('vodb_tag_sheet',dict(items=[]))['items'])
        updateVisitingGroupComputedSheets(visiting_group_o, visiting_group_o['visiting_group_properties'], sheet_map=dict(vodb_eat_sheet=vodb_eat_times_options, vodb_live_sheet=vodb_live_times_options, vodb_tag_sheet=vodb_tag_times_tags))

        holly_couch[vgroup_id] = visiting_group_o


        if visiting_group_o.has_key('_id'):
            raise redirect('/vodb_group/view_vodb_group?visiting_group_id='+visiting_group_o['_id'])
        raise redirect('/vodb_group/view_all')



    def dateGen(self, from_date, to_date):
        """generator expression for generating all dates from from_date to to_date"""
        tmp_result = datetime.datetime.strptime(from_date, "%Y-%m-%d")

        yield from_date
        delta = datetime.timedelta(1) #).strftime('%Y-%m-%d')
        tmp_result_str = from_date
        while tmp_result_str != to_date:
            tmp_result = tmp_result + delta
            tmp_result_str = tmp_result.strftime('%Y-%m-%d')
            yield tmp_result_str



    def make_empty_vodb_sheet(self, from_date, to_date, times, cols):
        """
        makes an empty sheet with all date-times for among others the live sheet
        """

        r1_items = list()
        for tmp_date in self.dateGen(from_date, to_date):
            for tmp_time in times:
                it = dict(date=tmp_date, time=tmp_time)
                it['rid'] = self.get_composite_key(it)
                for tmp_col in cols:
                    it[tmp_col] = 0
                r1_items.append(it)

        return dict(identifier='rid', items=r1_items)


    def make_empty_vodb_live_sheet(self, from_date, to_date):
        return self.make_empty_vodb_sheet(from_date, to_date, vodb_live_times, vodb_live_times_options)


    def make_empty_vodb_eat_sheet(self, from_date, to_date):
        return self.make_empty_vodb_sheet(from_date, to_date, vodb_eat_times, vodb_eat_times_options)


    def get_composite_key(self, row):
        # TODO:  refactor out
        # store composite key and use it as rid and things will go much faster.
        d = dict()
        d[u'fm']=u'1'
        d[u'em']=u'2'
        d[u'evening']=u'3'
        d[u'breakfast'] = u'10'
        d[u'lunch'] = u'11'
        d[u'lunch_arrive'] = u'12'
        d[u'lunch_depart'] = u'13'
        d[u'dinner'] = u'18'

        return row['date'] + u'_' +d.get(row['time'],'unknown')


    def fn_cmp_composite_key(self, a, b):
        return cmp(self.get_composite_key(a), self.get_composite_key(b))


    # the expression del referrs to Data Eat Live. LED was too confusing so I choose DEL :)




    def prepareAndSanitizeSheetDataForEdit(self,  a_visiting_group,  a_sheet_name,  a_from_date,  a_to_date,  a_empty_sheet):
        """sanitizing data, basically, removing data outside date range and adding data where it doesent exist"""

        data = a_visiting_group.get(a_sheet_name, dict(identifier='rid', items=[]))

        row_lookup = dict()
        for tmp_row in a_empty_sheet['items']:
            row_lookup[tmp_row['rid']] = tmp_row

        for tmp_row in data['items']:
            composite_key = tmp_row['rid']
            if row_lookup.has_key(composite_key):
                del row_lookup[composite_key]

        for row_left in row_lookup.values():
            data['items'].append(row_left)

        #...re-sort the rows
        data_items = data['items']
        data_items.sort(self.fn_cmp_composite_key)
        data['items'] = data_items
        return json.dumps( data )


    @expose('hollyrosa.templates.vodb_group_edit_sheet')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def edit_group_sheet(self, visiting_group_id=''):
        visiting_group_o = holly_couch[visiting_group_id]
        tmpl_context.form = create_edit_vodb_group_form

        #...augument old data
        if not visiting_group_o.has_key('vodb_status'):
            visiting_group_o['vodb_status'] = 0
        for k in ['vodb_contact_name', 'vodb_contact_email', 'vodb_contact_phone', 'vodb_contact_address']:
            if not visiting_group_o.has_key(k):
                visiting_group_o[k] = ''

        #...sanitizing data, basically, removing data outside date range and adding data where it doesent exist
        l_from_date = visiting_group_o['from_date']
        l_to_date = visiting_group_o['to_date']
        empty_vodb_live_sheet = self.make_empty_vodb_live_sheet(visiting_group_o['from_date'], visiting_group_o['to_date'])
        visiting_group_o['vodb_live_sheet'] = self.prepareAndSanitizeSheetDataForEdit(visiting_group_o,  'vodb_live_sheet', l_from_date,  l_to_date,  empty_vodb_live_sheet )

        #...same thing for eat data
        empty_vodb_eat_sheet = self.make_empty_vodb_eat_sheet(visiting_group_o['from_date'], visiting_group_o['to_date'])
        visiting_group_o['vodb_eat_sheet'] = self.prepareAndSanitizeSheetDataForEdit(visiting_group_o,  'vodb_eat_sheet', l_from_date,  l_to_date,  empty_vodb_eat_sheet )

        #...same thing for tag data
        tag_data = visiting_group_o.get('vodb_tag_sheet', dict(identifier='rid', items=[]))
        all_current_vgroup_tags = computeAllUsedVisitingGroupsTagsForTagSheet(visiting_group_o['tags'], tag_data['items'])
        empty_vodb_tag_sheet = self.make_empty_vodb_sheet(visiting_group_o['from_date'], visiting_group_o['to_date'],vodb_live_times, all_current_vgroup_tags.keys())
        visiting_group_o['vodb_tag_sheet'] = self.prepareAndSanitizeSheetDataForEdit(visiting_group_o,  'vodb_tag_sheet', l_from_date,  l_to_date,  empty_vodb_tag_sheet)

        #...we also must supply tags for the tag_grid layout since it depends both on old used tags and current tags
        tag_layout_tags = json.dumps(visiting_group_o['tags'])

        #...TODO: load notes
        notes = []

        return dict(vodb_group=visiting_group_o, tag_layout_tags=tag_layout_tags, reFormatDate=reFormatDate, vodb_state_map=bokn_status_map, program_state_map=bokn_status_map,  notes=notes)



    @expose()
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only staff members may update vodb group sheets'))
    def update_group_sheets(self, vgroup_id='', tag_sheet=None, eat_sheet=None, live_sheet=None, saveButton=''):
        ensurePostRequest(request, __name__)
        # todo: accessor function making sure the type really is visiting_group
        visiting_group_o = holly_couch[vgroup_id]
        visiting_group_properties = visiting_group_o['visiting_group_properties']

        if eat_sheet != None:
            visiting_group_o['vodb_eat_sheet'] = json.loads(eat_sheet)

        if live_sheet != None:
            visiting_group_o['vodb_live_sheet'] = json.loads(live_sheet)

        if tag_sheet != None:
            vodb_tag_sheet = json.loads(tag_sheet)
            visiting_group_o['vodb_tag_sheet'] = vodb_tag_sheet

        vodb_tag_times_tags = computeAllUsedVisitingGroupsTagsForTagSheet(visiting_group_o['tags'], vodb_tag_sheet['items'])

        #self.vodb_sheet_property_substitution(visiting_group_o,  vodb_eat_times_options,  visiting_group_properties,  'vodb_eat_sheet')
        #self.vodb_sheet_property_substitution(visiting_group_o,  vodb_live_times_options,  visiting_group_properties,  'vodb_live_sheet')
        #self.vodb_sheet_property_substitution(visiting_group_o,  vodb_tag_times_tags,  visiting_group_properties,  'vodb_tag_sheet')

        updateVisitingGroupComputedSheets(visiting_group_o, visiting_group_properties, sheet_map=dict(vodb_eat_sheet=vodb_eat_times_options, vodb_live_sheet=vodb_live_times_options, vodb_tag_sheet=vodb_tag_times_tags))

        holly_couch[vgroup_id] = visiting_group_o
        raise redirect(request.referrer)



    @expose('hollyrosa.templates.vodb_group_view')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), msg='Only logged in users may view me properties'))
    def view_vodb_group(self, visiting_group_id=''):
        visiting_group_o = holly_couch[visiting_group_id]

        #...construct the age group list. It's going to be a json document. Hard coded.
        #... if we are to partially load from database and check that we can process it, we do need to go from python to json. (and back)
        #...construct a program request template. It's going to be a json document. Hard coded.
        notes = [n.doc for n in getNotesForTarget(holly_couch, visiting_group_id)]

        visiting_group_o.show_vodb_live_sheet = json.dumps(dict(identifier='rid', items=visiting_group_o.get('vodb_live_computed', list())))
        visiting_group_o.show_vodb_eat_sheet = json.dumps(dict(identifier='rid', items=visiting_group_o.get('vodb_eat_computed', list())))
        visiting_group_o.show_vodb_tag_sheet = json.dumps(dict(identifier='rid', items=visiting_group_o.get('vodb_tag_computed', list())))


        #...find room_bookings
        activities = dict()
        for x in getAllActivities(holly_couch):
            activities[x.key[1]] = x.doc

        room_bookings = list()
        for b in getRoomBookingsOfVODBGroup(holly_couch,  visiting_group_id):

            #...lookup slot map
            live_schema_id = 'room_schema.2013' # TODO: Read dynamically from booking day
            tmp_slot_row_data = list(holly_couch.view('day_schema/slot_map',  keys=[[b['slot_id'],  live_schema_id], [b['booking_end_slot_id'],  live_schema_id]]))

            start_time = tmp_slot_row_data[0].value[1]['time_from']
            end_time = tmp_slot_row_data[1].value[1]['time_to']
            b2 = DataContainer(booking_state=b['booking_state'],  cache_content=b['cache_content'],  content=b['content'] ,  activity=activities[b['activity_id']],  id=b['_id'],  booking_date=b.get('booking_date', 'Unknown'), booking_end_date=b.get('booking_end_date', 'Unknown'),  booking_day_id=b.get('booking_day_id', ''),  valid_from=b.get('valid_from',''),  valid_to=b.get('valid_to',''),  requested_date=b.get('requested_date',''),  start_time=start_time,  end_time=end_time)

            room_bookings.append(b2)


        tag_layout_tags = json.dumps(visiting_group_o['tags'])
        return dict(visiting_group=visiting_group_o, reFormatDate=reFormatDate, vodb_state_map=bokn_status_map, program_state_map=bokn_status_map, notes=notes, tag_layout_tags=tag_layout_tags,  room_bookings=room_bookings,  getRenderContent=getRenderContent)



    @expose('hollyrosa.templates.visiting_group_program_request_edit2')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), has_level('vgroup'), msg=u'Du måste vara inloggad för att få ändra i dina programönskemål'))
    def edit_request(self, visiting_group_id=''):
        visiting_group_o = holly_couch[str(visiting_group_id)]
        visiting_group_o.program_request_info = visiting_group_o.get('program_request_info','message to program!')
        visiting_group_o.program_request_have_skippers = visiting_group_o.get('program_request_have_skippers',0)
        visiting_group_o.program_request_miniscout = visiting_group_o.get('program_request_miniscout',0)

        #...construct a program request template. It's going to be a json document. Hard coded.
        #...supply booking request if it exists


        age_group_data_tmp = json.loads(age_group_data_raw)
        for tmp_item in age_group_data_tmp['items']:
            tmp_item['from_date'] = visiting_group_o['from_date']
            tmp_item['to_date'] = visiting_group_o['to_date']

        age_group_data = json.dumps(age_group_data_tmp)
        visiting_group_o.program_request_age_group = visiting_group_o.get('program_request_age_group', age_group_data)

        program_request_data_dict = {'identifier': 'id', 'items': [[{'id':0, 'requested_date': visiting_group_o['from_date'], 'requested_time':'', 'requested_activity': '', 'age_sma':False, 'age_spar':False, 'age_uppt':False, 'age_aven':False, 'age_utm':False, 'age_rov':False, 'age_led':False, 'note':''} for i in range(35)]] }



        program_request_data = json.dumps(program_request_data_dict)
        visiting_group_o.program_request = visiting_group_o.get('program_request', program_request_data)

        return dict(visiting_group_program_request=visiting_group_o, reFormatDate=reFormatDate, bokn_status_map=bokn_status_map)


        #
        # It would be a great step towards 2014 version with the improved 4-1 schedule view
        #

        #...raise...redirect referer...

    def fnCmpSortOnFromDate(self, a, b):
        return cmp(a['from_date'], b['from_date'])


    def compute_used_dates_and_times(self, rows):
        used_dates = dict()
        used_times = dict()
        for row in rows:
            used_dates[row.key[0]] = True
            used_times[row.key[1]] = True
        return used_dates, used_times


    @expose('hollyrosa.templates.vodb_group_booking_overview')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), has_level('vgroup'), msg=u'fff'))
    def vodb_eat_overview(self, compute_local_sum=False, compute_live=False):
        if compute_live:
            overview_live_o = getBookingOverview(holly_couch, None, None, reduce=False)
        else:
            overview_live_o = list()
        overview_eat_o = getBookingEatOverview(holly_couch, None, None, reduce=False)
        overview_value_map = dict()

        vodb_statuses = [-100, -10, 0, 5, 10, 20, 50]
        used_vgroup_ids = dict()
        for tmp_status in vodb_statuses:
            used_vgroup_ids[tmp_status] = dict()

        for row in list(overview_live_o) + list(overview_eat_o):
            tmp_status = row.key[2]
            tmp_id = row.id
            if not used_vgroup_ids[tmp_status].has_key(tmp_id):
                used_vgroup_ids[tmp_status][tmp_id] = holly_couch[tmp_id]


            overview_value_map['%s:%s:%s:%s' % (row.id, row.key[0], row.key[1], row.key[3])] = row.value
            if compute_local_sum:
                try:
                    overview_value_map['%s:%s:%s:%s' % (row.id, row.key[0], row.key[1], 'SUM')] = overview_value_map.get('%s:%s:%s:%s' % (row.id, row.key[0], row.key[1], 'SUM'),0)+int(row.value)
                except ValueError:
                    pass
                except TypeError:
                    pass

        used_dates, used_times = self.compute_used_dates_and_times(list(overview_live_o) + list(overview_eat_o))

        status_level_overview_o = getBookingOverview(holly_couch, None, None, reduce=True)
        status_level_eat_overview = getBookingEatOverview(holly_couch, None, None, reduce=True)
        #...copy paste!
        for row in list(status_level_overview_o) + list(status_level_eat_overview):
            tmp_status = row.key[2]
            tmp_id = 'sum.%d' % tmp_status
            log.debug('tmp_id='+str(tmp_id))
            if not used_vgroup_ids[tmp_status].has_key(tmp_id):
                tmp_o = DataContainer()
                tmp_o.id=tmp_id
                tmp_o.name='summa for %d' % tmp_status
                tmp_o.boknr=''
                tmp_o.to_date=''
                tmp_o.vodbstatus = tmp_status
                tmp_o.from_date = '3000-00-00'

                used_vgroup_ids[tmp_status][tmp_id] = tmp_o


            overview_value_map['%s:%s:%s:%s' % (tmp_id, row.key[0], row.key[1], row.key[3])] = row.value
            if compute_local_sum:
                try:
                    overview_value_map['%s:%s:%s:%s' % (tmp_id, row.key[0], row.key[1], 'SUM')] = overview_value_map.get('%s:%s:%s:%s' % (tmp_id, row.key[0], row.key[1], 'SUM'),0)+int(row.value)
                except ValueError:
                    pass


        #...build a list of dates, starting with headers 'status' and 'vgroup'
        if compute_live:
            times = vodb_live_times + vodb_eat_times
        else:
            times = vodb_eat_times

        header_block = [(t,1) for t in times]
        header_block_len = len(header_block)
        dates = used_dates.keys()
        dates.sort()
        header_dates = [(h, header_block_len) for h in dates]

        #...check if any date is missing
        #...add header to dates
        vgroup_header = [('status',1), ('group',1),('date',1),('opt',1)]
        header_dates = vgroup_header + header_dates

        header_times = used_times.keys()

        #...cheat.
        header_times = [('',1)] * len(vgroup_header) + header_block * len(used_dates.keys())
        date_colspan = len(header_block)

        if compute_local_sum:
            row_choices = vodb_live_times_options + ['SUM']
        else:
            row_choices = vodb_live_times_options
        row_span = len(row_choices)


        #..........................................................

        #...Each vgroup can be represented as
        #   [(status,4), (name,4), (refnr,4), (opt1,1) ]  + fm/inne + em/inne + kvall/inne + fru/inne + lu/inne + midd/inne + kvall/inne * dates
        vgroups = []

        for tmp_status in vodb_statuses:
            tmp_used_vgroups = used_vgroup_ids[tmp_status].values()
            tmp_used_vgroups.sort(self.fnCmpSortOnFromDate)
            for tmp_vgroup in tmp_used_vgroups:
                rowspan = len(row_choices)
                for tmp_opt in row_choices:
                    date_opts = []
                    for d in dates:
                        for t in times:
                            if tmp_opt not in ['fm','em','evening']:
                                if t == 'daytrip':
                                    t = 'own'
                            date_opts.append('%s:%s:%s:%s' % (tmp_vgroup.id, d, t, tmp_opt))
                    vgroups.append(  (tmp_vgroup, tmp_opt, date_opts, rowspan )  )

                    if rowspan > 1:
                        rowspan=0


        return dict(header_dates=header_dates, header_times=header_times, row_choices=row_choices, vgroup_opts=vgroups, values=overview_value_map)


    def fn_cmp_vgroups_on_date(self, a, b):
        return cmp(a['from_date'], b['from_date'])


    def getVisitingGroupIdsOfViewSet(self, rows):
        vgroup_ids = dict()
        for row in rows:
            vgroup_ids[row.id] = True
        return vgroup_ids


    def makeSummaryVGroups(self, a_options, a_vodb_status_map):
        summary_vgroups = dict()
        for live_option in a_options:
            for vodb_status, vodb_status_name in a_vodb_status_map.items():
                try:
                    summary_live_option_vgroups = summary_vgroups[live_option]
                except KeyError:
                    summary_vgroups[live_option] = dict()
                    summary_live_option_vgroups = summary_vgroups[live_option]
                summary_live_option_vgroups[vodb_status] = DataContainer(id='summary_%s_%d' % (live_option, vodb_status), name=vodb_status_name, vodbstatus=vodb_status, from_date='', to_date='', vodb_live_computed=list(), has_values=False, all_values_zero=True)
        return summary_vgroups


    def computeDateRangeOfSummaryVGroup(self, a_summary_vgroups, a_vodb_live_times_options, a_vodb_status_map):
        """
        now that we have populated the dict-dict, we need to compute the date-range.
        """
        for live_option in a_vodb_live_times_options:
            for vodb_status, vodb_status_name in a_vodb_status_map.items():
                summary_live_option_vgroups = a_summary_vgroups[live_option]
                tmp_summary_group = summary_live_option_vgroups[vodb_status]
                if not tmp_summary_group.has_values:
                    formated_dates = []
                else:
                    formated_dates = dateRange(tmp_summary_group['from_date'], tmp_summary_group['to_date'], format='%Y-%m-%d')
                tmp_summary_group.date_range = formated_dates


    def computeLiveSummaries(self, a_live_summaries_rows, a_summary_vgroups):
        """iterating through reduced result set should give the data we need. """
        for live_computed_summary in a_live_summaries_rows:
            tmp_date = live_computed_summary.key[0]
            tmp_time = live_computed_summary.key[1]
            tmp_status = live_computed_summary.key[2]
            tmp_option = live_computed_summary.key[3]
            tmp_value = live_computed_summary.value

            #...
            summary_vgroup = a_summary_vgroups[tmp_option][tmp_status]
            if summary_vgroup.from_date > tmp_date or summary_vgroup.from_date=='':
                summary_vgroup.from_date = tmp_date
                summary_vgroup.has_values = True
            if summary_vgroup.to_date < tmp_date or summary_vgroup.to_date=='':
                summary_vgroup.to_date = tmp_date
                summary_vgroup.has_values = True

            #...append data to the vodb_live_computed list assuming all data in order this should work BUT we might get a hole in our data set (not good)
            try:
                tmp_live_summary_dict = summary_vgroup['live_summary']
            except:
                summary_vgroup.live_summary = dict()
                tmp_live_summary_dict = summary_vgroup['live_summary']


            tmp_live_summary_dict[tmp_date+':'+tmp_time] = tmp_value
            if tmp_value != '0' and tmp_value != 0:
                summary_vgroup.all_values_zero = False

    def getCompKey(self, a_vodb_status, a_live_row):
        return "%s:%s:%s" % (a_vodb_status, a_live_row['date'], a_live_row['time'])


    @expose('hollyrosa.templates.vodb_group_booking_overview2')
    @require(Any(has_level('pl'), has_level('staff'), has_level('view'), has_level('vgroup'), msg=u'fff'))
    def vodb_booking_overview(self, compute_local_sum=False, compute_live=False):
        # the aim at first is to start draw grid / sheet using div tags instead of a table.
        overview_live_o = getBookingOverview(holly_couch, None, None, reduce=False)
        used_dates, used_times = self.compute_used_dates_and_times(overview_live_o)
        used_dates_keys = used_dates.keys()
        used_dates_keys.sort()
        header_dates = used_dates_keys

        # try and extend dates
        min_date = header_dates[0]
        max_date = header_dates[len(header_dates)-1]
        header_dates = dateRange(min_date, max_date, format='%Y-%m-%d')

        header_times = vodb_live_times

        #...computing the vgroups we are looking for
        vgroup_ids = self.getVisitingGroupIdsOfViewSet(overview_live_o)

        #...create booking for all summary groups
        summary_vgroups = self.makeSummaryVGroups(vodb_live_times_options, vodb_status_map)

        #...iterating through reduced result set should give the data we need
        live_summaries_rows = getBookingOverview(holly_couch, None, None, reduce=True)
        self.computeLiveSummaries(live_summaries_rows, summary_vgroups)

        #...now that we have populated the dict-dict, we need to compute the date-range
        self.computeDateRangeOfSummaryVGroup(summary_vgroups, vodb_live_times_options, vodb_status_map)

        vgroups = list()
        for tmp_id in vgroup_ids.keys():
            tmp_vgroup = holly_couch[tmp_id]
            tmp_vgroup.all_values_zero = dict(indoor=True, outdoor=True, daytrip=True)
            formated_dates = dateRange(tmp_vgroup['from_date'], tmp_vgroup['to_date'], format='%Y-%m-%d')
            tmp_vgroup['date_range'] = formated_dates

            live_computed_by_date = dict()
            for tmp_live_row in tmp_vgroup['vodb_live_computed']:
                for k in vodb_live_times_options:
                    tmp_comp_key = self.getCompKey(k, tmp_live_row)
                    tmp_value = tmp_live_row[k]
                    live_computed_by_date[tmp_comp_key] = tmp_value

                    if tmp_value != '0' and tmp_value != 0:
                        tmp_vgroup.all_values_zero[k] = False

            tmp_vgroup['live_computed_by_date'] =  live_computed_by_date
            vgroups.append(tmp_vgroup)

        vgroups.sort(self.fn_cmp_vgroups_on_date)

        return dict(header_dates=header_dates, header_times=header_times, vgroups=vgroups, bokn_status_map=bokn_status_map, vodb_status_map=vodb_status_map, summary_vgroups=summary_vgroups)


    @expose()
    @validate(validators={'visiting_group_id':validators.UnicodeString(not_empty=True), 'live':validators.UnicodeString(not_empty=True), 'change_schema':validators.UnicodeString()})
    @require(Any(has_level('pl'), has_level('staff'), msg='Only staff members may set up vodb calculation schemas'))
    def create_calculation_schema(self,  visiting_group_id=None,  live='outdoor',  change_schema='live'):
        ensurePostRequest(request, __name__)
        # todo: accessor function making sure the type really is visiting_group
        visiting_group_o = holly_couch[visiting_group_id]
        visiting_group_properties = visiting_group_o['visiting_group_properties']

        time_row_schema = []
        is_changing_live_sheet = False
        is_changing_eat_sheet = False

        if change_schema == 'live':
            time_row_schema = ['fm', 'em', 'evening']
            is_changing_live_sheet = True
        elif change_schema == 'eat': # this one is more tricky since we dont want to have arrival and departure data set every day.
            time_row_schema = ['breakfast', 'lunch', 'lunch_arrive', 'lunch_depart',  'dinner']
            is_changing_eat_sheet = True


        # try create a live sheet for indoor living for the whole of the groups stay....fm em kvall
        # then try att use only properties that is within the stated range.

        from_date = visiting_group_o['from_date']
        to_date = visiting_group_o['to_date']
        rows=[]
        new_live_sheet = dict(identifier='rid',  items=rows)
        for tmp_date in self.dateGen(from_date, to_date):
            i=0
            for t in time_row_schema:
                i += 1
                #...figure out properties in range.
                prop_str_list = []
                for tmp_prop in visiting_group_properties.values():
                    if tmp_prop['from_date'] <= tmp_date and tmp_prop['to_date'] >= tmp_date:
                        prop_str_list.append('$'+tmp_prop['property'])
                tmp_r = dict(date=tmp_date,  time=t,  indoor=0,  outdoor=0,  daytrip=0,  rid=tmp_date+'_'+str(i))

                if t not in ['lunch_arrive', 'lunch_depart']:
                    tmp_r[live] = '+'.join(prop_str_list)
                else:
                    tmp_r[live] = 0
                rows.append(tmp_r)

        rows[0][live] = 0
        rows[-2][live] = 0
        rows[-1][live] = 0

        if is_changing_eat_sheet:
            visiting_group_o['vodb_eat_sheet'] = new_live_sheet
        elif is_changing_live_sheet:
            visiting_group_o['vodb_live_sheet'] = new_live_sheet


        #if eat_sheet != None:
        #   visiting_group_o['vodb_eat_sheet'] = json.loads(eat_sheet)

        #if live_sheet != None:
        #   visiting_group_o['vodb_live_sheet'] = json.loads(live_sheet)

        vodb_tag_times_tags = computeAllUsedVisitingGroupsTagsForTagSheet(visiting_group_o['tags'], visiting_group_o['vodb_tag_sheet']['items'])

        updateVisitingGroupComputedSheets(visiting_group_o, visiting_group_properties, sheet_map=dict(vodb_eat_sheet=vodb_eat_times_options, vodb_live_sheet=vodb_live_times_options, vodb_tag_sheet=vodb_tag_times_tags))

        holly_couch[visiting_group_id] = visiting_group_o
        raise redirect(request.referrer)
