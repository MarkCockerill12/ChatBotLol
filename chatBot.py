# Example miniirc-based bot © 2018 by luk3yx
#outline of code from https://github.com/luk3yx/stdinbot/blob/master/example.py


import miniirc, sys
assert miniirc.ver >= (1,4,0), 'This bot requires miniirc >= v1.4.0.'

# Variables
nick     = 'miniirc-test' + str(hash('.'))[1:4] # Make a unique(-ish) nickname
ident    = nick
realname = 'Example miniirc bot - https://gitlab.com/luk3yx/stdinbot'
identity = None
# identity = '<username> <password>'
debug    = False
channels = ['#lurk']
prefix   = '`'

ip = 'xeroxirc.net'
port = 6697

# Welcome!
print("  ________  ___  ___  ________  _________        ________  ________  _________   ")
print(" |\   ____\|\  \|\  \|\   __  \|\___   ___\     |\   __  \|\   __  \|\___   ___\ ")
print(" \ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     \ \  \|\ /\ \  \|\  \|___ \  \_| ")
print("  \ \  \    \ \   __  \ \   __  \   \ \  \       \ \   __  \ \  \\\  \   \ \  \  ")
print("   \ \  \____\ \  \ \  \ \  \ \  \   \ \  \       \ \  \|\  \ \  \\\  \   \ \  \ ")
print("    \ \_______\ \__\ \__\ \__\ \__\   \ \__\       \ \_______\ \_______\   \ \__\ ")
print("     \|_______|\|__|\|__|\|__|\|__|    \|__|        \|_______|\|_______|    \|__|")

server= input("Please enter your desired server, if you don't enter anything it will default to ::1")
if server == (""):
    server == ("::1")

port= input("Please enter your desired port, if you don't enter anything it will default to 6667")
if port == (""):
    port == ("6667")

nick= input("Please enter your desired nickname, if you don't enter anything it will default to BotLol")
if nick == (""):
    nick == ("BotLol")

# Handle normal messages
# This could probably be better than a large if/else statement.
# @irc.Handler('PRIVMSG', colon=False)
# def handle_privmsg(irc, hostmask, args):
#     channel = args[0]
#     text = args[-1].split(' ')
#     cmd = text[0].lower()
#     # Unprefixed commands here
#     if cmd.startswith('meep'):
#         irc.msg(channel, '\u200bMeep!')
#     elif cmd.startswith(prefix):
#         # Prefixed commands
#         cmd = cmd[len(prefix):]
#         if cmd == 'yay':
#             irc.msg(channel, '\u200bYay!')
#         elif cmd == 'rev':
#             if len(text) > 1:
#                 irc.msg(channel, "{}: {}".format(hostmask[0],
#                     ' '.join(text[1:])[::-1]))
#             else:
#                 irc.msg(channel, 'Invalid syntax! Syntax: ' + prefix +
#                     'rev <string>')
#         elif cmd == 'about':
#             irc.msg(channel,
#                 'I am {}, an example miniirc bot.'.format(irc.nick))

# Connect
# if __name__ == '__main__':
#     irc.connect()