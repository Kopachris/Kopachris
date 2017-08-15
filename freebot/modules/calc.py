from __future__ import division
from gluon import *
import bot_utils
#from ast import literal_eval


description = "Simple calculator"
prefix = "calc"
event_type = "PRIVMSG"
_cmd = ["!calc", "!math"]

def init(db):
    pass


def remove(db):
    pass


def run(bot, event, db):
    msg = event.message
    s = msg.split()
    args = ' '.join(s[1:])
    m = msg.lower()
    
    sandbox = {'__import__': None,
               'eval': None,
               'input': None,
               'open': None,
               'staticmethod': None,
               'all': None,
               'enumerate': None,
               'any': None,
               'isinstance': None,
               'basestring': None,
               'execfile': None,
               'issubclass': None,
               'print': None,
               'super': None,
               'file': None,
               'iter': None,
               'property': None,
               'filter': None,
               'len': None,
               'range': None,
               'type': None,
               'bytearray': None,
               'raw_input': None,
               'unichr': None,
               'callable': None,
               'format': None,
               'locals': None,
               'reduce': None,
               'unicode': None,
               'frozenset': None,
               'reload': None,
               'vars': None,
               'classmethod': None,
               'getattr': None,
               'map': None,
               'repr': None,
               'xrange': None,
               'globals': None,
               'zip': None,
               'compile':None,
               'hasattr': None,
               'memoryview': None,
               'complex': None,
               'hash': None,
               'set': None,
               'delattr': None,
               'help': None,
               'next': None,
               'setattr': None,
               'dict': None,
               'object': None,
               'slice': None,
               'dir': None,
               'id': None,
               'sorted': None,
               }
    
    if m.startswith('!math') or m.startswith('!calc'):
        try:
            result = eval(args, sandbox, {})
            if result is not None:
                bot.bot_reply(event, str(result))
        except:
            return
