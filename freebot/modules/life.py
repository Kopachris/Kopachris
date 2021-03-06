import re

## Description stored in db.bot_modules
description = "The answer"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "42_"

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
    m = event.message.lower()
    regex = re.compile('[!"#$%&\'()*+,./:;<=>?@\\^_`{|}~-]')
    mr = regex.sub('', m).split()
    ms = set(mr)
    q = {'what', 'the', 'life', 'universe', 'everything'}
    q2 = {'meaning', 'question', 'answer'}
    if q < ms and len(ms.intersection(q2)) == 1:
        bot.bot_reply(event, "Everyone knows it's 42, duh!")
