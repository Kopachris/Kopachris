#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import urllib2
import json
#from bs4 import BeautifulSoup

## Description stored in db.bot_modules
# returned by !help command
description = "!command - Does a thing"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "temp_"

## Event type handled by this module
# multiple event types not supported yet
event_type = "PRIVMSG"

## Additional global vars go here

# a lot of websites block specific user-agent strings associated with bots
# use this to avoid that if your module retrieves webpages
#H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
MLFW_URL = 'http://mylittlefacewhen.com/api/v3/face/?order_by=random&limit=1&offset=1&format=json&accepted=true'

def init(db):
    # called when module is uploaded/enabled
    # create any tables or add default values to db.bot_vars
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
    s = m.split()
    
    if s[0] in ('mfw', 'mlfw', 'mrw'):
        # general form for identifying a command
        api_res = json.loads(urllib2.urlopen(MLFW_URL).read())
        # alternate, instead of directly linking the image file:
        # reaction_url = 'http://mylittlefacewhen.com/face/' + str(api_res['objects'][0]['id'])
        # reaction_url = 'http://mylittlefacewhen.com' + api_res['objects'][0]['image']
        reaction_url = 'http://mlfw.info/f/' + str(api_res['objects'][0]['id'])
        bot.bot_reply(event, reaction_url, False)
