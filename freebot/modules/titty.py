#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
#import urllib2

## Description stored in db.bot_modules
description = "titty croissant"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "tt_"

## Event type handled by this module
event_type = "PRIVMSG"

## Additional global vars
#H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
#G_URL = 'http://www.google.com/search?q={}&btnI'

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    m = event.message.lower()
    
    if m.count('hon') >= 2 and ('titty' not in m and 'croissant' not in m):
        bot.bot_reply(event, 'hon hon hon titty croissant', False)
