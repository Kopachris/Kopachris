import bot, bot_utils, os, sys
from gluon.storage import Storage

def main():
    k = db.bot_vars.tbl_k
    bot_nick = bot_utils.get_item('nick', db)
    bot_user = bot_utils.get_item('user', db)
    bot_rname = bot_utils.get_item('rname', db)
    bot_server = bot_utils.get_item('server', db)
    bot_port = int(bot_utils.get_item('port', db))
    bot_chans = eval(bot_utils.get_item('chans', db))
    db(k == 'pid').update(v=os.getpid())
    db(k == 'ppid').update(v=os.getppid())

    print "Connecting:"
    print bot_server + ':' + str(bot_port)
    print bot_chans
    print bot_nick + ':' + bot_user + ':' + bot_rname

    #signal(SIGUSR1, get_cmd)

    our_bot = bot.ircBot(bot_nick)
    #our_bot._mode = '+B-x'
    our_bot.db = db
    our_bot.user = bot_user
    our_bot.real_name = bot_rname
    our_bot.storage = Storage()
    our_bot.connect(bot_server,
                port=bot_port,
                channel=bot_chans,
                )
    our_bot.conn_host = bot_server
    our_bot.conn_port = bot_port
    our_bot.conn_channel = bot_chans
    our_bot.start()

#daemonize.start(main)
#createDaemon()
pid = os.fork()
if pid:
    sys.exit(0)
else:
    pid = os.fork()
    if pid:
        sys.exit(0)
    else:
     main()
