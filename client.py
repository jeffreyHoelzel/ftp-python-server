import socket as s
import threading as t
import regex as re
import os
import sys

# constants
SERVER_IP = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 2048
# regex pattern for matching filepaths
FILE_PATH_PATTERN = r'^(.+/)*[^/]+\.[a-zA-Z0-9]+$'

# remove excess characters used to specify file room chatting prompt in terminal
def clean_message(message):
    idx = message.find(">")
    if idx != -1:
        clean_message = message[idx + 3:]
        return clean_message
    return message

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
            elif re.match(FILE_PATH_PATTERN, message):
                get_file(message)
            else:
                print(message)
        except KeyboardInterrupt:
            print("Error occured trying to get username. Check UP and/or port.")
            client.close()
            break

def send_message():
    while True:
        message = input("")

        # check if pattern matches a file path
        if re.match(FILE_PATH_PATTERN, message):
            send_file(message)
        client.send(f"{username} >> {message}".encode("utf-8"))

        if message == "CLOSE":
            sys.exit(0)

def get_file(filename):
    # parse out username
    filename = clean_message(filename)

    # parse out file and size
    filename, file_size = filename.split(":")
    file_size = int(file_size)

    # send OK to other client
    client.send(f"Received {filename}".encode("utf-8"))

    # get path to save file
    full_path = os.path.join(".", filename) # saving to current directory

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

    print(f"{filename} successfully received. Verify your current directory.")

def send_file(filename):
    # check if file exists
    if not os.path.isfile(filename):
        print(f"{filename} does not exits in this directory.")
        return
    
    # get size of file
    file_size = os.path.getsize(filename)

    # send the filename and size
    client.send(f"{username} >> {os.path.basename(filename)}:{file_size}".encode("utf-8"))

    # get ACK
    client.recv(BUFFER_SIZE)

    # send contents of file
    with open(filename, "rb") as f:
        while True:
            # get parts of file in chunks
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client.sendall(bytes_read)

    print(f"{filename} sent successfully.")

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
    recv_thread.join(timeout=2)
    send_thread.join(timeout=2)
