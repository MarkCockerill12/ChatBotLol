import socket
import select
import time
import sys


class Client:

    def setNick(self, nickName, permissions, realName):
        self.NICK = nickName
        self.permissions = permissions
        self.realname = realName

    def updateNick(self, nickName):
        self.NICK = nickName

    def getNick(self):
        return self.NICK

    def getTennis(self):
        return self.ping

    def setUser(self, USERarr):
        self.USER = USERarr

    def setSocketObj(self, socketObject):
        self._ownSocketObj = socketObject

    def getSocketObj(self):
        return self._ownSocketObj

    def sendData(self, data):
        self._ownSocketObj.sendall(data.encode('utf-8'))

    def setPing(self, b):
        self.ping = b
    
    def setTennis(self, b:bool):
        self.ping = b

    def __init__(self):
        self.ping = False
        self.NICK = ""
        self.USER = [None,None,None]
        self.realname = ""
        self._ownSocketObj = None

    def __init__(self,NICK):
        self.ping = False
        self.NICK = NICK
        self.USER = [None,None,None]
        self.realname = ""
        self._ownSocketObj = None

class Channel:
    def __init__(self):
        self.clients = {}  # Dictionary of users in the channel, key as NICK and value as Client class

    def addClient(self, client):
        self.clients[client.getNick()] = client

    def removeClient(self, client):
        if client.getNick() in self.clients:
            removedClient = self.clients.pop(client.getNick())
            return removedClient
        return None

    def getListOfClients(self):
        return self.clients.keys()


