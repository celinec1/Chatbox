import socket

HOST = "10.239.95.98"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

# Prompt the user to input a message
message = input("Enter message to send: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # Convert the input message to bytes and send it
    s.sendall(message.encode())
    data = s.recv(1024)

print(f"Received {data!r}")
