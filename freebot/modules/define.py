from gluon import *
import bot_utils
import urllib2
import json


description = "!define [<part-of-speech>] <word> - define a word"

prefix = "def_"

event_type = "PRIVMSG"

_cmd = ["!define"]

API = "http://api.wordnik.com/v4/word.json/{}/definitions?limit=1&partOfSpeech={}&api_key=<apikey>"
H_HTTP = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}

def init(db):
    pass

def remove(db):
    pass

def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    bot_nick = bot.nickname
    m = event.message.lower()
    margs = m.split()
    
    if m.startswith('!define'):
        if len(margs) == 2:
            pos = ''
            word = margs[1]
        elif len(margs) == 3:
            pos = margs[1]
            word = margs[2]
        else:
            return
        req = urllib2.Request(API.format(word, pos), headers=H_HTTP)
        j = json.loads(urllib2.urlopen(req).read())[0]
        if j is None:
            bot.bot_reply(event, "No definition found")
            return
        pos = j['partOfSpeech']
        definition = j['text']
        attr = j['attributionText']
        word = j['word']
        bot.bot_reply(event, "%s, %s - %s (Source: %s)" % (word, pos, definition, attr))
        #bot.bot_reply(event, "Source: %s" % attr, False)
