import socket
import select
import time


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
        self.clients = {}  # will be dictionary of users in the channel, key as NICK and value of client class

    def addClient(self, client):
        self.clients[client.getNick()] = client

    def removeClient(self, client):
        removedClient = self.clients.pop(client.getNick())
        return removedClient

    def getListofClients(self):
        return self.clients.keys()


class Server:

    def sendData(self, data, client: Client):
        try:
            if client.getSocketObj() is None:
                print("Client's socket object is not set.")
                return
            print("attempt to send")
            print(f"Data to send: {data} (type: {type(data)})")
            encodedData = data.encode("utf-8")
            print("attempt to send1")
            client.getSocketObj().sendall(encodedData)
            print("attempt to send2")
            client.setTennis(True)
            print("Data sent")
        except AttributeError as e:
            print(f"AttributeError: {e} - Data: {data} (type: {type(data)})")
        except Exception as e:
            print(f"Error: {e} - Data: {data} (type: {type(data)})")
        except socket.error as e:
            print(f"Error sending data: {e}")

    def receiveData(self, readable: socket.socket):
        try:
            receiveData = readable.recv(1024).decode()
            if receiveData:
                self.tennis = True
                self.timeFirst = time.time()
                return receiveData

        except socket.error as e:
            print(f"Error receiving data: {e}")
            return None  # Return None on error

    def checkCommand(self, data):
        if not data:
            return "ERR_NODATA"

        sections = data.split()
        print(f"Received sections: {sections}")
        temp = []
        response = None

        for i, s in enumerate(sections):
            if s == "NICK":
                try:
                    temp = [sections[i], sections[i + 1]]
                    response = self.operation(temp)
                    print(f"NICK command processed: {temp}")
                except IndexError as e:
                    print(e)
                    response = "ERR_NEEDMOREPARAMS"
                    break  # Exit the loop if an error occurs

            elif s == "USER":
                if len(sections[i:]) > 5:
                    response = "ERR_TOOMANYARGUMENTS"
                    break  # Exit the loop if too many arguments

                try:
                    temp = [sections[i], sections[i + 1], sections[i + 4]]
                    response = self.operation(temp)
                    print(f"USER command processed: {temp}")
                except IndexError as e:
                    print(e)
                    response = "ERR_NEEDMOREPARAMS"
                    break  # Exit the loop if an error occurs

            elif s == "JOIN":
                try:
                    temp = [sections[i], sections[i + 1]]
                    response = self.operation(temp)
                    print(f"JOIN command processed: {temp}")
                except IndexError as e:
                    print(e)
                    response = "ERR_NEEDMOREPARAMS"
                    break  # Exit the loop if an error occurs

            # Add more command handling as needed

        if response:
            return response
        else:
            return "ERR_UNKNOWNCOMMAND"  # Return an error for unknown commands

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
            pass
        elif command[0] == "QUIT":
            if command[1][0] != ":":
                return "ERR_INCORRECTFORMAT"

            self.QUIT()

        elif command[0] == "JOIN":
            if not command[1]:
                return "NOTICE %s:No channel provided" % (command[1])
            elif command[1] in self.channels:
                self.JOIN(command[1], self.client)
                print("the code is here 1")
            else:
                self.channels[command[1]] = Channel()
                self.JOIN(command[1], self.client)
                print("the code is here 2")
            return "JOIN command processed"

        else:
            print("unknown command")
            return "ERR_UNKNOWNCOMMAND"

    def QUIT(self):
        removedClient = self.clients.pop(self.currentClient.getNick())
        removedClient.getSocketObj().close()

    def NICK(self, nickname: str):
        if self.newClient:
            # Add client to the dictionary
            self.clients[nickname] = Client(nickname)
            self.clients.pop(self.tempClient.getNick())
            self.clients[nickname].setSocketObj(self.tempClient.getSocketObj())
            self.tempClient.setSocketObj(None)

            self.clients[nickname].updateNick(nickname)
            welcome_message = "CAP * LS :"
            self.sendData(welcome_message, self.clients[nickname])
            print(f"Nickname set to: {nickname}")

        else:
            self.clients[self.client].updateNick(nickname)
            self.clients[nickname] = self.clients.pop(self.client)

    def USER(self, username: str, realname: str):  # as host name and server name are not used for this project, they are ignored.
        self.clients[username].setUser([username, realname[1:]])

    def JOIN(self, channel, client_name):
        print("The join function is called")
        if not channel:
            raise ValueError("No channel provided.")
        if channel not in self.channels:
            self.channels[channel] = Channel()

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


    def PING(self):
        """ Handles PING command. """
        self.timeFirst = time.time()
        if not self.tennis and self.timeDifference > 60:
            self.sendData("PING %s" % (self.clients[0]))
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

        readable = []
        writable = []
        self.tempSocketObject = []
        response = None

        while True:
            readable.clear()
            readable.append(self.soc)
            readable.extend(self.addClientToReadableList())

            readConnection, readCommand, e = select.select(readable, writable, [], 1.0)
            readConnection, _, _ = select.select(readable, writable, [], 1.0)
            for con in readConnection:
                if con is self.soc:  # Adds new client to the server
                    self.newClient = True
                    self.tempSocketObject = con.accept()
                    self.tempClient = Client("temp")
                    self.tempClient.setSocketObj(self.tempSocketObject[0])
                    currentClient = self.tempClient.getNick()
                    self.clients[currentClient] = self.tempClient
                    response = self.checkCommand(self.receiveData(self.tempSocketObject[0]))

                else:  # Checks for commands from existing clients
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
                            response = ":%s :Erroneus nickname" % (self.tempClient.getNick())
                        case "ERR_NICKNAMEINUSE":
                            response = ":%s :Nickname is already in use" % (self.tempClient.getNick())
                        case "ERR_NEEDMOREPARAMS":
                            response = ":%s :Not enough parameters" % (self.tempClient.getNick())
                        case "ERR_TOOMANYARGUMENTS":
                            response = ":%s :Too many arguments" % (self.tempClient.getNick())
                        case "ERR_INCORRECTFORMAT":
                            response = ":%s :Incorrect format" % (self.tempClient.getNick())
                        case "JOIN":
                            self.JOIN(response.split()[1])

                    self.sendData(response, self.clients[currentClient])
                except:
                    pass

                self.tennis = False

    def __init__(self):
        self.tennis = False
        self.timeDifference = 0
        self.timeFirst = time.time()
        self.channels = {}  # will be dictionary of channel classes with key as channel name and value as class
        self.clients = {}  # will be dictionary of users in the server, key as NICK and value of client class
        self.main()


if __name__ == "__main__":
    test = Server()