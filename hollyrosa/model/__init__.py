# -*- coding: utf-8 -*-
"""The application's model objects"""

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
import couchdb
import tg

#from sqlalchemy import MetaData
###from sqlalchemy.ext.declarative import declarative_base

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False, extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
####DeclarativeBase = declarative_base()

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
###metadata = DeclarativeBase.metadata

# If you have multiple databases with overlapping table names, you'll need a
# metadata for each database. Feel free to rename 'metadata2'.
#metadata2 = MetaData()

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
#
######

couch_server = None
holly_couch = None

db_url = tg.config.get('couch.db_url', 'http://localhost:5989')
db_name = tg.config.get('couch.database', 'hollyrosa1')



print db_url,  db_name

couch_server = couchdb.Server(url=db_url)
try:
    holly_couch = couch_server[db_name]
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create(db_name)
        
        
def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    print 'INIT_MODEL'
    DBSession.configure(bind=engine)
    

# Import your model modules here.
###from hollyrosa.model.auth import User, Group, Permission
##from hollyrosa.model.booking import DaySchema, BookingDay, SlotRow, Booking, VisitingGroup, BookingHistory, Activity, ActivityGroup, SlotRowPosition,  SlotRowPositionState

import booking_couch
from booking_couch import genUID

# TODO: refactor 
holly_couch = booking_couch.holly_couch


getAllVisitingGroupsNameAmongBookings = booking_couch.getAllVisitingGroupsNameAmongBookings
getSlotAndActivityIdOfBooking = booking_couch.getSlotAndActivityIdOfBooking
getBookingDayOfDate = booking_couch.getBookingDayOfDate
getAllBookingDays = booking_couch.getAllBookingDays
getBookingDays = booking_couch.getBookingDays
