import socket
import select
import time
import sys


class Client:

    def setNick(self, nickName, permissions, realName):
        self.NICK = nickName
        self.permissions = permissions
        self.realname = realName

    def upadateNick(self, nickName):
        self.NICK = nickName

    def getNick(self):
        return self.NICK

    def getTennis(self):
        return ping

    def setUser(self, USERarr:list[str, str, str]):
        self.USER = USERarr

    def setSocketObj(self, socketObject):
        self._ownSocketObj = socketObject

    def getSocketObj(self):
        return self._ownSocketObj

    def sendData(self,data):
        self._ownSocketObj.sendall(bytes(data))
    
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
        self.clients = {} # will be dictionary of users in the channel, key as NICK and value of client class
    
    def addClient(self, client):
        self.clients[client.getNick()] = client

    def removeClient(self, client):
        removedClient = self.clients.pop(client.getNick())
        return removedClient

    def getListofClients(self):
        return self.clients.keys()


class Server:
    
    def sendData(self, data, client:Client):
        try:
            print("attempt to send")
            encodedData = data.encode("utf-8")
            client.getSocketObj().sendall(encodedData)
            #client.sendData(data.encode("utf-8"))
            client.setTennis(True)
            print("Data sent")

        except socket.error as e:
            print(f"Error sending data: {e}")

    def receiveData(self, readable:socket.socket):
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
            if len(command[1]) > 15 or len(command[1]) < 3:
                print("1")
                return "ERR_ERRONEUSNICKNAME"
            elif command[1] in self.clients:
                print("2")
                return "ERR_NICKNAMEINUSE"
            else:
                self.NICK(command[1])
                response = f"Welcome {command[1]}"

        elif command[0] == "USER":
            if command[2][0] != ":":
                print("Real name must start with a colon")
                return "ERR_INCORRECTFORMAT"
            else:
                self.USER(command[1], command[2])
                response = f"User {command[1]} registered as {command[2]}"

        elif command[0] == "PONG":
            self.PONG()
            pass
        elif command[0] == "QUIT":
            if command[1][0] != ":":
                return "ERR_INCORRECTFORMAT"
            
            self.QUIT()

        elif command[0] == "JOIN":
            if not command[1]:
                return "NOTICE %s:No channel provided"%(command[1])
            elif self.channels[command[1]]:
                self.JOIN(command[1])
                response = f"Joined channel {command[1]}"
            else:
                self.channels[command[1]] = Channel()
                self.JOIN(command[1])
                response = f"Channel {command[1]} created and joined"
                return 0

        else:
            print("unknown command")
    

    def checkCommand(self, data):
        if not data:
            print("No data received")
            return
        
        print(f"Data received: {data}")
        sections = data.split()
        print(f"Command sections: ", sections)
        temp = []
        response = None

        for s in sections:
            if s == "NICK":
                try:
                    index = sections.index(s)
                    temp = [sections[index], sections[index+1]]
                    self.operation(temp)
                except IndexError as e:
                    print(e)
                    response = "ERR_NEEDMOREPARAMS"

            elif s == "USER":
                index = sections.index(s)
                if len(sections[index:]) > 5:
                    return "ERR_TOOMANYARGUMENTS"
                
                try:
                    
                    temp = [sections[index], sections[index+1], sections[index+4]]
                    self.operation(temp)

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
            
        if self.tempClient is None:
            raise ValueError("No client provided.")
        self.channels[channel].addClient(self.clients)
        welcome_message = f"Welcome to {channel}, {self.tempClient.getNick()}"
        self.sendData(welcome_message, self.tempClient)

        for client in self.channels[channel].getListofClients():
            if client != self.temp:
                self.sendData(f"{self.temp} has joined {channel}", self.clients[client])

        print(f"{self.tempClient.getNick()} has joined {channel}")
        #self.channels[channel].clients[self.temp] = self.clients[self.temp]
        #print(f"{self.temp} has joined {channel}")
 

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
            readable.append(client.getSocketObj()) # In same order as clients dictionary
        return readable

    def main(self):

        port = 6667
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.soc.bind(('',port))
        print("Socket binded to %d" %(port))

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
            
            for con in readConnection:
                if con is self.soc: # Adds new client to the server
                    self.newClient = True
                    self.tempSocketObject = con.accept()
                    self.tempClient = Client("temp")
                    self.tempClient.setSocketObj(self.tempSocketObject[0])
                    currentClient = self.tempClient.getNick()
                    self.clients[currentClient] = self.tempClient
                    response = self.checkCommand(self.receiveData(self.tempSocketObject[0]))

                else: # Checks for commands from existing clients
                    self.newClient = False
                    for client in self.clients.values():
                        if con == client.getSocketObj():
                            self.client = client.getNick()
                            currentClient = client.getNick()
                            break
                    response = self.checkCommand(self.receiveData(con))
                try:
                    match response:
                        case "ERR_ERRONEUSNICKNAME":
                            response = ":%s :Erroneus nickname" %(self.tempClient.getNick())
                        case "ERR_NICKNAMEINUSE":
                            response = ":%s :Nickname is already in use" %(self.tempClient.getNick())
                        case "ERR_NEEDMOREPARAMS":
                            response = ":%s :Not enough parameters" %(self.tempClient.getNick())
                        case "ERR_TOOMANYARGUMENTS":
                            response = ":%s :Too many arguments" %(self.tempClient.getNick())
                        case "ERR_INCORRECTFORMAT":
                            response = ":%s :Incorrect format" %(self.tempClient.getNick())

                    self.sendData(response, currentClient)
                except:
                    pass

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
    test = Server()
