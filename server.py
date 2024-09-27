import socket
import select
import time

class Client:

    def setNick(self, nickName, permissions, realName):
        self.NICK = nickName
        self.permissions = permissions
        self.realname = realName
        print("x")

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

            self.socOb.sendall(bytes(data, 'utf-8'))

            self.tennis = True
            self.timeFirst = time.time()
        except socket.error as e:
            print(f"Error sending data: {e}")

    def receiveData(self, readable:list[socket]):
        try:            
            r, w, e = select.select(readable, [], [], 1.0)
            if r:
                receiveData = readable[0].recv(1024).decode()
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
        if command[0] == "NICK":
            self.NICK(command[1])
        elif command[0] == "USER":
            self.USER(command[1], command[2], command[4])
        elif command[0] == "PONG":
            pass
        elif command[0] == "QUIT":
            pass
        elif command[0] == "JOIN":
            print("join")
        else:
            print("unknown command")
    

    def checkCommand(self, data):
        # do regex in here to check commands match the correct formats. 
        if not data:
            return
        
        sections = data.split()
        print(sections)
        temp = []

        for s in sections:
            match s:
                case "NICK":
                    try: 
                        self.operation(temp)
                    except:
                        pass

                    temp = []
                    
                case "USER":
                    try: 
                        self.operation(temp)
                    except:
                        pass

                    temp = []

                case "PONG":
                    try: 
                        self.operation(temp)
                    except:
                        pass

                    temp = []
                
                case "JOIN":
                    try: 
                        self.operation(temp)
                    except:
                        pass
                    temp = []

            temp.append(s)
        try: 
            self.operation(temp)
        except:
            pass


    def NICK(self, nickname):

        if not nickname:
            raise ValueError("No nickname provided.")
        if len(nickname) < 3 or len(nickname) > 15:
            raise ValueError("Nickname must be between 3 and 15 characters.")
        if not nickname.isalnum():
            raise ValueError("Nickname can only contain alphanumeric characters.")
        if nickname in self.clients:
            raise ValueError(f"Nickname '{nickname}' is already taken. Please choose another.")

        # Add client to the dictionary
        self.clients[nickname] = Client(nickname)
        self.temp = nickname
        welcome_message = f"Welcome, {nickname}!"
        self.sendData(welcome_message)
        print(f"Nickname set to: {nickname}")

    def USER(self, username:str, permission:str, realname:str):
        if realname[0] != ":":
            return 0
        permissions = permission.split()
        for p in permissions:
            permissions[permissions.index(p)] = int(p)
        name = realname.strip(":")

        self.clients[username].setUser([username, permissions, name]) 
        


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

    def main(self):

        
        port = 6667
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.soc.bind(('',port))
        print("Socket binded to %d" %(port))

        self.soc.listen(5)
        print("Socket listening")
        readable = [self.soc]
        writable = []
        tempSocketObject = []
        index = 0
        while True:
            readConnection, readCommand, e = select.select(readable, writable, [],1.0)

            if readConnection:
                tempSocketObject = self.soc.accept() #connecting client to server
                time.sleep(0.2)                
                self.checkCommand(self.receiveData([tempSocketObject[0]]))
                tempArr = []
                for client in self.clients.values():
                    tempArr.append(client)
                tempArr[index].setSocketObj(tempSocketObject[0])
                # [index].setSocketObj(tempSocketObject[0])

            else:
                if self.clients:
                    for client in self.clients.values():
                        tempSocketObject = [client.getSocketObj()]
                        self.checkCommand(self.receiveData([tempSocketObject[0]]))
            
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