import socket
import sys
import time

class Server:
    def __init__(self):
        # Data structures for managing clients and channels
        self.tennis = False
        self.timeDifference = 0
        self.timeFirst = time.time()
        self.channels = {}  # Dictionary of channel classes
        self.clients = {}   # Dictionary of users in the server
        self.temp = None    # Temporary variable for current user
        self.port = 6667    # Server port
        self.setup_server()

    def setup_server(self):
        """ Initializes and sets up the server socket. """
        self.soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        try:
            self.soc.bind(('', self.port))
            print(f"Socket bound to {self.port}")
        except socket.error as e:
            print(f"Error binding socket: {e}")
            sys.exit(1)

        self.soc.listen(5)
        print("Socket listening")

        while True:
            try:
                self.socOb, self.addr = self.soc.accept()
                print(f"Connection from {self.addr}")
                self.handle_client()
            except socket.error as e:
                print(f"Error during connection: {e}")
                continue  # Handle connection errors gracefully

    def handle_client(self):
        """ Handles client communication. """
        client_data = self.receiveData()
        if client_data:
            self.checkCommand(client_data)
        else:
            print("No data received from the client.")

    def sendData(self, data):
        """ Sends data to the connected client. """
        try:
            self.socOb.send(data.encode())
            self.tennis = True
            self.timeFirst = time.time()
        except socket.error as e:
            print(f"Error sending data: {e}")

    def receiveData(self):
        """ Receives data from the connected client. """
        try:
            receiveData = self.socOb.recv(1024).decode()
            if receiveData:
                self.tennis = True
                self.timeFirst = time.time()
                return receiveData
        except socket.error as e:
            print(f"Error receiving data: {e}")
            return None  # Return None on error

    def checkCommand(self, data):
        """ Checks the command received from the client. """
        sections = data.split()
        
        if len(sections) < 2:
            self.sendData("ERROR: Insufficient command parameters.")
            return

        command = sections[0]
        nickname = sections[1] if len(sections) > 1 else None

        try:
            match command:
                case "NICK":
                    self.handle_nick(nickname)

                case "USER":
                    if self.temp is None:
                        raise ValueError("User must set a nickname before using USER command.")
                    # Handle USER command logic here

                case "PONG":
                    # Handle PONG logic here
                    pass

                case "JOIN":
                    print("Asked to join", sections[1])

                case _:
                    self.sendData(f"ERROR: Unknown command '{command}'")

        except ValueError as ve:
            print(f"Nickname error: {ve}")
            self.sendData(f"ERROR: {ve}")  # Notify the client of the error

    def handle_nick(self, nickname):
        """ Handles the NICK command and validates the nickname. """
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

class Client:
    def __init__(self, NICK):
        self.NICK = NICK
        self.USER = [None] * 4  # Initialize user array with None

    def setUser(self, USERarr):
        self.USER = USERarr

class Channel:
    def __init__(self):
        self.clients = {}  # Dictionary of users in the channel

# Start the server
if __name__ == "__main__":
    test = Server()
