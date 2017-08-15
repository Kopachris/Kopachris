#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
#import urllib2
#from bs4 import BeautifulSoup
from datetime import datetime

## Description stored in db.bot_modules
# returned by !help command
description = "!ping - Pongs"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "temp_"

## Event type handled by this module
event_type = "PRIVMSG"

## Additional global vars go here

# a lot of websites block specific user-agent strings associated with bots
# use this to avoid that if your module retrieves webpages
H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

def init(db):
    # called when module is uploaded
    pass


def remove(db):
    # called when module is disabled
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    m_items = prefix + "items"
    bot_nick = bot.nickname
    
    m = event.message.lower()
    
    if m.startswith('!ping'):
        # general form for identifying a command
        bot.bot_reply(event, datetime.now().strftime('%c') + " pong")