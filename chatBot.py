import socket

# Variables
nick     = ""
realname = 'Example miniirc bot - https://gitlab.com/luk3yx/stdinbot'
# identity = None
# identity = '<username> <password>'
prefix   = '`'

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

server= input("Please enter your desired server, if you don't enter anything it will default to '::1': ")
if server == "":
    server = "::1"

try:
    port = int(input("Please enter your desired port, if you don't enter anything it will default to 6667: ") or "6667")
except ValueError:
    port = 6667


nick= input("Please enter your desired nickname, if you don't enter anything it will default to BotLol: ")
if nick == (""):
    nick = "BotLol"

#https://realpython.com/python-sockets/
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    print(server)
    print(port)
    s.connect((server, port))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")
