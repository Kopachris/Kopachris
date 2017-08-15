from gluon import *
import inspect

description = "!bucket - create new single-response commands"

prefix = "bkt_"

event_type = "PRIVMSG"


# get database
#try:
#    db = inspect.getouterframes(inspect.currentframe())[1][0].f_locals['db']
#    mod_name = __name__.rsplit('.', 1)[1]
#    this_mod = db(db.bot_modules.name == mod_name).select()
#    prefix = this_mod.first().vars_pre
#    verbs_tbl = prefix + 'verbs'
#    if verbs_tbl not in db:
#        db.define_table(verbs_tbl,
#                        Field('verb', 'string', unique=True, length=32),
#                        Field('response', 'string', length=600),
#                        Field('enabled', 'list:string', default=[bot.nickname]),
#                        Field('disabled', 'list:string', default=[]),
                        #migrate=True
#                        )
    
#    _cmd = [r.verb for r in db(db[verbs_tbl]).select()]
#except:
#    pass


def init(db):
    pass
    
def remove(db):
    pass
    
def run(bot, event, db):
    mod_name = __name__.rsplit('.', 1)[1]
    this_mod = db(db.bot_modules.name == mod_name).select()
    prefix = this_mod.first().vars_pre
    
    # set up verbs table
    verbs_tbl = prefix + 'verbs'
    if verbs_tbl not in db:
        db.define_table(verbs_tbl,
                        Field('verb', 'string', unique=True, length=32),
                        Field('response', 'string', length=600),
                        Field('enabled', 'list:string', default=[bot.nickname]),
                        Field('disabled', 'list:string', default=[]),
                        #migrate=True
                        )
    
    m = event.message.lower()
    s = m.split(' ', 3)
    S = event.message.split(' ', 3)
    args_split = event.message.split()
    if len(args_split) > 1:
        args = ' '.join(args_split[1:])
    else:
        args = event.source
    
    verb_rows = db().select(db[verbs_tbl].ALL)
    all_verbs = [v.verb for v in verb_rows]
    
    if s[0] == '!bucket':
        py_mod = db(db.bot_modules.name == 'py')
        if py_mod.isempty() or not py_mod.select().first().mod_enabled:
            bot.bot_reply(event, "Bucket module depends on 'py' module. Please make sure it is installed and enabled.")
            return
        if event.source in bot.trusted:
            try:
                if s[1] == 'add':
                    db[verbs_tbl].update_or_insert(db[verbs_tbl].verb=='!'+s[2],verb='!'+s[2], response=S[3])
                    bot.bot_reply(event, "Added verb '!{}'".format(s[2]))
                if s[1] == 'en':
                    this_verb = db(db[verbs_tbl].verb == '!'+s[2])
                    en = set(this_verb.select().first().enabled)
                    en.add(S[3])
                    this_verb.update(enabled=list(en))
                    bot.bot_reply(event, "Verb {} now enabled by nick/channel {}".format(s[2], S[3]))
                if s[1] == 'unen':
                    this_verb = db(db[verbs_tbl].verb == '!'+s[2])
                    en = set(this_verb.select().first().enabled)
                    en.remove(S[3])
                    this_verb.update(enabled=list(en))
                    bot.bot_reply(event, "Verb {} no longer enabled by nick/channel {}".format(s[2], S[3]))
                if s[1] == 'dis':
                    this_verb = db(db[verbs_tbl].verb == '!'+s[2])
                    dis = set(this_verb.select().first().disabled)
                    dis.add(S[3])
                    this_verb.update(disabled=list(dis))
                    bot.bot_reply(event, "Verb {} now disabled by nick/channel {}".format(s[2], S[3]))
                if s[1] == 'undis':
                    this_verb = db(db[verbs_tbl].verb == '!'+s[2])
                    dis = set(this_verb.select().first().disabled)
                    dis.remove(S[3])
                    this_verb.update(disabled=list(dis))
                    bot.bot_reply(event, "Verb {} no longer disabled by nick/channel {}".format(s[2], S[3]))
                if s[1] == 'stat':
                    this_verb = db(db[verbs_tbl].verb == '!'+s[2]).select().first()
                    dis = this_verb.disabled
                    en = this_verb.enabled
                    bot.bot_reply(event, "Verb '!{}' enabled by {} and disabled by {}".format(s[2],en,dis))
                return
            except IndexError:
                bot.bot_reply(event, "Invalid arguments")
        else:
            bot.bot_reply(event, "Please authenticate yourself with !auth")
            return
    elif s[0] in all_verbs:
        i = all_verbs.index(s[0]) + 1
        v = db[verbs_tbl][i]
        action = v.response[0] == '*' and v.response[-1] == '*'
        resp = unicode(v.response, encoding='utf-8', errors='ignore').format(**locals())
        #resp = v.response.format(**locals())
        if action:
            resp = v.response.strip('*').format(**locals())
        if event.target.startswith('#'):
            tgt = event.target
            chan = set(bot.channels[event.target].user_list)
            chan.add(event.target)
            v_en = set(v.enabled)
            v_dis = set(v.disabled)
            if len(chan & v_en) and not len(chan & v_dis):
                if action:
                    bot.bot_log('CTCP_ACTION', bot.nickname, event.target, resp)
                    bot.send_action(tgt, resp)
                else:
                    bot.bot_reply(event, resp, False)
        else:
            tgt = event.source
            if action:
                bot.bot_log('CTCP_ACTION', bot.nickname, event.source, resp)
                bot.send_action(tgt, resp)
            else:
                bot.bot_reply(event, resp, False)
