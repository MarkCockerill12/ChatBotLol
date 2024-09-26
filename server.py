import socket
import sys
import time

class Server:
    
    def sendData(self,data):
        self.checkCommand(data)
        self.socOb.send(data.encode())

        self.tennis = True
        self.timeFirst = time.time()

    def receiveData(self):
        
        receiveData = ""
        while True: 
            receiveData = self.socOb.recv(1024).decode()
            if receiveData:
                self.tennis = True
                self.timeFirst = time.time()
                return receiveData
            else: return None
        

    def checkCommand(self, data):
        # do regex in here to check commands match the correct formats. 
        sections = data.split()
        
        print(sections)
        for s in sections:
            match s:
                case "NICK":
                    self.clients[sections[1]] = Client(sections[1])
                    self.temp = [sections[1]]
                case "USER":
                    if type(self.temp) == str:
                        pass
                        #self.clients[self.temp]
                    pass

                case "PONG":
                    pass
                case "JOIN":
                    print("Asked to join ", sections[1])
                
            

    def NICK(self):
        pass
    def USER(self):
        pass
    def JOIN(self):
        pass

    def PING(self):
        pass

    def main(self):
        self.timeFirst = time.time()
        if not self.tennis & self.timeDifference > 60:
            #send ping
            pass
        elif self.tennis == False:
            self.timeDifference = self.timeFirst - time.time()
        
        port = 6667
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.soc.bind(('',port))
        print("Socket binded to %d" %(port))

        self.soc.listen(5)
        print("Socket listening")

        while True:
            self.socOb, self.addr = self.soc.accept()
            #print("Connecting from %s" %(self.addr))
            #print(self.receiveData())
            #self.sendData("Thanks for connecting")
            self.checkCommand(self.receiveData())

            self.tennis = False

    def __init__(self):
        self.tennis = False
        self.timeDifference = 0
        self.timeFirst = time.time()
        #self.checkCommand("NICK * edwardFoster")
        self.channels = {} # will be dictionary of channel classes with key as channel name and value as class
        self.clients = {} # will be dictionary of users in the server, key as NICK and value of client class
        self.main()


class Client:

    def setNick(self):
        pass

    def setUser(self, USERarr:[str, str, str, str]):
        self.USER = USERarr

    def __init__(self,NICK):
        self.NICK = NICK
        self.USER = None[4]



    def __init__(self):
        self.NICK = ""
        self.USER = None[4]

class Channel:
    def __init__(self):
        self.clients = {} # will be dictionary of users in the channel, key as NICK and value of client class



test = Server()
