import os
import socket
import sys
import time
import random
import re
import argparse

# Bot Class
class Bot:
    def __init__(self, server="::1", port=6667, nick="BotLol", channel="#Test"):
        self.server = server
        self.port = port
        self.nick = nick
        self.channel = channel
        self.channel_info = {}
        self.Connected = False
        self.s = None
        self.command_prefix = "!"
        self.last_channel_message_time = 0
        self.jokes_file = "jokes.txt"
        self.startup_time = time.time()  # To track uptime

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            print(f"Connecting to {self.server}:{self.port}...")
            self.s.connect((self.server, self.port))

            # Send NICK and USER commands
            self.s.send(f"NICK {self.nick}\r\n".encode('utf-8'))
            self.s.send(f"USER {self.nick} 0 * :{self.nick}\r\n".encode('utf-8'))

            # Join the channel
            self.s.send(f"JOIN {self.channel}\r\n".encode('utf-8'))

            self.Connected = True
            self.running_bot()

        except Exception as e:
            print(f"Socket error occurred: {e}")
            self.shutdown()

    def running_bot(self):
        while self.Connected:
            try:
                data = self.s.recv(1024).decode('utf-8')
                if not data:
                    print("Disconnected from server.")
                    break

                print("Server Response:", data.strip())

                # Handle PING/PONG
                if data.startswith("PING"):
                    ping_response = data.split()[1]
                    self.s.send(f"PONG {ping_response}\r\n".encode('utf-8'))
                    print(f"Sent PONG response to {ping_response}")

                # Handle channel join confirmation
                if f":{self.nick}!{self.nick}@".lower() in data.lower() and "join".lower() in data.lower():
                    print(f"Successfully joined {self.channel}. Sending welcome message...")
                    self.send_message(f"Hello {self.channel}. I am {self.nick}, the friendly chat Bot, say !help to find out how to talk to me.")
                    self.channel_info[self.channel] = {
                        'user': self.nick,
                        'channel': self.channel,
                        'timestamp': time.time(),
                        'server_response': data.strip()
                    }

                # Handle messages from the channel
                if "PRIVMSG" in data:
                    self.handle_privmsg(data)

            except Exception as e:
                print(f"Error while receiving data: {e}")
                self.Connected = False
                self.shutdown()

    def send_message(self, message):
        try:
            # Ensure the message is sent to the channel
            self.s.send(f"PRIVMSG {self.channel} :{message}\r\n".encode('utf-8'))
            print(f"Message sent to {self.channel}: {message}")
        except Exception as e:
            print(f"Error while sending message: {e}")

    def handle_privmsg(self, data):
        sender = data.split('!', 1)[0][1:]  # Extract sender
        target = data.split('PRIVMSG', 1)[1].split(':', 1)[0].strip()  # Target channel or bot
        message = data.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()  # Message content

        print(f"Message from {sender} to {target}: {message}")

        if target.lower() == self.nick.lower():  
            if os.path.exists(self.jokes_file):
                with open(self.jokes_file, "r") as readjoke:
                    jokedata = readjoke.read().splitlines()
                    if jokedata:
                        joke = random.choice(jokedata)
                        self.s.send(f"PRIVMSG {sender} :{joke}\r\n".encode('utf-8'))
                        print(f"Sent a joke to {sender}: {joke}")
                    else:
                        self.send_message(f"Sorry {sender}, I have no jokes to share right now.")
            else:
                self.send_message(f"Sorry {sender}, I couldn't find the jokes file.")

        elif message.startswith(self.command_prefix):  # If it's a command
            parts = message[len(self.command_prefix):].strip().split()
            command = parts[0].lower()
            args = parts[1:]

            match command:
                case "quit" | "exit" | "leave":  # Added aliases
                    response = f"Alright, see ya, {sender}!"
                    self.send_message(response)
                    self.Connected = False
                    print("Quitting...")
                    self.shutdown()

                case "hello":
                    response = f"Hello, {sender}!"
                    self.send_message(response)

                case "help" | "commands" | "info":  # Added aliases for help
                    help_message = [
                        "!hello - I will say hello back to you.",
                        "!quit - I will say goodbye and leave the channel.",
                        "!savedata - I will show you the stored channel information.",
                        "!privmsg <user> <message> - Send a private message to a user.",
                        "!slap <user> - I will slap the user.",
                        "!uptime - Show how long I've been running."
                    ]
                    for msg in help_message:
                        self.send_message(msg)
                        time.sleep(0.5)

                case "savedata":
                    if self.channel in self.channel_info:
                        response = f"Stored channel information: {self.channel_info[self.channel]}"
                    else:
                        response = "No channel information saved yet."
                    self.send_message(response)

                case "privmsg":
                    if len(args) > 1:
                        user = args[0]
                        priv_message = ' '.join(args[1:])
                        if user.lower() == self.nick.lower():
                            self.send_message("I can't send private messages to myself!")
                        elif user.lower() in self.user_search():
                            self.s.send(f"PRIVMSG {user} :{priv_message}\r\n".encode('utf-8'))
                            print(f"Sent private message to {user}: {priv_message}")
                        else:
                            self.send_message(f"User {user} not found.")
                    else:
                        self.send_message("Usage: !privmsg <user> <message>")

                case "slap":
                    user_list = self.user_search()
                    if len(args) >= 1:
                        user = args[0]
                        if user.lower() == self.nick.lower() or user.lower() == sender.lower():
                            response = "I can't slap myself or the sender!"
                        elif user.lower() in [u.lower() for u in user_list]:
                            response = f"\x01ACTION slaps {user} around a bit with a large trout\x01"
                        else:
                            response = f"\x01ACTION slaps {sender} because {user} is not a user in the server\x01"
                    else:
                        if len(user_list) <= 2:
                            response = "There is no valid target to slap because only me and the sender exist in the channel"
                        else:
                            target = random.choice([u for u in user_list if u.lower() != self.nick.lower() and u.lower() != sender.lower()])
                            response = f"\x01ACTION slaps {target} around a bit with a large trout\x01"
                    self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
                    print(f"Sent slap action for {user if len(args) >= 1 else target}")

                case "uptime":
                    uptime = time.time() - self.startup_time
                    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))
                    self.send_message(f"I've been running for {uptime_str}.")

                case _:
                    self.send_message(f"Unknown command, {sender}. Try !help for a list of commands.")

        else:
            if target.lower() == self.channel.lower() and time.time() - self.last_channel_message_time > 30:  # Random reply to non-command message, 30s cooldown
                response = f"You're so right, {sender}! You're so amazing!"
                self.send_message(response)
                self.last_channel_message_time = time.time()

    def shutdown(self):
        try:
            if self.s:
                self.s.close()
                print("Connection closed successfully.")
            else:
                print("Socket was never created.")
        except Exception as e:
            print(f"Error while closing socket: {e}")

    def user_search(self):
        user_list = []
        self.s.send(f"NAMES {self.channel}\r\n".encode('utf-8'))  # Fetch user list
        self.s.settimeout(5)  # Set a timeout for recv to avoid blocking

        try:
            while True:
                data = self.s.recv(2048).decode('utf-8')
                match = re.search(r"353 .* = .* :(.*)", data)

                if match:
                    users = match.group(1).split()
                    user_list.extend(users)

                if ' 366 ' in data:  # 366 code indicates end of user list
                    break
        except socket.timeout:
            print("Timeout while fetching user list.")

        return user_list

