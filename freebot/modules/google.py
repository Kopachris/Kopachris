#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import urllib2
import urllib
import time

## Description stored in db.bot_modules
description = "Google `I'm feeling lucky' search"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "gg_"

## Event type handled by this module
event_type = "PRIVMSG"

_cmd = ["!google"]

## Additional global vars
H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
G_URL = 'http://www.google.com/search?q={}&btnI'

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    if 'sock' in event.source.lower():
        return
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    
    #event.message = event.message.replace('​', '')
    #if event.message.lower().endswith('< quack!') or event.message.lower().endswith('< flap flap!'):
    #    time.sleep(0.5)
    #    bot.bot_reply(event, '.bang', False)
    #    return
    
    if event.message.lower().startswith('!google '):
        q = '+'.join(event.message.split()[1:])
        try:
            req = urllib2.Request(G_URL.format(q), headers=H_HTTP)
            response = urllib2.urlopen(req)
            bot.bot_reply(event, response.geturl())
        except urllib2.HTTPError as e:
            bot.bot_reply(event, "Unable to get result: " + e.msg)
        return
