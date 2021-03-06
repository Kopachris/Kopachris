#!/usr/bin/env python
# coding: utf8

from gluon import *
import bot_utils
import urllib2
from urllib import quote
from bs4 import BeautifulSoup

description = "Queries Wolfram|Alpha.  Set your Wolfram|Alpha API key by PMing the bot '<prefix>apikey <your-api-key>' or manually setting the wa_apikey variable."

prefix = "wa_"

event_type = "PRIVMSG"

_cmd = ["!wa"]

WA_URL = 'http://api.wolframalpha.com/v2/query?appid=%(apikey)s&input=%(q)s&format=plaintext'
WA_FULL = 'http://www.wolframalpha.com/input/?i=%s'

def init(db):
    bot_utils.set_item(prefix + 'apikey', '', db)


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    k_apikey = prefix + 'apikey'
    apikey = bot_utils.get_item(k_apikey, db)
    
    m = event.message.lower()
    msg = event.message
    s = msg.split()
    
    if m.startswith(k_apikey) and len(s) == 2:
        apikey = s[1]
        bot_utils.set_item(k_apikey, apikey, db)
        bot.bot_reply(event, "Wolfram|Alpha API key set to %s" % apikey)
        return
    
    if m.startswith('!wa '):
        q = quote(' '.join(s[1:]))
        
        if apikey == '':
            bot.bot_reply(event, "Wolfram|Alpha API key not installed. Please let the bot admin know.")
            return
        
        try:
            req = urllib2.Request(WA_URL % locals())
            res = urllib2.urlopen(req)
        except urllib2.HTTPError:
            bot.bot_reply(event, "HTTP error, unable to retrieve results.")
            return
        
        page = res.read()
        #dbg_log = open('cicero_debug.log', 'w')
        #dbg_log.write(page)
        #dbg_log.close()
        page = BeautifulSoup(page)
        
        qr = page.queryresult
        if qr['success'] == 'false':
            bot.bot_reply(event, "Wolfram|Alpha error, unable to retrieve results.")
            return
        
        try:
            out_txt = "No text result (check your input interpretation)."
            in_txt = ''
            for pod in page.find_all('pod'):
                if pod['id'] == 'Input':
                    in_txt = pod.subpod.plaintext.get_text()
                elif pod['id'] == 'Result' and pod['primary'] == 'true':
                    out_txt = pod.subpod.plaintext.get_text()
        except KeyError:
            bot.bot_reply(event, "Error parsing results.")
            return
        
        if in_txt == '':
            bot.bot_reply(event, "Wolfram|Alpha error, could not interpret input.")
            return
        
        bot.bot_reply(event, out_txt)
        bot.bot_reply(event, 'Input interpretation: ' + in_txt, False)
        bot.bot_reply(event, 'More: http://www.wolframalpha.com/input/?i=' + q, False)
