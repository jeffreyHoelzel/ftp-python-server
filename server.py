################################################################################################################
# ***IMPORTANT DISCLAIMER***
# Some of the code used in this assignment was borrowed and/or modified from my Homework 2 assignment for CS460. 
# Jeffrey Hoelzel Jr
################################################################################################################

import socket as s
import sys
import threading as t

# constants
NUM_CONNECTIONS = 10
HOST_IP = "127.0.0.1" # localhost
PORT = 8080 # random port
BUFFER_SIZE = 2048

# global variable to handle server running
running = True

class FTPRoom:
    def __init__(self, room_name):
        self.name = room_name
        self.clients = []
        self.usernames = []

    # handle how the class should be displayed when printing
    def __str__(self):
        return self.name
    
    # handle how the class should be iterated over
    def __iter__(self):
        return iter(zip(self.clients, self.usernames))
    
    def add_clients(self, client, username):
        self.clients.append(client)
        self.usernames.append(username)

    def remove_clients(self, client, username):
        self.clients.remove(client)
        self.usernames.remove(username)

        # send close protocol to client program
        client.send("CLOSE".encode("utf-8"))
        client.close()

    def send_message(self, message):
        # send message to all clients in exchange room
        for client in self.clients:
            client.send(message) # file includes the entire path to file in host os

# prompts a user to join an existing, or set up a new FTP room
def ftp_room_prompt(ftp_rooms, client):
    # request and receive username from client
    client.send("USERNAME".encode("utf-8"))
    username = client.recv(BUFFER_SIZE).decode("utf-8")

    # send prompt message to user about setting up a new room or joining an existing one
    client.send(f"Welcome to the FTP server!\nYou can either join an existing FTP room or create a new one.\nEnter the name of the FTP room you wish to join or enter 'NEW' to create a new FTP room.\n(If none are listed, create one).\n\nSend any files you want! To quit, enter 'CLOSE'.\n".encode("utf-8"))

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
        
    # if each option fails, notify caller terminate the program
    print(f"{username} failed to specify either a new room to create or an existing one. Terminating connection.")
    client.close()
    sys.exit()

# remove excess characters used to specify file room chatting prompt in terminal
def clean_message(message):
    idx = message.find(">")
    if idx != -1:
        clean_message = message[idx + 3:]
        return clean_message
    return message

# handle file exchange between clients in ftp rooms
def handle_clients(ftp_room, client, username):
    while True:
        try:
            message = client.recv(BUFFER_SIZE).decode("utf-8")
            
            # check if client wants to leave the room
            if "CLOSE" in message:
                # remove client and notify server/room
                ftp_room.remove_clients(client, username)
                print(f"{username} has left {ftp_room}.")
                ftp_room.send_message(f"{username} has left the exchange room.".encode("utf-8"))
                break
            else:
                ftp_room.send_message(message.encode("utf-8")) # relays filepath to other clients
        except:
            # remove client on error
            print("Error receiving client message. Removing client.")
            ftp_room.remove_clients(client, username)
            break

if __name__ == "__main__":
    print(f"FTP server booting up...\n\nTo get started, connect a client.\n")

    # initialize socket
    server = s.socket(s.AF_INET, s.SOCK_STREAM) # TCP socket
    server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)

    server.bind((HOST_IP, PORT))
    print(f"{HOST_IP} bound to port {PORT}.")

    server.listen(NUM_CONNECTIONS)
    print("Listening for connections...")

    # file exchange rooms
    exchange_rooms = []

    # keep track of active threads
    active_threads = []

    try:
        while running:
            try:
                # set timeout to check for running flag
                server.settimeout(1.0) # one second to allow for quick shutdown

                try:
                    # display who just connected
                    client, address = server.accept()
                    print(f"Connected from {str(address)}.")

                    # get roomn name and username
                    room_name, username = ftp_room_prompt(exchange_rooms, client)

                    need_new_room = True

                    for room in exchange_rooms:
                        if room.name == room_name:
                            # get room in scope of main
                            ftp_room = room
                            ftp_room.add_clients(client, username)

                            # no need for new room since client just got added to existing room
                            need_new_room = False

                            print(f"{username} has joined {ftp_room}.")
                            ftp_room.send_message(f"{username} has joined the exchange room!".encode("utf-8"))
                            break

                    if need_new_room:
                        # create a new ftp room and add client
                        ftp_room = FTPRoom(room_name)
                        ftp_room.add_clients(client, username)
                        # add to list of known rooms
                        exchange_rooms.append(ftp_room)
                        
                        print(f"{username} has created a new exchange room.")
                        ftp_room.send_message(f"{username} has created an exchange room!".encode("utf-8"))

                    # create thread for current client
                    thread = t.Thread(target=handle_clients, args=(ftp_room, client, username,))
                    thread.start()

                    # add new thread to list of active threads
                    active_threads.append(thread)
                except s.timeout:
                    # ignore timeout, gives server opportunity to check for ctrl+c
                    pass
            except Exception as e:
                if running:
                    print(f"Error occured while handling clients: {e}.")

    except KeyboardInterrupt:
        # catch ctrl+c
        print("Server shutdown initiated.")
        running = False
    finally:
        # close server socket
        server.close()

        # remove all clients from each room
        for room in exchange_rooms:
            for client, username in room:
                room.remove_clients(client, username)

        # join all threads in list
        for thread in active_threads:
            thread.join(timeout=2) # add 2 second timeout to ensure smooth exit

        print("Server has been shutdown.")
        sys.exit(0)
