#!/usr/bin/env python
# coding: utf8
#from gluon import *
from gluon.tools import Auth
from gluon.storage import Storage
import bot_utils

## Description stored in db.bot_modules
description = "table"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "tbl_"

## Event type handled by this module
event_type = "PRIVMSG"

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    s = event.message.split()

    if event.message.lower().startswith('!table'):
        bot.bot_reply(event, u"(╯°□°）╯︵ ┻━┻", False)