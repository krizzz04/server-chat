import socket
from threading import Thread

# server's IP address
SERVER_HOST = "192.168.53.11"
SERVER_PORT = 5002  # port we want to use
separator_token = "<SEP>"  # we will use this to separate the client name & message

# initialize dictionary to store connected clients and their sockets
connected_clients = {}

# create a TCP socket
s = socket.socket()
# make the port as a reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


def listen_for_client(cs, client_name):
    """
    This function keeps listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the dictionary
            print(f"[!] {client_name} disconnected.")
            del connected_clients[client_name]
            break
        else:
            # if we received a message, replace the <SEP> token with ": " for nice printing
            msg = msg.replace(separator_token, ": ")
        # iterate over all connected clients and their sockets
        for name, client_socket in connected_clients.items():
            # and send the message
            client_socket.send(msg.encode())


while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    # receive the client's name
    client_name = client_socket.recv(1024).decode()
    # add the new connected client to the dictionary
    connected_clients[client_name] = client_socket
    print(f"[+] {client_name} connected.")
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket, client_name))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for client_socket in connected_clients.values():
    client_socket.close()
# close server socket
s.close()
