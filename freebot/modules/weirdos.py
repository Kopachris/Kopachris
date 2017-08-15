#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
#import urllib2

## Description stored in db.bot_modules
description = ""

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "weird_"

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
    
    if event.message.lower().startswith('!weird'):
        bot.bot_reply(event, "You are all weirdos!  http://youtu.be/PB-wmOYelnM", False)
