#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import urllib2
from datetime import datetime

## Description stored in db.bot_modules
description = "!seen <user> - when was user last seen"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "seen_"

## Event type handled by this module
event_type = "PRIVMSG"

_cmd = ["!seen"]

## Additional global vars


def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    
    event_log = db['event_log']
    if event.message.lower().startswith('!seen') and len(event.message.split()) == 2:
        user = event.message.split()[1]
        userseen = db(event_log.event_source == user).select().last()
        userseen2 = db((event_log.event_message == user) & (event_log.event_type == 'NICK')).select().last()
        if userseen2 is not None and userseen is not None:
            if userseen2.event_time > userseen.event_time:
                bot.bot_reply(event, '{} last seen at {} changing nick from {}'.format(user, userseen2.event_time, userseen2.event_source))
            else:
                if userseen.event_type in ('PRIVMSG', 'CTCP_ACTION'):
                    bot.bot_reply(event, '{} last seen in {} at {}, saying "{}"'.format(user, userseen.event_target, userseen.event_time, userseen.event_message))
                elif userseen.event_type in ('QUIT', 'PART'):
                    bot.bot_reply(event, '{} left at {} with the message "{}"'.format(user, userseen.event_time, userseen.event_message))
                elif userseen.event_type == 'JOIN':
                    bot.bot_reply(event, '{} joined {} at {}'.format(user, userseen.event_target, userseen.event_time))
                elif userseen.event_type == 'NICK':
                    bot.bot_reply(event, '{} last seen at {} changing nick to {}'.format(user, userseen.event_time, userseen.event_message))
        elif userseen is not None:
            if userseen.event_type in ('PRIVMSG', 'CTCP_ACTION'):
                bot.bot_reply(event, '{} last seen in {} at {}, saying "{}"'.format(user, userseen.event_target, userseen.event_time, userseen.event_message))
            elif userseen.event_type in ('QUIT', 'PART'):
                bot.bot_reply(event, '{} left at {} with the message "{}"'.format(user, userseen.event_time, userseen.event_message))
            elif userseen.event_type == 'JOIN':
                bot.bot_reply(event, '{} joined {} at {}'.format(user, userseen.event_target, userseen.event_time))
            elif userseen.event_type == 'NICK':
                bot.bot_reply(event, '{} last seen at {} changing nick to {}'.format(user, userseen.event_time, userseen.event_message))
        elif userseen2 is not None:
            bot.bot_reply(event, '{} last seen at {} changing nick from {}'.format(user, userseen2.event_time, userseen2.event_source))
        else:
            bot.bot_reply(event, "I have never seen {}.".format(user))