def main():
    print(r"  ________  ___  ___  ________  _________        ________  ________  _________   ")
    print(r" |\   ____\|\  \|\  \|\   __  \|\___   ___\     |\   __  \|\   __  \|\___   ___\ ")
    print(r" \ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     \ \  \|\ /\ \  \|\  \|___ \  \_| ")
    print(r"  \ \  \    \ \   __  \ \   __  \   \ \  \       \ \   __  \ \  \\\  \   \ \  \  ")
    print(r"   \ \  \____\ \  \ \  \ \  \ \  \   \ \  \       \ \  \|\  \ \  \\\  \   \ \  \ ")
    print(r"    \ \_______\ \__\ \__\ \__\ \__\   \ \__\       \ \_______\ \_______\   \ \__\ ")
    print(r"     \|_______|\|__|\|__|\|__|\|__|    \|__|        \|_______|\|_______|    \|__|")

    # User Inputs with Command-line Arguments
    parser = argparse.ArgumentParser(description='ChatBot Configuration')
    parser.add_argument('--host', type=str, help="Server host")
    parser.add_argument('--port', type=int, help="Port number")
    parser.add_argument('--name', type=str, help="Nickname")
    parser.add_argument('--channel', type=str, help="Channel name")

    args = parser.parse_args()

    # Prompt for input if arguments are not provided
    if args.host is None:
        args.host = input("Please enter the server host (default is 'localhost'): ") or 'localhost'
    if args.port is None:
        args.port = input("Please enter the desired port (default is 6667): ")
        args.port = int(args.port) if args.port.isdigit() else 6667
    if args.name is None:
        args.name = input("Please enter the bot name (default is 'SuperBot'): ") or 'SuperBot'
    if args.channel is None:
        args.channel = input("Please enter the channel name (default is '#hello'): ") or '#hello'

    # Print the arguments received for debugging
    print(f"Server: {args.host}, Port: {args.port}, Nick: {args.name}, Channel: {args.channel}")

    # Create Bot instance
    bot = Bot(args.host, args.port, args.name, args.channel)

    try:
        bot.connect()
    except KeyboardInterrupt:
        print("Bot interrupted, shutting down...")
        bot.shutdown()
    finally:
        print("Bot has been closed.")

# Call the main function
if __name__ == "__main__":
    main()
