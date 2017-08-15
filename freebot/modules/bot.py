#!/usr/bin/env python2
# -*- coding: utf-8 -*-

## Begin license block ##

##           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
##                   Version 2, December 2004
##
## Copyright (C) 2013 Christopher Koch <kopachris@gmail.com>
##
## Everyone is permitted to copy and distribute verbatim or modified
## copies of this license document, and changing it is allowed as long
## as the name is changed.
##
##           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
##  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
##
##  0. You just DO WHAT THE FUCK YOU WANT TO.

## End license block ##

from gluon import *

from ircutils import bot, client
from datetime import datetime, timedelta
#from bs4 import BeautifulSoup
from io import StringIO

#import urllib2
#import dateutil.parser
#import json
#import random
import os, sys
import bot_utils
import traceback


class ircBot(bot.SimpleBot):
    def __init__(self, *args, **kwargs):
        bot.SimpleBot.__init__(self, *args, **kwargs)
        
        # our on_quit() handler removes users after logging their disconnect
        self.events['quit'].remove_handler(client._remove_channel_user_on_quit)
        
    def bot_log(self, event_type, source, target, message, hostmask=''):
        """
        Log an event in the database.
        """
        self.db.event_log.insert(event_type=event_type,
                                 event_source=source,
                                 event_target=target,
                                 event_message=message,
                                 event_hostmask=hostmask,
                                 event_time=datetime.today()
                                 )
        self.db.commit()

    def bot_reply(self, event, message, reply=True):
        """
        Intelligently target a reply to a given event.  If reply is True,
        message will be prefixed with message.source.
        """
        if type(message) == str:
            message = unicode(message, 'utf-8', 'ignore')
        elif type(message) != unicode:
            message = unicode(repr(message), 'utf-8', 'ignore')
        lim = 400
        if len(message) > lim * 3:
            message = message[:lim * 3]    # flood control
        #s = StringIO(unicode(message, 'utf-8', 'ignore'))
        s = StringIO(message)
        while True:
            chunk = s.read(lim).encode('utf-8', 'ignore')
            if len(chunk) > 0:
                if event.target.startswith('#'):
                    ## event is a channel message, reply to channel
                    if reply:
                        ## include username of who we're replying to
                        msg = event.source + ': ' + chunk
                        self.send_message(event.target, msg)
                        self.bot_log('PRIVMSG', self.nickname, event.target, msg)
                        ## only include username for first message if we have to split the message up
                        reply = False
                    else:
                        self.send_message(event.target, chunk)
                        self.bot_log('PRIVMSG', self.nickname, event.target, chunk)
                else:
                    ## event is a pivate message, reply to user
                    self.send_message(event.source, chunk)
                    self.bot_log('PRIVMSG', self.nickname, event.source, chunk)
            if len(chunk) < lim:
                break

    def run_modules(self, event, event_type):
        """
        Select modules for a given event type and run them if enabled.
        """
        try:
            db = self.db
            s = db(db.bot_modules.event_type == event_type)
            ## Spam prevention
            #if event.target != self.nickname:  # skip spam prevention if in PM
            if False:  # spam prevention disabled 7-9-2015
                cmd_strings = list()
                for m in s.select():
                    # grab command strings from modules
                    if m.mod_enabled:
                        this_m = __import__(m.name)
                        reload(this_m)
                        try:
                            if this_m._cmd is not None:
                                cmd_strings += this_m._cmd
                        except TypeError:
                            cmd_strings.append(this_m._cmd)
                        except AttributeError:
                            pass
                        finally:
                            del this_m
                cmd_uses = [0] * len(cmd_strings)
                time_lim = datetime.today() - timedelta(minutes=1)
                for i, cmd_str in enumerate(cmd_strings):
                    # for each command, count its uses by same user in last minute
                    q_msg = db.event_log.event_message.like(cmd_str + '%')
                    q_usr = db.event_log.event_source == event.source
                    q_tgt = db.event_log.event_target == event.target
                    q_t = db.event_log.event_time >= time_lim
                    cmd_uses[i] = db(q_msg & q_usr & q_tgt & q_t).count()
                total_cmds = sum(cmd_uses)
                #self.send_message('Kopachris', repr(zip(cmd_strings, cmd_uses)))
                if total_cmds == 6:
                    self.bot_reply(event, "...")
                    return
                elif total_cmds > 6:
                    return
            ## Try to intelligently determine if message is meant for bot
            try:
                msg = event.message.lower()
                for_us = (self.nickname.lower() in msg or
                          self.real_name.lower() in msg or
                          self.user.strip('!~@+').lower() in msg
                          )
                ## if bot's name is at beginning of msg to direct msg at bot, strip it
                if for_us and msg.startswith(self.nickname.lower()):
                    event.message = event.message[len(self.nickname):].lstrip(':, ')
                elif for_us and msg.startswith(self.real_name.lower()):
                    event.message = event.message[len(self.real_name):].lstrip(':, ')
                elif for_us and msg.startswith(self.user.strip('!~@+').lower()):
                    event.message = event.message[len(self.user.strip('!~@+')):].lstrip(':, ')
            except AttributeError:
                ## not a PRIVMSG or ACTION
                for_us = False

            if event.target == self.nickname or for_us:
                for m in s.select():
                    if m.mod_enabled:
                        # log = open('bot_modules.log', 'w+')
                        # log.write('Running module {} for event {}'.format(m.name, repr(event)))
                        # log.close()
                        this_m = __import__(m.name)
                        reload(this_m)
                        this_m.run(self, event, db)
                        del this_m
            elif event.target.startswith('#'):
                chan_nicks = set(self.channels[event.target].user_list)
                for m in s.select():
                    if m.mod_enabled:
                        if event.target in m.chans_dis or len(set(m.nicks_dis) & chan_nicks):
                            continue
                        if event.target in m.chans_en or len(set(m.nicks_en) & chan_nicks):
                            # log = open('bot_modules.log', 'w+')
                            # log.write('Running module {} for event {}'.format(m.name, repr(event)))
                            # log.close()
                            this_m = __import__(m.name)
                            reload(this_m)
                            this_m.run(self, event, db)
                            del this_m
        except Exception, e:
            #self.bot_reply(event, "An exception occurred: %s" % e, False)
            self.bot_log('ERROR', event.source, event.target, traceback.format_exc())

    def on_message(self, e):
        self.bot_log('PRIVMSG', e.source, e.target, e.message)
        self.run_modules(e, 'PRIVMSG')

    def on_join(self, e):
        self.bot_log('JOIN', e.source, e.target, '', e.user + '@' + e.host)
        self.run_modules(e, 'JOIN')

    def on_quit(self, e):
        for chan in self.channels.values():
            if e.source in chan.user_list:
                self.bot_log('QUIT', e.source, chan.name, ' '.join(e.params), e.user + '@' + e.host)
                chan.user_list.remove(e.source)
        if e.source == self.nickname:
            print "Detected self-quit. Closing connection."
            self.conn.close_when_done()
            return
        try:
            if e.source in self.trusted:
                print "Removing %s from auth..." % e.source
                self.trusted.remove(e.source)
                print "Removed."
        except AttributeError:
            print "Failed to remove, emptying auth..."
            self.trusted = set()
            print "Auth reinitialized."
        #self.run_modules(e, 'QUIT')

    def on_disconnect(self, e):
        self.bot_log('ERROR', 'self', '', 'Disconnected')
        host = self.conn_host
        port = self.conn_port
        chan = self.conn_channel
        print "Attempting to reconnect..."
        self.connect(host, port=port, channel=chan)
        print "Done."

    def on_part(self, e):
        self.bot_log('PART', e.source, e.target, ' '.join(e.params[1:]), e.user + '@' + e.host)
        self._remove_user(e)
        self.run_modules(e, 'PART')

    def on_kick(self, e):
        self.bot_log('KICK', e.source, e.target, ' '.join(e.params), e.user + '@' + e.host)
        self.channels[e.target].user_list.remove(e.params[0])
        self.run_modules(e, 'KICK')

    def on_nick_change(self, e):
        for chan in self.channels.values():
            if e.source in chan.user_list:
                self.bot_log('NICK', e.source, chan.name, e.target, e.user + '@' + e.host)
                chan.user_list.remove(e.source)
                chan.user_list.add(e.target)
        self.run_modules(e, 'NICK')

    def on_ctcp_action(self, e):
        self.bot_log('CTCP_ACTION', e.source, e.target, ' '.join(e.params))
        #self.run_modules(e, 'CTCP_ACTION')

    def on_welcome(self, e):
        pass
        #self.send_message('NickServ', 'identify <password>')
        #self.bot_log('PRIVMSG', self.nickname, 'NickServ', 'identify <password>')
        #self.join('#hotelreddit')
        #self.conn.execute('MODE', self.nickname, '-x')
    
    def _remove_user(self, e):
        if not event.target.startswith('#'):
            return
        self.channels[event.target].user_list.remove(event.source)
