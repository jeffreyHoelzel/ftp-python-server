# Multi-threaded FTP Chat Server and Client

This multi-threaded FTP chat server enables multiple clients to connect and exchange messages and/or files within specified exchange rooms. Clients can join existing rooms or create new ones to send messages or share files with others.

## How to Run
## Server
1. Install the server script (`server.py`).
2. Start the server by running the following command in a terminal (Powershell or Unix-based):
```bash
python server.py
```
The server will run and output status updates in the terminal. To stop the server, press `CTRL+C` to stop the threads and terminate the server.

## Client
1. Install the client script (`client.py`).
2. In at least two other terminals, run the following command to start the client:
```bash
python client.py
```
The first client to connect must enter `"NEW"` to create a new exchange room, as there won't be any available to join initially. Subsequent clients can either join the created room or create a new one.

## Server-side Output
- The server will display status updates about the connection, room management, and file transfers in the terminal.

## Client-side Interaction
1. The first client to connect will create a new exchange room by typing "NEW". They can then send messages or files to others.
2. Subsequent clients will see a list of available rooms and can join an existing room or create a new one by entering its name exactly as displayed. Failing to type the room name correctly will terminate the client program.

## Sending Messages and Files
- **Messages**: Type and send any text to share with other clients in the exchange room.
- **Files**: Specify the exact path to a file, and it will be sent to all other clients in the exchange room.

---
### Example Use Case
1. Start the server by running `server.py` in one terminal.
2. In at least two other terminals, run `client.py`.
3. The first client creates a new exchange room by typing `"NEW"`.
4. The second client can either join the newly created room or create their own by typing the exact name of the room.
5. Clients can now exchange messages and share files.

### Developed by Jeffrey Hoelzel