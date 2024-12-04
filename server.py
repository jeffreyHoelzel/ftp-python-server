import socket
import sys
import time
import os

# constants
NUM_CONNECTIONS = 10
HOST_IP = '127.0.0.1' # localhost
PORT = 8080 # random port
BUFFER_SIZE = 2048

class FTPRoom:
    def __init__(self, room_name):
        self.name = room_name
        self.clients = []
        self.usernames = []

    def __str__(self):
        return self.name
    
    def add_clients(self, client, username):
        self.clients.append(client)
        self.usernames.append(username)

    def remove_clients(self, client, username):
        self.clients.remove(client)
        self.usernames.remove(username)

        # send close protocol to client program
        client.send("CLOSE".encode("utf-8"))
        client.close()

    def send_file(self, file):
        # send file to all clients in exchange room
        for client in self.clients:
            client.send(file) # file includes the entire path to file in host os



if __name__ == '__main__':
    print(f"FTP server booting up...\n\nTo get started, connect a client.\n")

    # initialize socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST_IP, PORT))
    print(f"{HOST_IP} bound to port {PORT}.")

    server.listen(NUM_CONNECTIONS)
    print("Listening for connections...")

    # file exchange rooms
    exchange_rooms = []

    while True:
        # display who just connected
        connection, address = server.accept()
        print(f"Connected from {str(address)}.")
