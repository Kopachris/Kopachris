#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import random

## Description stored in db.bot_modules
description = "botsnack"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "snack_"

## Event type handled by this module
event_type = "PRIVMSG"

def init(db):
    bot_utils.set_item('snack_choices', "['Yipee!', 'Oh, I say!']", db)
    bot_utils.set_item('snack_slap', "Is Alfred Pennyworth going to have to slap a Wayne?", db)


def remove(db):
    """
    Remove module from database,
    including any variable that may have been added
    """
    db(db.bot_vars.tbl_k == 'snack_choices').delete()


def run(bot, event, db):
    this_mod = db(db.bot_modules.name == "botsnack").select().first()
    pre = this_mod.vars_pre
    if event.message.lower().startswith('!botsnack'):
        s = bot_utils.get_item('snack_choices', db)
        choices = eval(str(s)) or ['Yipee!', 'Oh, I say!']
        bot.bot_reply(event, random.choice(choices), False)
    elif event.message.lower().startswith('!botslap'):
        bot.bot_reply(event, bot_utils.get_item(pre+'slap', db) or "Is Alfred Pennyworth going to have to slap a Wayne?", False)
