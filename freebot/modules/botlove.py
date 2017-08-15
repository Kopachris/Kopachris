#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils

## Description stored in db.bot_modules
description = "botlove"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "love_"

## Event type handled by this module
event_type = "PRIVMSG"

def init(db):
    s = db(db.bot_vars.tbl_k == 'love_name')
    if not len(s.select()):
        db.bot_vars.insert(tbl_k='snack_choices', v="BotenAnna")


def remove(db):
    """
    Remove module from database,
    including any variable that may have been added
    """
    db(db.bot_vars.tbl_k == 'love_name').delete()


def run(bot, event, db):
    if event.message.lower().startswith('!botlove') and event.target.startswith('#'):
        bot.send_action(event.target, 'hugs ' + bot_utils.get_item('love_name', db))