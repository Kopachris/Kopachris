#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import re
from multiprocessing import Process, Pipe
from time import sleep, time

## Description stored in db.bot_modules
# returned by !help command
description = "regex substitutes the previous message"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "re_"

## Event type handled by this module
event_type = "PRIVMSG"

## Additional global vars go here

# a lot of websites block specific user-agent strings associated with bots
# use this to avoid that if your module retrieves webpages
#H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

def init(db):
    # called when module is uploaded
    pass


def remove(db):
    # called when module is disabled
    pass


def mp_dosub(pipe, reg, sub, msg, maxmatch=None):
    if maxmatch:
        new_m = re.sub(reg, sub, msg, maxmatch)
    else:
        new_m = re.sub(reg, sub, msg)
        
    if new_m == msg:
        pipe.send(False)
    else:
        pipe.send(new_m)
    pipe.close()


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    m_items = prefix + "items"
    bot_nick = bot.nickname
    
    m = event.message.split('/')
    
    if m[0] == 's' and (len(m) == 3 or len(m) == 4):
        reg = m[1]
        sub = m[2]
        all_m = db(((db.event_log.event_type == 'PRIVMSG') | (db.event_log.event_type == 'CTCP_ACTION')) & (db.event_log.event_target == event.target)).select(db.event_log.ALL, orderby=~db.event_log.id, limitby=(1,47))
        #prev_m = all_m.records[-2:-15:-1]
        for msg in all_m:
            #msg = old_m.event_log
            if len(m) == 4 and m[3] == 'g':
                maxmatch = None
            else:
                maxmatch = 1

            par_pipe, ch_pipe = Pipe()
            mp = Process(target=mp_dosub, args=(ch_pipe, reg, sub, msg.event_message, maxmatch))
            new_m = None
            start_time = time()
            mp.start()
            i = 0
            while time() < start_time + 5:
                i += 1
                if par_pipe.poll():
                    new_m = par_pipe.recv()
                    break
                else:
                    sleep(0.05)
                    
            #bot.bot_reply(event, "{} loops".format(i))

            if mp.is_alive():
                mp.terminate()

            if new_m:
                bot.bot_reply(event, '<{}> {}'.format(msg.event_source, new_m), False)
                return
            elif new_m is None:
                # timed out!
                #bot.bot_reply(event, "Timed out, {} loops".format(i))
                return
