from gluon import *
import bot_utils
import random

## Description stored in db.bot_modules
description = "!8ball <question>"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "8b_"

## Event type handled by this module
event_type = "PRIVMSG"

_cmd = ["!8ball"]

## Additional global vars
QA = {'yes': ('It is certain', 'It is decidedly so', 'Without a doubt',
              'Yes, definitely', 'You may rely on it', 'As I see it, yes',
              'Most likely', 'Outlook good', 'Yes', 'Signs point to yes'),
      'maybe': ('Reply hazy; try again', 'Ask again later',
                'Better not tell you now', 'Cannot predict now',
                'Concentrate and ask again'),
      'no': ('Don\'t count on it', 'My reply is no', 'My sources say no',
             'Outlook not so good', 'Very doubtful')}
# easy way of changing probability of getting maybe or yes/no, use random.choice()
prob_true = 1
prob_false = 3
# prob_true = 2; prob_false = 3; means 2/5 chance of getting true, 3/5 chance of getting false
PROB = [False for i in range(prob_false)] + [True for i in range(prob_true)]

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    m_items = prefix + "items"
    bot_nick = bot.nickname
    
    m = event.message.lower()
    
    if m.startswith('!8ball'):
        # First decide whether to give maybe or yes/no
        # if maybe, return random choice of QA['maybe']
        # else convert string to lowercase, add up ascii values of each character,
        # and mod 2 to determine whether yes or no
        maybe = random.choice(PROB)
        if maybe:
            bot.bot_reply(event, random.choice(QA['maybe']))
        else:
            s = m.split('!', 1)[1][6:].translate(None, '?!. :;,\'"`@#$%^&*()[]{}\\|/<>')
            count = 0
            for c in s:
                count += ord(c)
            a = count % 2
            # this is calibrated so the question "will I get laid" always comes up 'no'
            # BECAUSE NO ONE ON IRC GETS LAID
            if not a:
                bot.bot_reply(event, random.choice(QA['yes']))
            else:
                bot.bot_reply(event, random.choice(QA['no']))
        return
