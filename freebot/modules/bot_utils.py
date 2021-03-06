#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Begin license block ##

##           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
##                   Version 2, December 2004
##
## Copyright (C) 2013 Christopher Koch <kopachris@gmail.com>
##
## Everyone is permitted to copy and distribute verbatim or modified
## copies of this license document, and changing it is allowed as long
## as the name is changed.
##
##           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
##  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
##
##  0. You just DO WHAT THE FUCK YOU WANT TO.

## End license block ##

from gluon import *


def store_dict(kv, db, tbl='bot_vars'):
    """
    Define a table of kv pairs and store a Python dict in it.
    """
    for k, v in kv.items():
        set_item(k, v, db, tbl)


def get_item(k, db, tbl='bot_vars'):
    """
    Retrieve an item from a kv pair table
    """
    try:
        tbl = db[tbl]
        r = db(tbl.tbl_k == k).select().first()
        if r is not None:
            return r.v
        else:
            return None
    except:
        return None


def set_item(k, v, db, tbl='bot_vars'):
    try:
        tbl = db.define_table(tbl,
                              Field('tbl_k', 'string', unique=True, length=32),
                              Field('v', 'string', length=512),
                              )
    except SyntaxError:
        ## table already defined in this db
        tbl = db[tbl]
    r = db(tbl.tbl_k == k)
    if not r.isempty():
        r.update(v=v)
    else:
        tbl.insert(tbl_k=k, v=v)
