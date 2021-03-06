#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import gc

## Description stored in db.bot_modules
description = "!gc - display "

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "gc_"

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
    
    if event.source == 'Kopachris':
		if event.message.lower().startswith('!gc'):
			cmd = event.message.lower().split()[1]
			if cmd == 'collect':
				unreachable = gc.collect()
				bot.bot_reply(event, "{} unreachable objects found".format(unreachable))
			elif cmd == 'objects':
				objs = gc.get_objects()
				bot.bot_reply(event, "All tracked objects: {}".format(len(objs)))
			elif cmd == 'counts':
				counts = gc.get_count()
				bot.bot_reply(event, "Current collection counts: {}".format(counts))
			elif cmd == 'garbage':
				garbage = gc.garbage
				bot.bot_reply(event, str(garbage))
			elif cmd == 'all_objects':
				objs = gc.get_objects()
				bot.bot_reply(event, str(objs))
			