import socket
import select
import time

class Client:

    def setNick(self, nickName, permissions, realName):
        self.NICK = nickName
        self.permissions = permissions
        self.realname = realName
        print("x")

    def upadateNick(self, nickName):
        self.NICK = nickName

    def getNick(self):
        return self.NICK
        

    def setUser(self, USERarr:list[str, str, str]):
        self.USER = USERarr
        print("a")

    def setSocketObj(self, socketObject):
        self._ownSocketObj = socketObject

    def getSocketObj(self):
        return self._ownSocketObj

    def __init__(self):
        self.NICK = ""
        self.USER = [None,None,None]
        self.realname = ""
        self._ownSocketObj = None

    def __init__(self,NICK):
        self.NICK = NICK
        self.USER = [None,None,None]
        self.realname = ""
        self._ownSocketObj = None






class Channel:
    def __init__(self):
        self.clients = {} # will be dictionary of users in the channel, key as NICK and value of client class


class Server:
    
    def sendData(self,data):
        try:
            print("attempt to send")

            self.tempSocketObject[0].sendall(bytes(data, 'utf-8'))

            self.tennis = True
            self.timeFirst = time.time()
        except socket.error as e:
            print(f"Error sending data: {e}")

    def receiveData(self, readable:socket.socket):
        try:           
            receiveData = readable.recv(1024).decode()
            if receiveData:
                self.tennis = True
                self.timeFirst = time.time()
                return receiveData
            else:
                print("Read time out")
                return None
                
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
                return "ERR_ERRONEUSNICKNAME"
            elif command[1] in self.clients:
                return "ERR_NICKNAMEINUSE"
            else:
                self.NICK(command[1])
            
        elif command[0] == "USER":
            if command[3][0] != ":":
                print("Real name must start with a colon")
                return "ERR_INCORRECTFORMAT"

            self.USER(command[1:])

        elif command[0] == "PONG":
            pass
        elif command[0] == "QUIT":
            pass
        elif command[0] == "JOIN":
            if not command[1]:
                return "NOTICE %s:No channel provided"%(command[1])
            elif self.channels[command[1]]:
                self.JOIN(command[1])
            else:
                self.channels[command[1]] = Channel()
                self.JOIN(command[1])
                return 0

        else:
            print("unknown command")
    

    def checkCommand(self, data):
        # do regex in here to check commands match the correct formats. 
        if not data:
            return
        
        sections = data.split()
        print(sections)
        temp = []
        response = None

        for s in sections:
            if s == "NICK":
                try:
                    index = sections.index(s)
                    temp = [sections[index], sections[index+1]]
                    self.operation(temp)
                except IndexError:
                    response = "ERR_NEEDMOREPARAMS"

            elif s == "USER":
                index = sections.index(s)
                if len(sections) < 5:
                    return "ERR_TOOMANYARGUMENTS"
                
                try:
                    temp = [sections[index], sections[index+1], sections[index+4]]
                    self.operation(temp)
                except IndexError:
                    response = "ERR_NEEDMOREPARAMS"

            if response:
               return response
            

    def NICK(self, nickname:str):

        # Add client to the dictionary
        self.clients[nickname] = Client(nickname)
        self.clients.pop(self.tempClient.getNick())
        self.clients[nickname].setSocketObj(self.tempClient.getSocketObj())
        self.tempClient.setSocketObj(None)

        self.clients[nickname].upadateNick(nickname)
        welcome_message = f"Welcome, {nickname}!"
        self.sendData(welcome_message)
        print(f"Nickname set to: {nickname}")

    def USER(self, username:str, realname:str): # as host name and server name are not used for this project, they are ignored.
        name = realname[1:]
        self.clients[username].setUser([username, name]) 

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
        self.sendData("PONG")
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
        index = 0
        
        while True:
            readable.clear()
            readable.append(self.soc)
            readable.extend(self.addClientToReadableList())

            readConnection, readCommand, e = select.select(readable, writable, [], 1.0)

            for con in readConnection:
                if con == self.soc:
                    self.tempSocketObject = con.accept()
                    self.tempClient = Client("temp")
                    self.tempClient.setSocketObj(self.tempSocketObject[0])
                    self.clients[self.tempClient.getNick()] = self.tempClient
                    response = self.checkCommand(self.receiveData(self.tempSocketObject[0]))
                    if response:
                        match response:
                            case "ERR_ERRONEUSNICKNAME":
                                self.sendData(":%s :Erroneus nickname" %(self.tempClient.getNick()))
                            case "ERR_NICKNAMEINUSE":
                                self.sendData(":%s :Nickname is already in use" %(self.tempClient.getNick()))
                            case "ERR_NEEDMOREPARAMS":
                                self.sendData(":%s :Not enough parameters" %(self.tempClient.getNick()))
                            case "ERR_TOOMANYARGUMENTS":
                                self.sendData(":%s :Too many arguments" %(self.tempClient.getNick()))
                            case "ERR_INCORRECTFORMAT":
                                self.sendData(":%s :Incorrect format" %(self.tempClient.getNick()))

                        self.sendData(response)

                
                    

                
                self.checkCommand(self.receiveData(con))





            # if readConnection:
            #     tempSocketObject = self.soc.accept() #connecting client to server
            #     time.sleep(0.2)                
            #     self.checkCommand(self.receiveData([tempSocketObject[0]]))
            #     tempArr = []
            #     for client in self.clients.values():
            #         tempArr.append(client)
            #     tempArr[index].setSocketObj(tempSocketObject[0])
            #     # [index].setSocketObj(tempSocketObject[0])

            # else:
            #     if self.clients:
            #         for client in self.clients.values():
            #             tempSocketObject = [client.getSocketObj()]
            #             self.checkCommand(self.receiveData([tempSocketObject[0]]))
            
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