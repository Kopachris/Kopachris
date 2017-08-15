#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils

## Description stored in db.bot_modules
description = "!help - Displays information about the bot's owner"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "o_"

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
    
    if event.message.lower().startswith('!help') or event.message.lower() == '!h':
        event.target = bot.nickname
        bot.bot_reply(event, "I am owned and operated by Kopachris/groot.")
        bot.bot_reply(event, "Installed modules:")
        mods = db(db.bot_modules.mod_enabled == True).select()
        bot.bot_reply(event, ', '.join([m.name for m in mods]))
