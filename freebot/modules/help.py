#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import urllib2

## Description stored in db.bot_modules
description = "!help - Displays descriptions of all enabled modules"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "h_"

## Event type handled by this module
event_type = "PRIVMSG"

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mods = db.bot_modules
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(mods.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    m = event.message.lower()
    s = m.split()
    
    if event.message.lower().startswith('!help') or event.message.lower() == '!h':
        event.target = bot.nickname
        
        if len(s) == 2:
            mod_name = s[1]
            mod = db((mods.name == mod_name) & (mods.mod_enabled == True))
            if mod.isempty():
                bot.bot_reply(event, "That module is either not installed or not enabled.")
                return
            else:
                mod_desc = mod.select().first().description
                bot.bot_reply(event, mod_desc)
                return
        
        all_mods = db(mods.mod_enabled == True).select()
        bot.bot_reply(event, "I am owned and operated by Kopachris/groot.")
        bot.bot_reply(event, "List of installed modules (use !help <module name> for more details):")
        bot.bot_reply(event, ', '.join([m.name for m in all_mods]))
