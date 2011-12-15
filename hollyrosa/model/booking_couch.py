# -*- coding: utf-8 -*-

"""Couch db"""

#...ME
import couchdb
from uuid import uuid4

def genUID():
    return uuid4().hex


couch_server = couchdb.Server()
try:
    holly_couch = couch_server['hollyrosa1']
    print 'opened hollyrosa1'
    
except couchdb.ResourceNotFound, e:
    holly_couch = couch_server.create('hollyrosa1')
    
    
    
