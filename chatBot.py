import socket

# Variables
nick     = ""

server= ""
port = 6667


# Welcome!
print("  ________  ___  ___  ________  _________        ________  ________  _________   ")
print(" |\   ____\|\  \|\  \|\   __  \|\___   ___\     |\   __  \|\   __  \|\___   ___\ ")
print(" \ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     \ \  \|\ /\ \  \|\  \|___ \  \_| ")
print("  \ \  \    \ \   __  \ \   __  \   \ \  \       \ \   __  \ \  \\\  \   \ \  \  ")
print("   \ \  \____\ \  \ \  \ \  \ \  \   \ \  \       \ \  \|\  \ \  \\\  \   \ \  \ ")
print("    \ \_______\ \__\ \__\ \__\ \__\   \ \__\       \ \_______\ \_______\   \ \__\ ")
print("     \|_______|\|__|\|__|\|__|\|__|    \|__|        \|_______|\|_______|    \|__|")

#User Inputs
#Bot asks for desired server and defaults to ::1
server= input("Please enter your desired server, if you don't enter anything it will default to '::1': ")
if server == "":
    server = "::1"

#Bot asks for desired port and defaults to 6667
try:
    port = int(input("Please enter your desired port, if you don't enter anything it will default to 6667: ") or "6667")
except ValueError:
    port = 6667

#Bot asks for desired nickname and defaults to BotLol
nick= input("Please enter your desired nickname, if you don't enter anything it will default to BotLol: ")
if nick == (""):
    nick = "BotLol"

#Bot asks for desired channel and defaults to #Test
channel = input("What channel should the bot join? If you don't enter anything it will default to #Test")
if channel == "":
    channel == "#Test"


#some code snippets from https://realpython.com/python-sockets/
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    print(server)
    print(port)
    s.connect((server, port))
    
    Connected = True
    #Sends Nick and User to join server - Need to make it work with user inputs
    s.send(b"NICK BotLol\r\n")
    s.send(b"USER Bot Bot2 Bot3 Bot4\r\n")

    #Commands for Bot to do - Need to make it work with user inputs
    s.send(b"JOIN #Test\r\n")
    s.send (b"PRIVMSG #Test :Hello World.\r\n")
    
    #Handler for Ping / Pong requests to avoid timeout needs work
    #while Connected
     #data = s.recv(1024).decode
    # print(data)
     #if data[0:4] == "PING"
     # print(data)
    #  s.send(b"PONG" + data.split()[1]+"r\n")
     # print("Pong")

    while Connected:
        data = s.recv(1024).decode()
        print(data)
        if data[0:4] == "PING":
            s.send(s, data.replace("PING", server))
            print("Pong")


    