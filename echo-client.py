# import socket

# HOST = "10.239.95.98"  # The server's hostname or IP address
# PORT = 65432  # The port used by the server

# # Prompt the user to input a message
# message = input("Enter message to send: ")

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     # Convert the input message to bytes and send it
#     s.sendall(message.encode())
#     data = s.recv(1024)

# print(f"Received {data!r}")


# Python program to implement client side of chat room.
import socket
import select
import sys
from device_list import device_map 


if len(sys.argv) != 2:
    print("Correct usage: script, person's name")
    exit()

person_name = sys.argv[1]

if person_name in device_map:
    IP_address, Port = device_map[person_name]
else:
    print("Person not found in device map.")
    exit()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP_address, Port))
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# if len(sys.argv) != 3:
#     print("Correct usage: script, IP address, port number")
#     exit()
# IP_address = str(sys.argv[1])
# Port = int(sys.argv[2])
# server.connect((IP_address, Port))

while True:
    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    # Using select to manage multiple inputs/outputs
    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print(message.decode())  # Decoding the incoming message
        else:
            message = sys.stdin.readline()
            server.send(message.encode())  # Encoding the message before sending
            sys.stdout.write("<You> ")
            sys.stdout.write(message)
            sys.stdout.flush()
server.close()
