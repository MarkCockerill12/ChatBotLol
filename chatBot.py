import socket
import time

#Badly adding classes and objects WORK IN PROGRESS !!

class Bot: 

    def __init__(self, server="::1", port=6667, nick="BotLol", channel="#Test"):
    # Variables
        self.server = server
        self.port = port
        self.nick = nick
        self.channel = channel
        self.channel_info = {}
    

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
                Connected = Truee
                self.running_bot()

        except Exception as e:
        print(f"Socket error occurred: {e}")


    def running_bot(self):
        
        while self.Connected:
            data = s.recv(1024).decode('utf-8')
            if not data:
                print("Disconnected from server.")
                break
                
            print("Server Response:", data.strip())  # Debugging line to check server's response

            # Handle channel join confirmation
            if f":{nick}!{nick}@".lower() in data.lower() and "join".lower() in data.lower():
                print(f"Successfully joined {channel}. Sending message...")
                s.send(f"PRIVMSG {channel} :Hello {channel}. I am {nick}, the friendly chat Bot, say !help to find out how to talk to me.\r\n".encode('utf-8'))
                print(f"Message sent to {channel}: 'Hello {channel}.'")
                channel_info[channel] = {
                    'user': self.nick,
                    'channel': self.channel,
                    'timestamp': time.time(),
                    'server_response': data.strip()
                }
                print(f"Stored channel information: {self.channel_info[self.channel]}")

            # Check for PING message from server
            if data.startswith("PING"):
                ping_response = data.split()[1]
                self.s.send(f"PONG {ping_response}\r\n".encode('utf-8'))
                print(f"Sent PONG response to {ping_response}")

            # Handle messages from the channel
            if "PRIVMSG" in data:
                self.handle_privmsg(data)
                
                
                
    def handle_privmsg(self,data):
        sender = data.split('!', 1)[0][1:]
        message = data.split('PRIVMSG', 1)[1].split(':', 1)[1]

        print(f"Message from {sender}: {message}")

        if message.strip().lower() == "!quit":
            response = f"Alright, see ya, {sender}!"
            self.s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
            Connected = False
            print("Quitting...")

        elif message.strip().lower() == "!hello":
            response = f"Hello, {sender}!"
            self.s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
            print(f"Responded to {sender}: {response}")

        elif message.strip().lower() == "!help":
            response = "!hello - I will say hello back to you. !quit - I will say goodbye and leave the channel. !savedata - I will show you the stored channel information."
            self.s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
            print(f"Responded to {sender}: {response}")

        elif message.strip().lower() == "!savedata":
            if channel in channel_info:
            response = f"Stored channel information: {channel_info[channel]}"
            self.s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
            print(f"Responded to {sender}: {response}")
        
            else:
                response = "No channel information saved yet."
                self.s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
                print(f"Responded to {sender}: {response}")

        else:
            response = f"You're so right, {sender}! You're so amazing!"
            self.s.send(f"PRIVMSG {channel} :{response}\r\n".encode('utf-8'))
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

        runbot= bot(server,port,nick,channel)
        
        try:
            runbot.connect()
        except KeyboardInterrupt:
            print("Bot interrupted, closing connection...")
        finally:
            print("Connection closed.")
    


    # Exception handling
        #except KeyboardInterrupt:
        # print("Bot interrupted, closing connection...")
        #except socket.error as e:
        # print(f"Socket error occurred: {e}")
        #except Exception as e:
            #print(f"An unexpected error occurred: {e}")
        #finally:
            #print("Connection closed.")