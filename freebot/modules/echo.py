#!/usr/bin/env python
# coding: utf8
from gluon import *

description = "Just echo whatever is directed towards the bot"
prefix = ''
event_type = 'PRIVMSG'

def init(db):
    """
    Initialize database for module
    """
    pass


def remove(db):
    """
    Remove module from database
    """
    pass


def run(bot, event, db):
    if event.target == bot.nickname or bot.nickname.lower() in event.message.lower():
        bot.bot_reply(event, event.message, False)
