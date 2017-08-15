#!/usr/bin/env python
# coding: utf8

from gluon import *
import bot_utils
import urllib2
import json
from datetime import datetime
import dateutil.parser

description = "Retrieves weather from wunderground.com.  Set your WeatherUnderground API key by PMing the bot '<prefix>apikey <your-api-key>' or manually setting the wu_apikey variable."

prefix = "wu_"

event_type = "PRIVMSG"

_cmd = ["!weather", "!forecast"]

W_URL = 'http://api.wunderground.com/api/%(apikey)s/conditions/q/%(q)s.json'
F_URL = 'http://api.wunderground.com/api/%(apikey)s/forecast/q/%(q)s.json'
W_FMT = '%(station)s at %(time)s: [Temp: %(f)s F / %(c)s C %(cond)s] [Hum: %(hum)s] [Wind: %(wind)s %(mph)s mph / %(kph)s kph]'
F_FMT = 'Forecast for %(station)s: %(d1)s - %(f1)s, %(d2)s - %(f2)s'
T_FMT = '%I:%M %p %Z on %B %d, %Y'

def init(db):
    bot_utils.set_item(prefix + 'apikey', '', db)
    bot_utils.set_item(prefix + 'wfmt', W_FMT, db)
    bot_utils.set_item(prefix + 'ffmt', F_FMT, db)


def remove(db):
    pass


def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    if event.message.startswith('!wuname'):
        bot.bot_reply(event, mod_name)
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    k_apikey = prefix + 'apikey'
    apikey = bot_utils.get_item(k_apikey, db)
    w_fmt = bot_utils.get_item(prefix + 'wfmt', db) or W_FMT
    f_fmt = bot_utils.get_item(prefix + 'ffmt', db) or F_FMT
    w_locs = prefix + 'locations'
    if w_locs not in db:
        db.define_table(w_locs,
                        Field('tbl_k', 'string', unique=True, length=32),
                        Field('v', 'string', length=512),
                        )

    if event.message.startswith(k_apikey):
        apikey = event.message.split()[1]
        bot_utils.set_item(k_apikey, apikey, db)
        bot.bot_reply(event, "Wunderground API key set to %s" % apikey)
    elif event.message.lower().startswith('!weather'):
        if apikey == '':
            bot.bot_reply(event, "Wunderground API key not installed.  Please let the bot admin know.")
            return
        if len(event.message.split()) > 1:
            q = '+'.join(event.message.split()[1:])
            bot_utils.set_item(event.source, q, db, w_locs)
        else:
            q = bot_utils.get_item(event.source, db, w_locs)
            if q is None:
                bot.bot_reply(event, 'There is no stored location for you.  Please try "!weather [location]".')
                return

        try:
            req = urllib2.Request(W_URL % locals())
            response = urllib2.urlopen(req)
        except urllib2.HTTPError:
            bot.bot_reply(event, "Unable to retrieve weather")
            return
        try:
            w_data = json.load(response)['current_observation']
        except KeyError:
            #dbgf = open('wu_dbg.log', 'w')
            #dbgf.write(response)
            #dbgf.close()
            bot.bot_reply(event, "No results, or too many.  Try being more specific, or some other error has occurred.")
            return

        station = w_data['observation_location']['full']
        time = dateutil.parser.parse(w_data['observation_time_rfc822']).strftime(T_FMT)
        f = w_data['temp_f']
        c = w_data['temp_c']
        cond = w_data['weather']
        hum = w_data['relative_humidity']
        wind = w_data['wind_dir']
        mph = w_data['wind_mph']
        kph = w_data['wind_kph']
        weather = w_fmt % locals()
        bot.bot_reply(event, weather)
    elif event.message.lower().startswith('!forecast'):
        if apikey == '':
            bot.bot_reply(event, "Wunderground API key not installed.  Please let the bot admin know.")
            return
        if len(event.message.split()) > 1:
            q = '+'.join(event.message.split()[1:])
            bot_utils.set_item(event.source, q, db, w_locs)
        else:
            q = bot_utils.get_item(event.source, db, w_locs)
            if q is None:
                bot.bot_reply(event, 'There is no stored location for you.  Please try "!forecast [location]".')
                return

        try:
            req = urllib2.Request(W_URL % locals())
            response = urllib2.urlopen(req)
        except urllib2.HTTPError:
            bot.bot_reply(event, "Unable to retrieve forecast")
            return
        try:
            w_data = json.load(response)['current_observation']
        except KeyError:
            bot.bot_reply(event, "No results, or too many.  Try being more specific, or some other error has occurred.")
            return

        station = w_data['observation_location']['full']
        country = w_data['observation_location']['country_iso3166']

        try:
            req = urllib2.Request(F_URL % locals())
            response = urllib2.urlopen(req)
        except urllib2.HTTPError:
            bot.bot_reply(event, "Unable to retrieve forecast")
            return
        f_data = json.load(response)['forecast']
        #if f_data['simpleforecast']['forecastday'][0]['date']['tz_long'].startswith('America'):
        if country == 'US':
            f1 = f_data['txt_forecast']['forecastday'][0]['fcttext']
            f2 = f_data['txt_forecast']['forecastday'][1]['fcttext']
        else:
            f1 = f_data['txt_forecast']['forecastday'][0]['fcttext_metric']
            f2 = f_data['txt_forecast']['forecastday'][1]['fcttext_metric']
        d1 = f_data['txt_forecast']['forecastday'][0]['title']
        d2 = f_data['txt_forecast']['forecastday'][1]['title']
        forecast = f_fmt % locals()
        bot.bot_reply(event, forecast)
