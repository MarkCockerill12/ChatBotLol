import socket
import time
import random
import re

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
        self.command_prefix = "!"  # Define your command prefix here

        # Initialize jokes list here
        self.jokes = [
            "Why don't programmers like nature? It has too many bugs.",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
            "Why do Java developers wear glasses? Because they don’t see sharp.",
            "Why did the developer go broke? Because they used up all their cache.",
            "I told my computer I needed a break, and now it won’t stop sending me KitKats!"
            "hawk tuah"
        ]

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
        # Extract sender, target and message
        sender = data.split('!', 1)[0][1:]  # Extracts the sender (e.g., username)
        target = data.split('PRIVMSG', 1)[1].split(':', 1)[0].strip()  # The target (could be the bot's nick or a channel)
        message = data.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()  # The message itself

        print(f"Message from {sender} to {target}: {message}")

        # Check if the message is a private message directed to the bot
        if target.lower() == self.nick.lower():  # Check if the message is directed to the bot
            # Respond with a random joke for private messages
            joke = random.choice(self.jokes)
            self.s.send(f"PRIVMSG {sender} :{joke}\r\n".encode('utf-8'))  # Send joke back to sender
            print(f"Sent a joke to {sender}: {joke}")
        
        elif message.startswith(self.command_prefix):  # If it's a command
            # Process commands as usual
            parts = message[len(self.command_prefix):].strip().split()
            command = parts[0].lower()  # First part is the command
            args = parts[1:]  # Remaining parts are arguments (if any)
            
            match command:
                case "quit":
                    response = f"Alright, see ya, {sender}!"
                    self.send_message(response)
                    self.Connected = False
                    print("Quitting...")
                    self.shutdown()

                case "hello":
                    response = f"Hello, {sender}!"
                    self.send_message(response)

                case "help":
                    response = "!hello - I will say hello back to you. !quit - I will say goodbye and leave the channel. !savedata - I will show you the stored channel information. !privmsg <user> <message> - Send a private message to a user."
                    self.send_message(response)

                case "savedata":
                    if self.channel in self.channel_info:
                        response = f"Stored channel information: {self.channel_info[self.channel]}"
                    else:
                        response = "No channel information saved yet."
                    self.send_message(response)

                case "privmsg":
                    # Handle the privmsg command, requires at least one argument (the user)
                    if len(args) > 1:
                        user = args[0]  # The first argument is the user
                        priv_message = ' '.join(args[1:])  # The rest of the arguments form the message
                        response = f"Private message to {user}: {priv_message}"
                        self.s.send(f"PRIVMSG {user} :{priv_message}\r\n".encode('utf-8'))
                        print(f"Sent private message to {user}: {priv_message}")
                    else:
                        self.send_message("Usage: !privmsg <user> <message>")
                
                case "slap":
                    # Handle the slap command, requires at least one argument (the recipient).
                    if len(args) >= 1:
                        user = args[0]
                        if user.lower() == self.nick.lower() or user.lower() == sender.lower():
                            response = "I can't slap myself or the sender!"
                        
                        else:
                            #Input validation to check if slap victim is a user in user list
                            self.s.send(f"NAMES {self.channel}\r\n".encode('utf-8'))

                            user_list = self.user_search()
    
                            if user.lower() in [u.lower() for u in user_list]:
                                 response = f"\x01ACTION slaps {user} around a bit with a large trout\x01" 
                            else:
                                response = f"\x01ACTION slaps {sender} because {user} is not a user in the server\x01"
                        
                        self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
                        print(f"Sent slap action for {user}")
                    
                    
                    else:
                        self.send_message("Usage: !slap <user>")
                
                case _:
                    response = f"Unknown command, {sender}. Try !help for a list of commands."
                    self.send_message(response)

        else:
            # Handle non-command messages sent to the channel
            if target.lower() == self.channel.lower():  # Ensure we're only responding to channel messages
                response = f"You're so right, {sender}! You're so amazing!"
                self.send_message(response)

    def shutdown(self):
        try:
            if self.s:
                self.s.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error while closing socket: {e}")

    def user_search(self):
        user_list = []

        while True:
            data = self.s.recv(2048).decode('utf-8')

            #search parameters need refining maybe
            #Basically it searches for 353 in data as it comes before the list of names then it recieves and then reads in all the data after the : 
            match = re.search(r"353 .* = .* :(.*)", data)

            if match:
                # Extract the list of users and split them into a list
                users = match.group(1).split()
                user_list.extend(users)
                
                
          # 366 code indicates the end of the NAMES list
            if ' 366 ' in data:
                break  # End of user list
            
        return user_list


# Main function
def main():
    if __name__ == "__main__":
        # Welcome message
        print("  ________  ___  ___  ________  _________        ________  ________  _________   ")
        print(" |\   ____\|\  \|\  \|\   __  \|\___   ___\     |\   __  \|\   __  \|\___   ___\ ")
        print(" \ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     \ \  \|\ /\ \  \|\  \|___ \  \_| ")
        print("  \ \  \    \ \   __  \ \   __  \   \ \  \       \ \   __  \ \  \\\  \   \ \  \  ")
        print("   \ \  \____\ \  \ \  \ \  \ \  \   \ \  \       \ \  \|\  \ \  \\\  \   \ \  \ ")
        print("    \ \_______\ \__\ \__\ \__\ \__\   \ \__\       \ \_______\ \_______\   \ \__\ ")
        print("     \|_______|\|__|\|__|\|__|\|__|    \|__|        \|_______|\|_______|    \|__|")

        # User Inputs
        server = input("Please enter your desired server, default is '::1': ") or "::1"

        try:
            port = int(input("Please enter your desired port, default is 6667: ") or 6667)
        except ValueError:
            print("Invalid port. Defaulting to 6667.")
            port = 6667

        nick = input("Please enter your nickname, default is 'BotLol': ") or "BotLol"
        channel = input("Enter channel name, default is '#Test': ") or "#Test"

        # Create Bot instance
        bot = Bot(server, port, nick, channel)

        try:
            bot.connect()
        except KeyboardInterrupt:
            print("Bot interrupted, shutting down...")
            bot.shutdown()
        finally:
            print("Bot has been closed.")

# Call the main function
main()
