################################################################################################################
# ***IMPORTANT DISCLAIMER***
# Much of the code used in this assignment was borrowed and/or modified from my Homework 2 assignment for CS460. 
# Jeffrey Hoelzel Jr
################################################################################################################

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

# prompts a user to join an existing, or set up a new FTP room
def ftp_room_prompt(ftp_rooms, client):
    # request and receive username from client
    client.send("USERNAME".encode("utf-8"))
    username = client.recv(BUFFER_SIZE).decode("utf-8")

    # send prompt message to user about setting up a new room or joining an existing one
    client.send(f"Welcome to the FTP server!\nYou can either join an existing FTP room or create a new one.\nEnter the name of the FTP room you wish to join or enter 'NEW' to create a new FTP room.\n(If none are listed, create one).\n\nSend any files you want! To quit, enter 'CLOSE'".encode("utf-8"))

    # display rooms if available
    if len(ftp_rooms) != 0:
        for room in ftp_rooms:
            client.send(f"   {room}\n".encode("utf-8"))
    else:
        client.send("There are no rooms available to join. Create a new one!".encode("utf-8"))

    # get client response
    raw_choice = client.recv(BUFFER_SIZE).decode("utf-8")
    cleaned_choice = clean_message(raw_choice) # remove any chat modifications to string

    if "NEW" in cleaned_choice:
        # request and receive room name
        client.send("NEW".encode("utf-8"))
        raw_room_name = client.recv(BUFFER_SIZE).decode("utf-8")
        cleaned_room_name = clean_message(raw_room_name)

        # return room name and username to caller
        return cleaned_room_name, username
    
    # otherwise, figure out which room clients wants to join and return
    for room in ftp_rooms:
        if room.name == cleaned_choice:
            return cleaned_choice, username
        
    # if each option fails, notify caller and return empty string
    print(f"{username} failed to specify either a new room to create or an existing one.")
    return "error", "error"





def clean_message(message):
    pass

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
