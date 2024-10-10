import socket
import time
import argparse
import os
import re
import random

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
        self.current_users = []

    def handle_messages(self, data):
        if "PRIVMSG" in data:
            self.handle_privmsg(data)
        elif "332" in data:  # Topic of the channel
            self.handle_topic(data)
        elif "353" in data:  # Names list
            self.handle_names(data)
        elif "366" in data:  # End of names list
            self.handle_end_of_names(data)
        else:
            print(f"Unhandled message: {data.strip()}")

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            print(f"Connecting to {self.server}:{self.port}...")
            self.s.connect((self.server, self.port))

            # Send NICK and USER commands
            self.s.send(f"NICK {self.nick}\r\n".encode('utf-8'))
            self.s.send(f"USER {self.nick} 0 * :{self.nick}\r\n".encode('utf-8'))

            self.Connected = True
            print(f"Connected as {self.nick}. Joining channel {self.channel}...")
            self.join_channel()
            self.running_bot()  # Start receiving messages

        except Exception as e:
            print(f"Connection error: {e}")
            self.shutdown()

    def join_channel(self):
        try:
            self.s.send(f"JOIN {self.channel}\r\n".encode('utf-8'))
            print(f"Bot joining channel {self.channel}")
            # Wait for server response to confirm join
            while True:
                data = self.s.recv(1024).decode('utf-8')
                print(f"Server Response: {data.strip()}")
                if f"JOIN {self.channel}" in data:
                    print(f"Successfully joined channel {self.channel}")
                    # Send welcome message
                    self.send_message(f"Hello everyone! I'm {self.nick}. Type !help to see what I can do.")
                    break
                elif "ERR" in data:
                    print(f"Error joining channel: {data.strip()}")
                    break
        except Exception as e:
            print(f"Error joining channel: {e}")

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

                # Handle messages
                self.handle_messages(data)

            except Exception as e:
                print(f"Error while receiving data: {e}")
                self.Connected = False
                self.shutdown()

    def handle_topic(self, data):
        print(f"Channel topic: {data.strip()}")

    def handle_names(self, data):
        print(f"Names list: {data.strip()}")
        # Extract and update the current users in the channel
        names = data.split(':')[-1].strip().split()
        self.current_users = names

    def handle_end_of_names(self, data):
        print(f"End of names list: {data.strip()}")

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
                        self.send_message(random.choice(jokedata))
                    else:
                        self.send_message(f"Sorry {sender}, I couldn't find any jokes.")
            else:
                self.send_message(f"Sorry {sender}, I couldn't find the jokes file.")

        elif message.startswith(self.command_prefix):  # If it's a command
            parts = message[len(self.command_prefix):].strip().split()

            # Input validation for if parts list is empty E.G the user inputs "!"
            if len(parts) == 0:
                self.send_message(f"Unknown Command, use !help for a list of the commands.")
                return

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
                    # Calls on user_Search method to get list of users in the channel
                    user_list = self.user_search()
                    if len(args) >= 1:
                        user = args[0]
                        
                        # Input Validations for Slap command
                        # If slap victim is either the bot or sender
                        if user.lower() == self.nick.lower() or user.lower() == sender.lower():
                            response = "I can't slap myself or the sender!"
                        elif user.lower() in [u.lower() for u in user_list]:
                            response = f"{sender} slaps {user} around a bit with a large trout!"
                        else:
                            response = f"User {user} not found."
                    else:
                        # If user list contains only user and bot
                        if len(user_list) <= 2:
                            response = "No one to slap!"
                        else:
                            response = f"{sender} slaps everyone around a bit with a large trout!"
                            
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
        finally:
            self.Connected = False
            print("Bot has been shut down.")

    def user_search(self):
        user_list = []
        self.s.send(f"NAMES {self.channel}\r\n".encode('utf-8'))  # Fetch user list
        # Set a timeout for recv to avoid blocking

        try:
            while True:
                data = self.s.recv(2048).decode('utf-8')
                match = re.search(r"353 .* = .* :(.*)", data)  # Reads data after 353 which indicates start of user list

                if match:
                    user_list.extend(match.group(1).split())

                if ' 366 ' in data:                    
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