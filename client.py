import socket as s
import threading as t
import regex as re
import sys

# constants
SERVER_IP = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 2048
# regex pattern for matching filepaths
FILE_PATH_PATTERN = r'^(.+/)*[^/]+\.[a-zA-Z0-9]+$'

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
            send_file(f"{username} >> {message}".encode("utf-8"))
        else:
            client.send(f"{username} >> {message}".encode("utf-8"))

def get_file(file_path):
    pass

def send_file(file_path):
    pass

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
