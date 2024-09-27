import socket
import time

# Variables
nick = ""
server = ""
port = 6667
channel_info = {}  # Dictionary to store channel information

# Welcome!
print("  ________  ___  ___  ________  _________        ________  ________  _________   ")
print(" |\   ____\|\  \|\  \|\   __  \|\___   ___\     |\   __  \|\   __  \|\___   ___\ ")
print(" \ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     \ \  \|\ /\ \  \|\  \|___ \  \_| ")
print("  \ \  \    \ \   __  \ \   __  \   \ \  \       \ \   __  \ \  \\\  \   \ \  \  ")
print("   \ \  \____\ \  \ \  \ \  \ \  \   \ \  \       \ \  \|\  \ \  \\\  \   \ \  \ ")
print("    \ \_______\ \__\ \__\ \__\ \__\   \ \__\       \ \_______\ \_______\   \ \__\ ")
print("     \|_______|\|__|\|__|\|__|\|__|    \|__|        \|_______|\|_______|    \|__|")

# User Inputs
# Bot asks for desired server and defaults to ::1
server = input("Please enter your desired server, if you don't enter anything it will default to '::1': ")
if server == "":
    server = "::1"

# Bot asks for desired port and defaults to 6667
try:
    port = int(input("Please enter your desired port, if you don't enter anything it will default to 6667: ") or "6667")
except ValueError:
    port = 6667

# Bot asks for desired nickname and defaults to BotLol
nick = input("Please enter your desired nickname, if you don't enter anything it will default to BotLol: ")
if nick == "":
    nick = "BotLol"

# Bot asks for desired channel and defaults to #Test
channel = input("What channel should the bot join? If you don't enter anything it will default to #Test: ")
if channel == "":
    channel = "#Test"

# Improved socket handling with explicit connection closing
try:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        print(f"Connecting to {server}:{port}...")
        s.connect((server, port))

        Connected = True
        
        # Sends Nick and User to join the server using user inputs
        s.send(f"NICK {nick}\r\n".encode('utf-8'))
        s.send(f"USER {nick} 0 * :{nick}\r\n".encode('utf-8'))

        # Joins the specified channel
        s.send(f"JOIN {channel}\r\n".encode('utf-8'))

        # Wait for server's response before sending a message
        while Connected:
            data = s.recv(1024).decode('utf-8')
            print("Server Response:", data.strip())  # Debugging line to check server's response

            # Store channel information from server responses (more explicit)
            if f":{nick}!{nick}@".lower() in data.lower() and "join".lower() in data.lower():
                print(f"Join event detected for {nick} in {channel}")
                channel_info[channel] = {
                'user': nick,
                'channel': channel,
                'timestamp': time.time(),  # Optional, to store the time when the bot joined
                'server_response': data.strip()  # Optional, to store the entire server response
            }
            print(f"Stored channel information: {channel_info[channel]}")


           # Look for a "JOIN" confirmation from the server
            if f":{nick}!{nick}@".lower() in data.lower() and "join".lower() in data.lower():
                print(f"Successfully joined {channel}. Sending message...")
                s.send(f"PRIVMSG {channel} :Hello {channel}. I am BotLol, the friendly chat Bot, say !help to find out how talk to me.\r\n".encode('utf-8'))
                print(f"Message sent to {channel}: 'Hello World.'")

            # Check for "PING" message from server
            if data.startswith("PING"):
                # Extract the server's ping message and reply with a PONG
                ping_response = data.split()[1]
                s.send(f"PONG {ping_response}\r\n".encode('utf-8'))
                print(f"Sent PONG response to {ping_response}")
                
                # Handle messages from the channel
            if "PRIVMSG" in data:
                sender = data.split('!', 1)[0][1:]
                message = data.split('PRIVMSG', 1)[1].split(':', 1)[1]
                print(f"Message from {sender}: {message}")

                if message.strip().lower() == "!quit":
                    response = f"Alright see ya, {sender}!"
                    s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                    Connected = False
                    print("Quitting...")

                elif message.strip().lower() == "!hello":
                    response = f"Hello, {sender}!"
                    s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                    print(f"Responded to {sender}: {response}")

                elif message.strip().lower() == "!help":
                    response = f"!Hello - I will say hello back to you. !Quit - I will say goodbye and leave the channel. !SaveData - I will show you the stored channel information."
                    s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                    print(f"Responded to {sender}: {response}")

                elif message.strip().lower() == "!savedata":
                    # Check if the channel information is available
                    print("AAARGH")
                    if channel in channel_info:
                        response = f"Stored channel information: {channel_info[channel]}"
                        s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                        print(f"Responded to {sender}: {response}")
                    else:
                        response = "No channel information saved yet."
                        s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                        print(f"Responded to {sender}: {response}")

                else:
                    response = f"You're SOOO right, {sender}! You're sooo amazing"
                    s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                    print(f"Responded to {sender}: {response}")


            


# Exception handling
except (KeyboardInterrupt, SystemExit):
    print("Bot interrupted, closing connection...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # This ensures the socket is properly closed when the bot stops or an error occurs
    print("Connection closed.")
