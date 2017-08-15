import re

## Description stored in db.bot_modules
description = "Hugs the target"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "hug_"

## Event type handled by this module
event_type = "PRIVMSG"

_cmd = ["!hug"]

## Additional global vars
#H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
#G_URL = 'http://www.google.com/search?q={}&btnI'

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    m = event.message.lower()
    if m.startswith('!hug '):
        cmd = m.split()
        target = cmd[1]
        chan = event.target
        
        # convert users to lowercase to make non case-sensitive
        user_list = [u for u in list(bot.channels[chan].user_list)]
        users_lower = [u.lower() for u in user_list]
        try:
            user_idx = users_lower.index(target)
        except ValueError:
           user_idx = None        

        if target == bot.nickname.lower():
            bot.send_action(chan, 'hugs himself')
            bot.bot_log('CTCP_ACTION', bot.nickname, chan, 'hugs himself')
        elif target in users_lower:
            hug_msg = 'hugs ' + user_list[user_idx]
            bot.send_action(chan, hug_msg)
            bot.bot_log('CTCP_ACTION', bot.nickname, chan, hug_msg)
        else:
            hug_msg = "looks around, but can't find " + target
            bot.send_action(chan, hug_msg)
            bot.bot_log('CTCP_ACTTION', bot.nickname, chan, hug_msg)
            
