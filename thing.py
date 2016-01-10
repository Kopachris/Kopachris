#!/usr/bin/env python2
import socket
import random
random.seed()
network = 'irc.ponychat.net'
port = 6667
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((network,port))
data = irc.recv(4096)
nick = "CheeseSandwichPie"
irc.send("NICK {}\r\n".format(nick))
irc.send("USER {0} 0 {0} :{0}\r\n".format(nick))
irc.settimeout(0.1)
quit = False
     
def ircParse(s): #courtesy of Twisted,
         prefix = ''
         trailing = []
         if not s:
            return None
         if s[0] == ':':
             try:
                 prefix, s = s[1:].split(' ', 1)
             except:
                 print ("[~] Malformed data received: "),s
         if s.find(' :') != -1:  
             s, trailing = s.split(' :', 1)
             args = s.split()
             args.append(trailing)
         else:
             args = s.split()
         command = args.pop(0)
         return prefix, command, args
     
def nickParse(s):
         return s.split("!")[0]
     
def fncLine(source,command,args):
        knownCallbacks = {
                          "PING":fncPing,
                          "PRIVMSG":fncPrivMsg,
                          }
        try:
            if command in knownCallbacks.keys():
                return (knownCallbacks[command])(source,args)
            else:
                return False
        except Exception as e:
            print (e)
            return False
     
def fncPing(source,args):
        irc.send("PONG "+args[0]+"\r\n")
        return False
     
def fncPrivMsg(source,args):
        channel = args[0]
        text = args[1].replace("\r\n","")
        if source == "Kelton2" or source == "PrincessTwilight":
            #bot control stuff goes here
            if text == "!quit":
                irc.send("QUIT :I'm leaving now. I'll see you guys again when my master wants to bring me out.\r\n")
                quit = True
                return True
            if text == "!join":
                irc.send("JOIN #geek\r\n")
            if text.startswith("!x"):
                text = text[3:]
                irc.send(text+"\r\n")
        if channel == "#geek":
            #fun stuff goes here
            if text == "Princess":
                irc.send("WORST PRINCESS EVAR!!!!\r\n")
                    if text == "linux":
                        irc.send("Windows is better.\r\n")
                        return False
                    while True: # main loop
                        try:
                            data = irc.recv(8192)
                            continue
                            lines = []
                            if data:
                                lines = data.split("\r\n")
                                for l in lines:
                                    line = ircParse(l)
                                    if line == None:
                                        continue
                                    else:
                                        print line
                                        source = nickParse(line[0])
                                        if source == line[0]: #from server (no nick), might as well blank
                                            source == ""
                                            command = line[1]
                                            args = line[2]
                                            quit = fncLine(source,command,args)
                                            if quit > 9: # True when quitting
                                                break
                        except:
                            pass