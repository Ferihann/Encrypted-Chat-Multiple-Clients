import select
import socket
import sys

ip = "127.0.1.1"
port = 1239
max_header_length = 10

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # SOL: socket option level ,
                                                                  # REUSEADDR : allow use same address with different sockets
server_socket.bind((ip, port))  # attach this ip and port to this socket
server_socket.listen()  # sockets starts to listen coming connections

connected_sockets = [server_socket]
clients = {}  # dictionary data has client name and their message

print("Listening connections on {ip}:{port} ....")


def recv_msg(client_socket):
    try:
        message_header = client_socket.recv(max_header_length)
        message_length = int(message_header.decode().strip())
        message = client_socket.recv(message_length)
        return {'header': message_header, 'data': message}  # returns user and message information
    except:
        return False


while True:

    readable_sockets, _, exception_socket = select.select(connected_sockets, [], connected_sockets)

    for approved_socket in readable_sockets:
        if approved_socket == server_socket:

            client_socket, client_address = server_socket.accept()
            user = recv_msg(client_socket)  # only username information comes
            if user is False:
                continue

            clients[client_socket] = user
            connected_sockets.append(client_socket)
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode()))

        else:
            message = recv_msg(approved_socket)  # message is received

            if message is False:
                print("Closed connection")
                connected_sockets.remove(approved_socket)
                del clients[approved_socket]
                continue

            user = clients[approved_socket]  # In the clients array , we take the appropriate user
            print("Received message from ", user['data'].decode(), " is: ", message['data'].decode())
            sendingMessage = user['header'] + user['data'] + message['header'] + message['data']

            for i in clients:
                if i == approved_socket:
                    continue
                i.send(sendingMessage)  # send message to the other clients

    for notified_socket in exception_socket:  # if socket is exception socket del the socket

        connected_sockets.remove(notified_socket)
        del clients[notified_socket]
