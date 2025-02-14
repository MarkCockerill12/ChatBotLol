import socket
import select
import time
import random

class Client:
    def __init__(self, NICK=""):
        self.ping = False
        self.tennis = False
        self.NICK = NICK
        self.USER = [None, None, None]
        self.realname = ""
        self._ownSocketObj = None

    def setNick(self, nickName, permissions, realName):
        self.NICK = nickName
        self.permissions = permissions
        self.realname = realName

    def updateNick(self, nickName):
        self.NICK = nickName

    def getNick(self):
        return self.NICK

    def getPing(self):
        return self.ping

    def setUser(self, USERarr: list[str]):
        self.USER = USERarr

    def setSocketObj(self, socketObject):
        self._ownSocketObj = socketObject

    def getSocketObj(self):
        return self._ownSocketObj

    def sendData(self, data):
        self._ownSocketObj.sendall(data.encode("utf-8"))

    def setPing(self, b: bool):
        self.ping = b

    def setTennis(self, b: bool):
        self.tennis = b
        self.ping = b

class Channel:
    def __init__(self):
        self.clients = {}  # Dictionary of users in the channel, key as NICK and value as Client object

    def addClient(self, client):
        self.clients[client.getNick()] = client
        print(f"Client {client.getNick()} added to channel")

    def removeClient(self, client):
        removedClient = self.clients.pop(client.getNick(), None)
        if removedClient:
            print(f"Client {client.getNick()} removed from channel")
        return removedClient

    def getListofClients(self):
        return self.clients.keys()

