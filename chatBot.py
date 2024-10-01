import socket
import time

#Added classes and method structure for the bot, definetly needs improving though.

class Bot: 

    def __init__(self, server="::1", port=6667, nick="BotLol", channel="#Test"):
    # Making an instance of bot class 
        self.server = server
        self.port = port
        self.nick = nick
        self.channel = channel
        self.channel_info = {}
        self.Connected = False
    

    # Welcome!


    # Improved socket handling with explicit connection closing

    def connect(self):
        try:
            with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as self.s:
                print(f"Connecting to {self.server}:{self.port}...")
                self.s.connect((self.server, self.port))

                # Sends Nick and User to join the server using user inputs
                self.s.send(f"NICK {self.nick}\r\n".encode('utf-8'))
                self.s.send(f"USER {self.nick} 0 * :{self.nick}\r\n".encode('utf-8'))

                # Joins the specified channel
                self.s.send(f"JOIN {self.channel}\r\n".encode('utf-8'))

                # Wait for server's response before sending a message
                self.Connected = True
                self.running_bot()

        except Exception as e:
            print(f"Socket error occurred: {e}")

  
    def running_bot(self):
        
        
        while self.Connected:
            data = self.s.recv(1024).decode('utf-8')
            if not data:
                print("Disconnected from server.")
                break
                
            print("Server Response:", data.strip())  # Debugging line to check server's response

            # Handle channel join confirmation
            if f":{self.nick}!{self.nick}@".lower() in data.lower() and "join".lower() in data.lower():
                print(f"Successfully joined {self.channel}. Sending message...")
                self.s.send(f"PRIVMSG {self.channel} :Hello {self.channel}. I am {self.nick}, the friendly chat Bot, say !help to find out how to talk to me.\r\n".encode('utf-8'))
                print(f"Message sent to {self.channel}: 'Hello {self.channel}.'")
                self.channel_info[self.channel] = {
                    'user': self.nick,
                    'channel': self.channel,
                    'timestamp': time.time(),
                    'server_response': data.strip()
                }
                print(f"Stored channel information: {self.channel_info[self.channel]}")

            # Check for PING message from server - Needs updating
            if data.startswith("PING"):
                ping_response = data.split()[1]
                self.s.send(f"PONG {ping_response}\r\n".encode('utf-8'))
                print(f"Sent PONG response to {ping_response}")

            # Handle messages from the channel
            if "PRIVMSG" in data:
                self.handle_privmsg(data)
                
                
                
    def handle_privmsg(self,data):
        #Handling for messages 

        sender = data.split('!', 1)[0][1:]
        message = data.split('PRIVMSG', 1)[1].split(':', 1)[1]

        print(f"Message from {sender}: {message}")

        if message.strip().lower() == "!quit":
            response = f"Alright, see ya, {sender}!"
            self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
            self.Connected = False
            print("Quitting...")

        elif message.strip().lower() == "!hello":
            response = f"Hello, {sender}!"
            self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
            print(f"Responded to {sender}: {response}")

        elif message.strip().lower() == "!help":
            response = "!hello - I will say hello back to you. !quit - I will say goodbye and leave the channel. !savedata - I will show you the stored channel information."
            self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
            print(f"Responded to {sender}: {response}")

        elif message.strip().lower() == "!savedata":
            if self.channel in self.channel_info:
                response = f"Stored channel information: {self.channel_info[self.channel]}"
                self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
                print(f"Responded to {sender}: {response}")
            
            else:
                response = "No channel information saved yet."
                self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
                print(f"Responded to {sender}: {response}")

        else:
            response = f"You're so right, {sender}! You're so amazing!"
            self.s.send(f"PRIVMSG {self.channel} :{response}\r\n".encode('utf-8'))
            print(f"Responded to {sender}: {response}")

    


if __name__ == "__main__":

        # User Inputs
        server = input("Please enter your desired server, if you don't enter anything it will default to '::1': ") or "::1"

        # Bot asks for desired port and defaults to 6667
        try:
            port = int(input("Please enter your desired port, if you don't enter anything it will default to 6667: ") or "6667")
        except ValueError:
            print("Invalid port number. Using default port 6667.")
            port = 6667

        nick = input("Please enter your desired nickname, if you don't enter anything it will default to BotLol: ") or "BotLol"
        channel = input("What channel should the bot join? If you don't enter anything it will default to #Test: ") or "#Test"

        runbot= Bot(server,port,nick,channel)
        
        try:
            runbot.connect()
        except KeyboardInterrupt:
            print("Bot interrupted, closing connection...")
        finally:
            print("Connection closed.")
    


    # Exception handling- needs to be added back in
        #except KeyboardInterrupt:
        # print("Bot interrupted, closing connection...")
        #except socket.error as e:
        # print(f"Socket error occurred: {e}")
        #except Exception as e:
            #print(f"An unexpected error occurred: {e}")
        #finally:
            #print("Connection closed.")