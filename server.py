import socket
import select
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
    
    def operation(self, operat):
        if operat == "NICK":
            self.NICK()
        elif operat == "USER":
            self.USER()
        elif operat == "PONG":
            pass
        elif operat == "QUIT":
            pass
        elif operat == "JOIN":
            pass
        else:
            print("unknown command")
    

    def checkCommand(self, data):
        # do regex in here to check commands match the correct formats. 
        sections = data.split()
        print("checking")
        print(sections)

        for s in sections:
            match s:
                case "NICK":
                    try: 
                        self.operation(temp[0])
                    except:
                        pass

                    temp = ["NICK"]
                    
                case "USER":
                    try: 
                        self.operation(temp[0])
                    except:
                        pass

                    temp = ["USER"]

                case "PONG":
                    try: 
                        self.operation(temp[0])
                    except:
                        pass

                    temp = ["PONG"]
                
                case "JOIN":
                    try: 
                        self.operation(temp[0])
                    except:
                        pass

                    print("Asked to join ", sections[1])
                
            temp.append[s]


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
        if not self.tennis and self.timeDifference > 60:
            self.sendData("PING %s" %(self.clients[0]))
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
            readable = [self.soc]
            writeable = []
            errable = []

            read, write, e = select.select(readable, writeable, errable,1.0)
            if read:
                self.socOb, self.addr = self.soc.accept()
                self.checkCommand(self.receiveData())
            elif write:
                self.checkCommand(self.receiveData())
            else:
                print("Check")

            
            #print("Connecting from %s" %(self.addr))
            #print(self.receiveData())
            #self.sendData("Thanks for connecting")
            #self.checkCommand(self.receiveData())

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

    def setUser(self, USERarr:list[str, str, str, str]):
        self.USER = USERarr

    def __init__(self):
        self.NICK = ""
        self.USER = [None,None,None,None]

    def __init__(self,NICK):
        self.NICK = NICK
        self.USER = [None,None,None,None]





class Channel:
    def __init__(self):
        self.clients = {} # will be dictionary of users in the channel, key as NICK and value of client class



test = Server()
