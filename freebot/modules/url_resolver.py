#!/usr/bin/env python
# coding: utf8
from gluon import *
import bot_utils
import urllib2
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import traceback
import re, string #for removing non-alphanumeric characters for comparing titles to the url

## Description stored in db.bot_modules
description = "URL resolver"

## Prefix stored in db.bot_modules
## Each module should have its own prefix for bot_vars entries
prefix = "url_"

## Event type handled by this module
event_type = "PRIVMSG"

## Additional global vars
H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
          'Range': 'bytes=0-500000'}  # get at most 500KB

whitelist = ('fave.me',
             'deviantart.com',
             )
blacklist = ('wikipedia.org',
             'lmgtfy.com',
             'kopachr.is',
             'bash.org',
             'amazon.com',
             'youtube.com',
             'youtu.be',
             'twitter.com',
             'reddit.com',
             )

def init(db):
    bot_utils.set_item('url_timeout', '0', db)
    bot_utils.set_item('url_prev', '', db)
    s = db(db.bot_vars.tbl_k == 'url_timeout')
    if not len(s.select()):
        db.bot_vars.insert(tbl_k='url_timeout', v='0')

    s = db(db.bot_vars.tbl_k == 'url_prev')
    if not len(s.select()):
        db.bot_vars.insert(tbl_k='url_prev', v='')


def remove(db):
    pass


def run(bot, event, db):
    this_mod = db(db.bot_modules.name == 'url_resolver').select().first()
    prefix = this_mod.vars_pre
    prev_url = bot_utils.get_item(prefix+'prev', db)
    secure = False
    if event.source == 'gonzobot':
        return
    i = event.message.find('http://')
    if i == -1:
        i = event.message.find('https://')
        secure = True
    if i > -1:
        u = ''
        for c in event.message[i:]:
            if c == ' ':
                break
            u += c
        to_the_moon = True
        for solar in whitelist:
            if solar in u:
                to_the_moon = False
                break
        for solar in blacklist:
            if solar in u:
                return
        if prev_url != u:
            bot_utils.set_item(prefix+'prev', u, db)
            if re.match('^https?://(www\.)?youtu\.?be(\.com)?', u) and 'VB6' in bot.channels[event.target].user_list:
                return
            #if re.match('^https?://(www\.)?youtu\.?be(\.com)?', u): # just gives http 429 too many requests
                #secure = True
                #return
            if len(u) == len(event.message) and not secure and to_the_moon and ('`Luna`' in bot.channels[event.target].user_list or
                                                                                '`Celestia`' in bot.channels[event.target].user_list):
                return
            try:
                req = urllib2.Request(u, headers=H_HTTP)
                res = urllib2.urlopen(req)
                page = res.read().strip(' \t\n\r')
                res.close()
                del res
                if page.startswith('<!doctype>'):
                    page = page[10:]
                page = BeautifulSoup(page)
                try:
                    #not exactly the most optimized, I know
                    s = page.title.get_text().strip()
                    rchars = '\n\r\t\0'
                    for c in rchars:
                        s = s.replace(c, ' ')
                    title_in_url = True
                    title = s.lower()
                    pattern = re.compile('[\W_]+')
                    title = pattern.sub(' ', title).strip()
                    u = u.lower()
                    for word in title.split():
                        if word not in u:
                            title_in_url = False
                            break
                    if not title_in_url:
                        if len(s) > 300:
                            s = s[:297] + '...'
                        bot.bot_reply(event, s, False)
                        del page
                except AttributeError, e:
                    #bot.bot_log('ERROR', event.source, 'url_resolver', "AttributeError: %s" % e)
                    del page
                    pass
            except Exception, e:
                bot.bot_log('ERROR', event.source, 'url_resolver', traceback.format_exc())
                #del page
                pass
