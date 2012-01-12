### -*- coding: utf-8 -*-
##"""
##Copyright 2010, 2011, 2012 Martin Eliasson
##
##This file is part of Hollyrosa
##
##Hollyrosa is free software: you can redistribute it and/or modify
##it under the terms of the GNU Affero General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##Hollyrosa is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Affero General Public License for more details.
##
##You should have received a copy of the GNU Affero General Public License
##along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.
##
##""" 
##
##from sqlalchemy import *
##from sqlalchemy.orm import mapper, relation,  backref
##from sqlalchemy import Table, ForeignKey, Column
##from sqlalchemy.types import Integer, Unicode,  Numeric,  Boolean
##
##from hollyrosa.model import DeclarativeBase, metadata, DBSession
##from hollyrosa.model.auth import User
##
##    
##__all__=['DaySchema',  'BookingDay', 'SlotRow', 'Booking', 'VisitingGroup', 'BookingHistory', 'Activity', 'ActivityGroup',  'SlotRowPosition',  'SlotRowPositionState',  'VistingGroupProperty', 'VisitingGroupTags', 'VisitingGroupTag']
##    
##    
##class DaySchema(DeclarativeBase):
##    __tablename__ = 'day_schema'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##
##    id = Column(Integer, primary_key=True)
##    title = Column(Unicode(255), nullable=False)
##    
##    
##    
##class BookingDay(DeclarativeBase):
##    __tablename__ = 'booking_day'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    date = Column(Date,  nullable=False)
##    note = Column(Unicode(8192),  nullable=True) # original 512 was too small
##    num_program_crew_members = Column(Integer)
##    num_fladan_crew_members = Column(Integer)
##    
##    day_schema_id = Column(Integer, ForeignKey('day_schema.id'))
##    day_schema = relation(DaySchema, backref=backref('booking_day', order_by=id))
##
##
##class ActivityGroup(DeclarativeBase):
##    __tablename__ = 'activity_group'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    title = Column(Unicode(128), nullable=False)
##    description = Column(Unicode(4096), nullable=False)
##    
##    
##class Activity(DeclarativeBase):
##    __tablename__ = 'activity'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    bg_color = Column(Unicode(64), nullable=True)
##    guides_per_slot = Column(Integer)
##    guides_per_day = Column(Integer)
##    equipment_needed = Column(Boolean)
##    education_needed = Column(Boolean)
##    certificate_needed = Column(Boolean)
##    tags = Column(Unicode(255), nullable=True)
##    title = Column(Unicode(128), nullable=False)
##    description = Column(Unicode(4096), nullable=False)
##    external_link = Column(Unicode(4096), nullable=True)
##    internal_link = Column(Unicode(4096), nullable=True)
##    print_on_demand_link = Column(Unicode(4096), nullable=True)
##    capacity = Column(Integer)
##    default_booking_state = Column(Integer,  nullable=False) 
##    
##    #...there can be many activities per activity group
##    activity_group_id = Column(Integer, ForeignKey('activity_group.id'))
##    activity_group = relation(ActivityGroup, backref=backref('activity', order_by=id))
##        
##    #gps_lat = Column(Numeric, precision=8, scale=5, nullable=True)
##    #gps_long = Column(Numeric, precision=8, scale=5,  nullable=True)
##    
##    gps_lat = Column(Numeric, nullable=True)
##    gps_long = Column(Numeric, nullable=True)
##    
##    
##    
##class SlotRow(DeclarativeBase):
##    __tablename__ = 'slot_row'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    slot_row_schema =  Column(String(255),  nullable=False)
##    zorder = Column(Integer)
##    
##    activity_id = Column(Integer, ForeignKey('activity.id'))
##    activity = relation(Activity, backref=backref('slot_row', order_by=id))
##
##
##class SlotRowPosition(DeclarativeBase):
##    __tablename__ = 'slot_row_position'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##
##    time_from = Column(Time,  nullable=False)
##    time_to = Column(Time,  nullable=False)
##    duration = Column(Integer,  nullable=False) # compute and cache for speed. This is only to be used for computing width of fields
##
##    slot_row_id = Column(Integer, ForeignKey('slot_row.id'))
##    slot_row = relation(SlotRow, backref=backref('slot_row_position', order_by=time_from))
##    
##    
##class SlotRowPositionState(DeclarativeBase):
##    __tablename__ = 'slot_row_position_state'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    level = Column(Integer,  nullable=False)
##    slot_row_position_id = Column(Integer, ForeignKey('slot_row_position.id'))
##    slot_row_position = relation(SlotRowPosition, backref=backref('slot_row_position_state', order_by=id))
##
##    booking_day_id = Column(Integer, ForeignKey('booking_day.id'))
##    booking_day = relation(BookingDay, backref=backref('slot_row_position_state', order_by=id))
##
###
###...brand new table(s) for association table
###class VisitingGroupTags(DeclarativeBase):
###    __tablename__ = 'visiting_group_tags'
###    __table_args__ = {'mysql_engine':'InnoDB'}
###    visiting_group_tag_id = Column(Integer, ForeignKey('visiting_group_tag.id'))  
###    visiting_group_id = Column(Integer, ForeignKey('visiting_group.id'))
##
##
##    
##class VisitingGroup(DeclarativeBase):
##    __tablename__ = 'visiting_group'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##
##    name = Column(Unicode(512),  nullable=False)
##    fromdate = Column(Date,  nullable=False) 
##    todate = Column(Date,  nullable=False)
##    info = Column(Unicode(8192),  nullable=True)
##    contact_person = Column(Unicode(255),  nullable=True)
##    contact_person_phone = Column(Unicode(512),  nullable=True)
##    contact_person_email = Column(Unicode(512),  nullable=True)
##    
##    #...GCal implementation
##    calendar_id = Column(Unicode(128),  nullable=True)
##
##    #...2011 additions
##    boknr = Column(Unicode(128), nullable=True)
##    boknstatus = Column(Integer, nullable=False)
##    camping_location = Column(Unicode(256), nullable=True)
##
##    # many to many BlogPost<->Keyword
###    tags = relation('VisitingGroupTag', secondary=visiting_group_tags, backref='visiting_groups')
##    
##    
##
### brand new tags table
###class VisitingGroupTag(DeclarativeBase):
###    __tablename__ = 'visiting_group_tag'
###    __table_args__ = {'mysql_engine':'InnoDB'}
###    
###    id = Column(Integer, primary_key = True) 
###    tag = Column(Unicode(128), nullable=False, unique=True)
##    
##    
##class Booking(DeclarativeBase):
##    __tablename__ = 'booking'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    content = Column(Unicode(512),  nullable=True)
##    
##    visiting_group_name = Column(Unicode(512),  nullable=True)
##    
##    #...the following three fields are usefull when booking in springtime
##    
##    requested_date = Column(Date)
##    valid_from = Column(Date)
##    valid_to = Column(Date)
##    
##    booking_state = Column(Integer,  nullable=False)
##    
##    activity_id = Column(Integer, ForeignKey('activity.id'))
##    activity = relation(Activity, backref=backref('booking', order_by=id))
##    
##       
##    
##    last_changed_by_id = Column(Integer, ForeignKey('tg_user.user_id'))
##    #last_changed_by = relation(User,  backref=backref('slot', order_by=id))
##    
##    approved_by_id = Column(Integer, ForeignKey('tg_user.user_id'))
##    #approved_by = relation(User,  backref=backref('slot', order_by=id))
##    
##    visiting_group_id = Column(Integer, ForeignKey('visiting_group.id'))
##    visiting_group = relation(VisitingGroup,  backref=backref('book', order_by=id))
## 
##    slot_row_position_id = Column(Integer, ForeignKey('slot_row_position.id'))
##    slot_row_position = relation(SlotRowPosition, backref=backref('booking', order_by=id))
##
##    booking_day_id = Column(Integer, ForeignKey('booking_day.id'))
##    booking_day = relation(BookingDay, backref=backref('booking', order_by=id))
##    
##    #...misc (time for Trapper is main usage of this field)
##    misc = Column(Unicode(128),  nullable=True)
##    
##    #...gcal integration
##    gcal_id = Column(Unicode(128),  nullable=True)
##    gcal_is_dirty = Column(Boolean,  nullable=True)
##    
##    #...cache content, used with visiting group properties
##    cache_content = Column(Unicode(1024),  nullable=True)
##    
##    extra = Column(Unicode(128),  nullable=True) # REMOVE IF NOT NEEDED, THIS IS A SPARE FOR DEVELOPMENT REASONS
##    
##    
##    
##class BookingHistory(DeclarativeBase):
##    __tablename__ = 'booking_history'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    change_op = Column(Integer,  nullable=False)
##    booking_content = Column(Unicode(512),  nullable=True)
##    change = Column(Unicode(512), nullable=True)
##    changed_by = Column(Unicode(255),  nullable=False)
##    timestamp = Column(DateTime,  nullable=False)
##    
##    
##    booking_id = Column(Integer, ForeignKey('booking.id'))
##    booking = relation(Booking, backref=backref('booking_history', order_by=id))
##    
##    booking_day_id = Column(Integer, ForeignKey('booking_day.id'))
##    booking_day = relation(BookingDay, backref=backref('booking_history', order_by=id))
##    
##    
##class VistingGroupProperty(DeclarativeBase):
##    __tablename__ = 'visiting_group_property'
##    __table_args__ = {'mysql_engine':'InnoDB'}
##    
##    id = Column(Integer, primary_key=True)
##    visiting_group_id = Column(Integer, ForeignKey('visiting_group.id'))
##    visiting_group = relation(VisitingGroup,  backref=backref('visiting_group_property', order_by=id))
##    
##    property = Column(Unicode(64),  nullable=False)
##    value = Column(Unicode(64),  nullable=False)
##    unit = Column(Unicode(64),  nullable=True)
##    description = Column(Unicode(512),  nullable=True)
##    fromdate = Column(Date,  nullable=True) 
##    todate = Column(Date,  nullable=True)
