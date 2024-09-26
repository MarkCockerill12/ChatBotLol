import sockets
import sys

# create a bot that connects to the server given by user and listens for commands


def SocketConnect():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((port))
        s.send("NICK %s\r\n" % botname)
        s.send("USER %s %s bla :%s\r\n" % (botname, botname, botname))
        s.send("JOIN %s\r\n" % channel)
        return s
    except Exception as e:
        print(e)
        sys.exit(1)


def botSettings():
    
    server=input("Enter the server to connect to: ")
    if server == "":
        server = "::1"

    port=input("Enter the port to connect to: ")
    if port == "":
        port = 6667

    botname=input("Enter the name of the bot: ")
    if botname == "":
        botname = "Chat-bot"

    channel=input("Enter the channel to join: ")
    if channel == "":
        channel = "#test"


def joinChannel(s, channel):
    s.send("JOIN %s\r\n" % channel)
    return

