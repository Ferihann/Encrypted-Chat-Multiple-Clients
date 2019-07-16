import errno
import socket
import select
import sys
from aes import Aes

max_len = 10

ip = '127.0.1.1'
port = 1239

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((ip, port))
client_socket.setblocking(False)

username = input("Enter your username : ")
usernameEncode = username.encode()
usernameHeader = f"{len(usernameEncode):<{max_len}}".encode()
client_socket.send(usernameHeader + usernameEncode)
ciphering = Aes('1')


def receive_coming_messages():
    header = client_socket.recv(max_len)  # Username header is come

    if not len(header):
        print("connection closed")
        sys.exit()
    header_length = int(header.decode().strip())
    sending_user = client_socket.recv(header_length)  # take the user name

    message_header = client_socket.recv(max_len)  # message header is come
    message_length = int(message_header.decode().strip())
    coming_message = client_socket.recv(message_length)  # message is taken
    coming_message = coming_message.decode()
    coming_message = ciphering.decrypt(coming_message)
    return sending_user.decode() + ">" + coming_message.decode()  # send the message to the server


while True:

    message = input(f'{username} >')  # user sends its message
    message = ciphering.encrypt(message)
    message_header = f"{len(message):<{max_len}}".encode()
    client_socket.send(message_header + message)  # message header and message is sends

    try:
        while True:
            print(receive_coming_messages())
# Exception issues
    except IOError as e:

        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue

    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()
