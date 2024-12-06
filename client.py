################################################################################################################
# ***IMPORTANT DISCLAIMER***
# Some of the code used in this assignment was borrowed and/or modified from my Homework 2 assignment for CS460. 
# Jeffrey Hoelzel Jr
################################################################################################################

import socket as s
import threading as t
import regex as re
import os
import sys

# constants
SERVER_IP = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096
# regex pattern for matching filepaths
FILE_PATH_PATTERN = r'^(.+/)*[^/]+\.[a-zA-Z0-9]+$'

# remove excess characters used to specify file
def clean_file(file_info):
    # remove the prefix "{username} >> ", but keep sender name
    sender, file_info = file_info.split(" >> ", 1)
    return sender, file_info

def get_message():
    while True:
        try:
            message = client.recv(BUFFER_SIZE).decode("utf-8")
            if message == "USERNAME":
                client.send(username.encode("utf-8"))
            elif message == "NEW":
                client.send(f"{username}'s exchange room".encode("utf-8"))
            elif message == "CLOSE":
                client.close()
                print("You have left the exhange room. Ending program.")
                sys.exit(0)
            # handle file exchange
            elif message.startswith("FILE:"):
                # remove FILE: from message
                file_info = message[5:]
                # replace \ with / for windows users
                file_info = file_info.replace("\\", "/")
                # parse out username
                sender, file_info = clean_file(file_info)
                # check that username did not send this file
                if sender == username:
                    continue # prevent sender from reading their own file
                get_file(file_info)
            else:
                print(message)
        except Exception as e:
            print(f"Error occured in get_message: {e}.")
            client.close()
            break

def send_message():
    while True:
        message = input("")

        # check if pattern matches a file path
        if re.match(FILE_PATH_PATTERN, message):
            filename = message.replace("\\", "/")
            send_file(filename)
        client.send(f"{username} >> {message}".encode("utf-8"))

        if message == "CLOSE":
            sys.exit(0)

def get_file(file_info):
    # parse out file and size
    filename, file_size_str = file_info.split(":")
    file_size = int(file_size_str)

    print(f"Receiving file '{filename}' ({file_size} bytes).")

    # get path to save file
    full_path = os.path.join(".", os.path.basename(filename)) # saving to current directory

    # get all file contents
    with open(full_path, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            # read in chunks
            chunk = client.recv(min(BUFFER_SIZE, file_size - bytes_received))
            # no more chunks usually means done
            if not chunk:
                break
            f.write(chunk)
            bytes_received += len(chunk)

    print(f"{filename} successfully received. {username} verify your current directory.")

def send_file(file_path):
    # check if file exists
    if not os.path.isfile(file_path):
        print(f"{file_path} does not exits in this directory.")
        return
    
    # get size of file
    file_size = os.path.getsize(file_path)
    # get filename
    filename = os.path.basename(file_path)

    # send the filename and size
    client.send(f"FILE:{username} >> {filename}:{file_size}".encode("utf-8"))

    # send contents of file
    with open(file_path, "rb") as f:
        while True:
            # get parts of file in chunks
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client.sendall(bytes_read)

    print(f"{file_path} sent successfully.")

if __name__ == "__main__":
    username = input("Enter your username: ")

    # set up client socket
    client = s.socket(s.AF_INET, s.SOCK_STREAM)
    client.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)

    # connect client to server
    client.connect((SERVER_IP, PORT))
    print(f"Connection client to server\n    IP Adress: {SERVER_IP}\n    PORT: {PORT}\n")

    # set up thread to get messages/files
    recv_thread = t.Thread(target=get_message)
    recv_thread.start()

    # set up thread to send messages/files
    send_thread = t.Thread(target=send_message)
    send_thread.start()

    # join threads when done
    recv_thread.join()
    send_thread.join()