class Server:
    def __init__(self):
        self.tennis = False
        self.timeDifference = 0
        self.timeFirst = time.time()
        self.channels = {}  # Dictionary of channel classes with key as channel name and value as class
        self.clients = {}  # Dictionary of users in the server, key as NICK and value of Client class
        self.main()

    def sendData(self, data, client):
        try:
            encodedData = data.encode("utf-8")
            client.getSocketObj().sendall(encodedData)
            client.setPing(True)
            print("Data sent:", data)
        except socket.error as e:
            print(f"Error sending data: {e}")

    def receiveData(self, readable):
        try:
            receiveData = readable.recv(1024).decode()
            if receiveData:
                self.tennis = True
                self.timeFirst = time.time()
                return receiveData
        except socket.error as e:
            print(f"Error receiving data: {e}")
            return None  # Return None on error

    def operation(self, command):

        #error codes:
        #NICK: ERR_NONICKNAMEGIVEN, ERR_ERRONEUSNICKNAME, ERR_NICKNAMEINUSE
        #USER: ERR_NEEDMOREPARAMS, ERR_ALREADYREGISTRED, ERR_TOOMANYARGUMENTS
        #JOIN: ERR_NEEDMOREPARAMS
        #PING: ERR_NOORIGIN
        #QUIT: ERR_NOORIGIN
        if command[0] == "NICK":
            return self.setNick(command[1])

        elif command[0] == "USER":
            return self.setUser(command[1], command[2])

        elif command[0] == "PONG":
            return self.PONG()

        elif command[0] == "QUIT":
            return self.quit()

        elif command[0] == "JOIN":
            return self.joinChannel(command[1])

        else:
            print("Unknown command:", command[0])
            return f":Error: Unknown command {command[0]}"

    def setNick(self, nickname):
        if len(nickname) > 15 or len(nickname) < 3:
            return "ERR_ERRONEUSNICKNAME"
        if nickname in self.clients:
            return "ERR_NICKNAMEINUSE"
        self.clients[nickname] = Client(nickname)
        self.clients[nickname].setSocketObj(self.tempClient.getSocketObj())
        welcome_message = f":Welcome to the IRC, {nickname}!"
        self.sendData(welcome_message, self.clients[nickname])
        print(f"Nickname set to: {nickname}")

    def setUser(self, username, realname):
        if username in self.clients:
            self.clients[username].setUser([username, realname[1:]])
            return None
        return "ERR_ALREADYREGISTERED"

    def joinChannel(self, channel):
        if channel not in self.channels:
            self.channels[channel] = Channel()
        self.channels[channel].addClient(self.tempClient)
        self.sendData(f":{self.tempClient.getNick()} has joined {channel}", self.channels[channel])
        print(f"{self.tempClient.getNick()} has joined {channel}")
        irc = f":{self.tempClient.getNick()}!{self.tempClient.getNick()}@{self.tempClient.getNick()} JOIN {channel}"
        self.sendData(irc, self.tempClient)
        

    def quit(self):
        if self.tempClient.getNick() in self.clients:
            self.sendData(f":{self.tempClient.getNick()} has left the server.", self.tempClient)
            self.clients.pop(self.tempClient.getNick()).getSocketObj().close()

    def PONG(self):
        print("PONG received")

    def checkCommand(self, data):
        if not data:
            return

        sections = data.split()
        temp = []
        response = None

        for s in sections:
            if s == "NICK":
                index = sections.index(s)
                temp = [sections[index], sections[index + 1]]
                response = self.operation(temp)

            elif s == "USER":
                index = sections.index(s)
                if len(sections[index:]) < 5:
                    return "ERR_TOOMANYARGUMENTS"

                try:
                    temp = [sections[index], sections[index + 1], sections[index + 4]]
                    response = self.operation(temp)

                except IndexError as e:
                    print(e)
                    response = "ERR_NEEDMOREPARAMS"

            if response:
                return response
        
    def QUIT(self):
        removedClient = self.clients.pop(self.currentClient.getNick())
        removedClient.getSocketObj().close()

    def NICK(self, nickname:str):
        if self.newClient:
            # Add client to the dictionary
            self.clients[nickname] = Client(nickname)
            self.clients.pop(self.tempClient.getNick())
            self.clients[nickname].setSocketObj(self.tempClient.getSocketObj())
            self.tempClient.setSocketObj(None)

            self.clients[nickname].upadateNick(nickname)
            welcome_message = "CAP * LS :"
            self.sendData(welcome_message, self.clients[nickname])
            print(f"Nickname set to: {nickname}")
        
        else:
            self.clients[self.client].upadateNick(nickname)
            self.clients[nickname] = self.clients.pop(self.client)

    def USER(self, username:str, realname:str): # as host name and server name are not used for this project, they are ignored.
        self.clients[username].setUser([username, realname[1:]]) 

    def JOIN(self, channel):
        """ Handles join command. """
        if not channel:
            raise ValueError("No channel provided.")
        if channel not in self.channels:
            self.channels[channel] = Channel()
        self.channels[channel].clients[self.temp] = self.clients[self.temp]
        print(f"{self.temp} has joined {channel}")

    def PING(self):
        """ Handles PING command. """
        self.timeFirst = time.time()
        if not self.tennis and self.timeDifference > 60:
            self.sendData("PING %s" %(self.clients[0]))
            pass
        elif self.tennis == False:
            self.timeDifference = self.timeFirst - time.time()
            print("PING sent")

    def PONG(self):
        """ Handles PONG command. """
        self.timeDifference = self.timeFirst - time.time()
        print("PONG received")

    def addClientToReadableList(self):
        readable = []
        for client in self.clients.values():
            readable.append(client.getSocketObj())  # In same order as clients dictionary
        return readable

    def main(self):
        port = 6667
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.soc.bind(('', port))
        print("Socket binded to %d" % (port))

        self.soc.listen(5)
        print("Socket listening")

        while True:
            readable = [self.soc] + self.addClientToReadableList()
            readConnection, _, _ = select.select(readable, [], [], 1.0)

            for con in readConnection:
                if con is self.soc:  # Adds new client to the server
                    self.tempSocketObject = con.accept()
                    self.tempClient = Client("temp")
                    self.tempClient.setSocketObj(self.tempSocketObject[0])
                    self.clients[self.tempClient.getNick()] = self.tempClient
                    print("New client connected.")

                    # Send welcome message immediately after accepting a new client
                    welcome_message = f":Welcome to the IRC, {self.tempClient.getNick()}!"
                    self.sendData(welcome_message, self.tempClient)
                else:  # Checks for commands from existing clients
                    for client in list(self.clients.values()):  # Use list to avoid RuntimeError
                        if con == client.getSocketObj():
                            self.tempClient = client
                            data = self.receiveData(con)
                            response = self.checkCommand(data)

                            if response:
                                self.sendData(response, self.tempClient)

                    self.tennis = False

    
    def __init__(self):
        self.tennis = False
        self.timeDifference = 0
        self.timeFirst = time.time()
        #self.checkCommand("NICK edwardFoster")
        self.channels = {} # will be dictionary of channel classes with key as channel name and value as class
        self.clients = {} # will be dictionary of users in the server, key as NICK and value of client class
        self.main()


if __name__ == "__main__":
    server = Server()