class Server:
    def sendData(self, data, client: Client):
        try:
            if client.getSocketObj() is None:
                print("Client's socket object is not set.")
                return
            print(f"Data to send: {data} (type: {type(data)})")
            encodedData = data.encode("utf-8")
            client.getSocketObj().sendall(encodedData)
            client.setTennis(True)
            print("Data sent")
        except AttributeError as e:
            print(f"AttributeError: {e} - Data: {data} (type: {type(data)})")
        except Exception as e:
            print(f"Error: {e} - Data: {data} (type: {type(data)})")
            self.removeClient(client)

    def removeClient(self, client: Client):
        try:
            client.getSocketObj().close()
        except Exception as e:
            print(f"Error closing socket for client {client.getNick()}: {e}")
        finally:
            if client.getNick() in self.clients:
                del self.clients[client.getNick()]
                print(f"Client {client.getNick()} removed from server.")

    def receiveData(self, readable: socket.socket):
        try:
            receiveData = readable.recv(1024).decode()
            if receiveData:
                self.tennis = True
                self.timeFirst = time.time()
                # Check if the message is channel-specific
                if receiveData.startswith("PRIVMSG"):
                    parts = receiveData.split()
                    if len(parts) > 2 and parts[1].startswith("#"):
                        channel = parts[1]
                        message = ' '.join(parts[2:])[1:]  # Extract the message part correctly
                        self.broadcast(message, self.client, channel)  # Broadcast to the specific channel
                    else:
                        message = ' '.join(parts[2:])[1:]  # Extract the message part correctly
                        self.broadcast(message, self.client)  # Broadcast to all clients e,krbgyelfuygicbgy.iwu
                else:
                    self.broadcast(receiveData, self.client)  # Broadcast to all clients
                return receiveData
        except socket.error as e:
            print(f"Error receiving data: {e}")
            return None  # Return None on error

    def handlePrivmsg(self, sender_nick, target_nick, message):
        print("okay the thing in server for priv mesg is working")
        if target_nick in self.clients:
            print("still working 1")
            client = self.clients[target_nick]
            formatted_message = f":{sender_nick}!{sender_nick}@localhost PRIVMSG {target_nick} :{message}\r\n"
            print(f"Sending private message: {formatted_message}")
            self.sendData(formatted_message, client)
            print(f"Private message sent from {sender_nick} to {target_nick}: {message}")
            print("still working 2")
        else:
            print(f"User {target_nick} not found.")

    def checkCommand(self, data):
        if not data:
            return "ERR_NODATA"

        sections = data.split()
        print(f"Received sections: {sections}")
        response = None

        for i, s in enumerate(sections):
            if s == "NICK":
                response = self.operation(sections[i:i+2])
            elif s == "USER":
                response = self.operation(sections[i:i+4])
            elif s == "JOIN":
                response = self.operation(sections[i:i+2])
            elif s == "PONG":
                response = self.operation(sections[i:i+1])
            elif s == "QUIT":
                nick = sections[i-1].split('!')[0][1:]  # Extract the nickname of the client quitting
                self.currentCLient = self.clients.get(self.client)
                response = self.operation(sections[i:i+2])
            elif s == "NAMES":
                response = self.operation(sections[i:i+2])
            elif s == "PRIVMSG":
                if len(sections) >= 3:
                    sender_nick = sections[0].split('!')[0][1:]  # Extract sender's nickname
                    target_nick = sections[1]
                    message = ' '.join(sections[2:])
                    print(f"Parsed !privmsg command: sender_nick={sender_nick}, target_nick={target_nick}, message={message}")
                    self.handlePrivmsg(sender_nick, target_nick, message)
                else:
                    print("Incorrect format for !privmsg command.")
            elif s == "PONG":
                response = self.operation(sections[i:i+2])
            else:
                continue

        if response:
            return response
        else:
            return None  # Return None instead of ERR_UNKNOWNCOMMAND32

    def operation(self, command):
        print(f"Operation called with command: {command}")
        if command[0] == "NICK":
            if len(command[1]) > 15 or len(command[1]) < 3:
                return "ERR_ERRONEUSNICKNAME"
            elif command[1] in self.clients:
                return "ERR_NICKNAMEINUSE"
            self.NICK(command[1])
            return "NICK set successfully"  # return message

        elif command[0] == "USER":
            if command[2][0] != ":":
                print("Real name must start with a colon")
                return "ERR_INCORRECTFORMAT"

            self.USER(command[1], command[2])

        elif command[0] == "PONG":
            self.PONG()
            return None 



        elif command[0] == "QUIT":
            if command[1][0] != ":":
                return "ERR_INCORRECTFORMAT"

            self.QUIT()

        elif command[0] == "JOIN":
            if not command[1]:
                return "NOTICE %s:No channel provided" % (command[1])
            elif command[1] in self.channels:
                self.JOIN(command[1], self.client)
            else:
                self.channels[command[1]] = Channel()
                self.JOIN(command[1], self.client)
                print("the code is here 2")
            return None  # Return None to avoid sending "JOIN command processed"
        
        elif command[0] == "NAMES":
            # Ensure a channel name is provided
            if len(command) < 2 or not command[1]:
                return "NOTICE %s: No channel provided" % (self.client)
            namechannel = command[1]
            # Check if the channel exists
            if namechannel not in self.channels:
                return "NOTICE %s: No such channel" % (self.client)
            self.NAMES(namechannel,self.client)

        elif command[0] == "PONG":
            self.PONG()
            return None  # No response needed
            

        else:
            print("unknown command")
            print("The problem is here 2")
            return "ERR_UNKNOWNCOMMAND"

    def QUIT(self):
        if self.currentClient is None:
            print("Error: No client to remove.")
            return
        removedClient = self.clients.pop(self.currentClient.getNick())
        if removedClient:
            removedClient.getSocketObj().close()
            print(f"Client {self.currentClient.getNick()} removed from server.")
        else:
            print(f"Error: Client {self.currentClient.getNick()} not found.")
        

    def validate_nickname(self, nickname):
        user_list = self.user_search()  # Get list of users in the channel
        while nickname.lower() in [user.lower() for user in user_list]:
            nickname += str(random.randint(1, 9))  # Append a random number to the nickname
        return nickname


    def NICK(self, nickname: str):
        #self.nick = self.validate_nickname(self.nick)
        if self.newClient:
            # Ensure the temporary client exists in the dictionary before changing its nickname
            if "temp" in self.clients:
                # Add client to the dictionary with new nickname
                self.clients[nickname] = self.clients.pop("temp")
                self.clients[nickname].updateNick(nickname)
                self.clients[nickname].setSocketObj(self.tempClient.getSocketObj())
                
                welcome_message = "CAP * LS :"
                self.sendData(welcome_message, self.clients[nickname])
                print(f"Nickname set to: {nickname}")
                return f"NICK set successfully {nickname}"  # return message with new nickname
            else:
                print("Error: Temporary client not found.")
        else:
            # Update the existing client's nickname
            if self.client in self.clients:
                self.clients[self.client].updateNick(nickname)
                self.clients[nickname] = self.clients.pop(self.client)
            else:
                print(f"Error: Client {self.client} not found.")

    def USER(self, username: str, realname: str):  # as host name and server name are not used for this project, they are ignored.
        if not realname.startswith(':'):
            realname = ':' + realname  # Ensure the real name starts with a colon
        if username in self.clients:
            self.clients[username].setUser([username, realname[1:]])
        else:
            print(f"Error: Client {username} not found.")

    def JOIN(self, channel, client_name):
        if not channel:
            raise ValueError("No channel provided.")
        if channel not in self.channels:
            self.channels[channel] = Channel()
            print(f"Channel {channel} created.")

        self.channels[channel].addClient(self.clients[client_name])
        print(f"{client_name} has joined {channel}")

        # Send confirmation to the client
        join_message = f":{client_name}!{client_name}@localhost JOIN {channel}\r\n"
        self.sendData(join_message, self.clients[client_name])

        # Send the topic of the channel (assuming no topic for simplicity)
        topic_message = f":localhost 332 {client_name} {channel} :No topic is set\r\n"
        self.sendData(topic_message, self.clients[client_name])

        # Send the names of the users in the channel
        names = ' '.join(self.channels[channel].getListofClients())
        names_message = f":localhost 353 {client_name} = {channel} :{names}\r\n"
        self.sendData(names_message, self.clients[client_name])

        # End of names list
        end_names_message = f":localhost 366 {client_name} {channel} :End of /NAMES list\r\n"
        self.sendData(end_names_message, self.clients[client_name])

    def NAMES(self, namechannel, client_name):
        names = ' '.join(self.channels[namechannel].getListofClients())
        names_message = f":localhost 353 {client_name} = {namechannel} :{names}\r\n"

        end_names_message = f":localhost 366 {client_name} {namechannel} :End of /NAMES list\r\n"
    
        # Combine both messages into one
        combined_message = names_message + end_names_message
    
        # Send the combined message to the client
        self.sendData(combined_message, self.clients[client_name])

    def PING(self):
        current_time = time.time()
        for nick, client in self.clients.items():
            if not client.getPing() and (current_time - self.timeFirst > 60):
                ping_id = str(int(current_time))  # Using the current time as a unique ID
                self.sendData(f"PING {ping_id}\r\n", client)
                print("PING sent to:", client.getNick())
                client.setPing(True)
            
            elif client.getPing():
                # This would mean we received a PONG response
                client.setPing(False)




    def PONG(self):
        print(f"yaay")         

    def addClientToReadableList(self):
        readable = []
        for client in self.clients.values():
            readable.append(client.getSocketObj())  # In same order as clients dictionary
        return readable

    def broadcast(self, message, sender_nick, channel=None):
        if channel:
            # Broadcast to all clients in the specified channel
            print("THIS IS SENDING TO THE CHANNEL: ", channel)
            if channel in self.channels:
                print(f"Clients in channel {channel}: {list(self.channels[channel].clients.keys())}")
                for nick, client in self.channels[channel].clients.items():
                    if nick != sender_nick:  # Don't send the message back to the sender
                        formatted_message = f":{sender_nick}!{sender_nick}@localhost PRIVMSG {channel} :{message}\r\n"
                        self.sendData(formatted_message, client)
                        print("THIS IS SENDING TO THE CLIENT: ", nick)
                        print("THIS IS THE MESSAGE: ", formatted_message)
            else:
                print(f"Channel {channel} does not exist.")
        #else:
        #     # Broadcast to all clients
        #     print("Broadcasting to all clients")
            # for nick, client in self.clients.items():
            #     if nick != sender_nick:  # Don't send the message back to the sender
            #         formatted_message = f":{sender_nick}!{sender_nick}@localhost PRIVMSG {nick} :{message}\r\n"
            #         self.sendData(formatted_message, client)
        #             print("THIS IS SENDING TO THE CLIENT: ", nick)
        #             print("THIS IS THE MESSAGE: ", formatted_message)

    def main(self):
        port = 6667
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.soc.bind(('', port))
        print("Socket binded to %d" % (port))

        self.soc.listen(5)
        print("Socket listening")

        readable = []
        writable = []
        self.tempSocketObject = []
        response = None

        while True:
            readable.clear()
            readable.append(self.soc)
            readable.extend(self.addClientToReadableList())

            readConnection, readCommand, e = select.select(readable, writable, [], 1.0)

            if not readConnection:
                self.PING()  # Send a PING if no data is being read

            
            for con in readConnection:
                if con is self.soc:  # Adds new client to the server
                    self.newClient = True
                    self.tempSocketObject = con.accept()
                    self.tempClient = Client("temp")
                    self.tempClient.setSocketObj(self.tempSocketObject[0])
                    currentClient = self.tempClient.getNick()
                    self.clients[currentClient] = self.tempClient
                    self.client = currentClient  # Set the client attribute
                    response = self.checkCommand(self.receiveData(self.tempSocketObject[0]))

                else:  # Checks for commands from existing clients
                    self.newClient = False
                    for client in self.clients.values():
                        if con == client.getSocketObj():
                            self.client = client.getNick()  # Set the client attribute
                            currentClient = client.getNick()
                            break
                    response = self.checkCommand(self.receiveData(con))
                try:
                    if response:  # Ensure response is not None
                        if currentClient == "temp" and response.startswith("NICK set successfully"):
                            currentClient = response.split()[-1]  # Extract the new nickname
                            self.client = currentClient  # Update the client attribute

                        self.sendData(response, self.clients[currentClient])
                        # Check if the response is channel-specific
                        if response.startswith("PRIVMSG"):
                            parts = response.split()
                            if len(parts) > 2 and parts[1].startswith("#"):
                                channel = parts[1]
                                self.broadcast(response, currentClient, channel)  # Broadcast to the specific channel
                            else:
                                self.broadcast(response, currentClient)  # Broadcast to all clients
                        else:
                            self.broadcast(response, currentClient)  # Broadcast to all clients
                except KeyError as e:
                    print(f"KeyError: {e} - Client {currentClient} not found.")
                except Exception as e:
                    print(f"Error: {e}")
                    if currentClient in self.clients:
                        self.removeClient(self.clients[currentClient])


                self.tennis = False

    def __init__(self):
        self.clients = {}
        self.currentClient = None
        self.tennis = False
        self.timeDifference = 0
        self.timeFirst = time.time()
        self.channels = {}  # Dictionary of channel classes with key as channel name and value as class
        self.clients = {}  # Dictionary of users in the server, key as NICK and value of client class
        self.main()

if __name__ == "__main__":
    test = Server()