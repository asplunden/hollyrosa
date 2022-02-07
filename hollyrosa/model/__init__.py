# -*- coding: utf-8 -*-
"""The application's model objects"""

#from zope.sqlalchemy import ZopeTransactionExtension
#from sqlalchemy.orm import scoped_session, sessionmaker
import threading
import couchdb
import tg


#from sqlalchemy import MetaData
###from sqlalchemy.ext.declarative import declarative_base

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
##maker = sessionmaker(autoflush=True, autocommit=False, extension=ZopeTransactionExtension())
##DBSession = scoped_session(maker)

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

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    pass

def getHollyCouch(): # TODO this is like our session object we can import everywhere...
    """
    Always use this to get access to threadlocal couchdb, should give improved performance and thread safety if needed over holly implementation
    """
    threadLocal = threading.local()
    l_holly_couch_db = getattr(threadLocal, 'holly_couch_db', None)
    if l_holly_couch_db is None:
        l_holly_couch_db = _initDB_ng()
        threadLocal.holly_couch_db = l_holly_couch_db
    return l_holly_couch_db


def _initDB_ng():
    """
    initialize a database connection
    """
    db_url = tg.config.get('couch.db_url', 'http://localhost:5989')
    db_name = tg.config.get('couch.database', 'hollyrosa1')

    db_login = tg.config.get('couch.login', '')
    db_password = tg.config.get('couch.password', '')

    threadLocal = threading.local()
    threadLocal.couch_server = couchdb.Server(url=db_url)
    if len(db_login) > 0:
        threadLocal.couch_server.resource.credentials = (db_login, db_password)

    try:
        threadLocal.holly_rosa_db = threadLocal.couch_server[db_name]
    except couchdb.ResourceNotFound as e:
        threadLocal.holly_rosa_db = couch_server.create(db_name)
    return threadLocal.holly_rosa_db

from hollyrosa.model.booking_couch import genUID
