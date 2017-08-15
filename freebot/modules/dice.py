#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import random
import re

description = "!roll xdy - roll x number of y-sided dice"

prefix = "dice_"

event_type = 'PRIVMSG'

_cmd = ["!roll"]


max_sides = 100
max_dice = 25
max_rolls = 5

def init(db):
    pass

def remove(db):
    pass


def run(bot, event, db):
    patt = re.compile('^\d+d\d+$')
    m = event.message.lower()
    if m.startswith('!roll'):
        m = m.split()
        if len(m) < 2:
            return
        if len(m) > max_rolls+1:
            m = m[:max_rolls+1]
            bot.bot_reply(event, "Only rolling first {} rolls".format(max_rolls))
        for roll in m[1:]:
            if patt.search(roll) is None:
                continue
            xy = roll.split('d')
            x = int(xy[0])
            y = int(xy[1])
            if x > max_dice or y > max_sides:
                continue
            results = [random.randint(1,y) for i in range(x)]
            total = sum(results)
            bot.bot_reply(event, roll+': '+repr(results)+'='+str(total), False)