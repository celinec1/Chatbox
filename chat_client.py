import socket

HOST = "10.0.0.31"
PORT = 30000

def send_receive(s, message):
    s.sendall(message.encode())
    return s.recv(1024).decode()

# Establish connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

user_id = None
def chat_room_interaction(friend_id):
    while True:
        message = input("You: ")
        if message.upper() == "EXIT":
            send_receive(s, "EXIT_CHAT")
            break
        else:
            response = send_receive(s, f"SEND_CHAT:{user_id}:{friend_id}:{message}")
            print(response)  

while True:
    if user_id is None:
        user_status = input("Are you a returning user (1) or a new user (2)? ")
        if user_status == "1":
            user_id = input("Welcome back! Please enter your UserID: ")
            response = send_receive(s, f"RETURNING:{user_id}")
            if "UserID not found" in response or "Error" in response:
                print(response) 
                user_id = None  
                continue 
            elif "Welcome back." in response:
                print(response)  
        elif user_status == "2":
            user_name = input("Welcome! Please enter your name for registration: ")
            response = send_receive(s, f"NEW:{user_name}")
            user_id = response.split()[-1]
            print(f"Your new UserID is {user_id}")
    
    action = input("Select an action: (1) Add a friend (2) Check active friends (3) Disconnect (4) Request Chatbox (5) Check Inbox:")
    if action == "1":
        friend_id = input("Enter your friend's UserID: ")
        response = send_receive(s, f"ADD_FRIEND:{user_id}:{friend_id}")
        response = send_receive(s, f"ADD_FRIEND:{user_id}:{friend_id}")
        print(response)
    elif action == "2":
        response = send_receive(s, f"CHECK_ACTIVE_FRIENDS:{user_id}")
        print(response)
    elif action == "3":
        send_receive(s, "DISCONNECT")
        break  
    elif action == "4":  
        friend_id = input("Enter your friend's UserID to request a chat: ")
        response = send_receive(s, f"CHAT_REQUEST:{friend_id}")
        print(f"Waiting for {friend_id} to join the chat room...")

    elif action == "5":  
        response = send_receive(s, "LIST_CHAT_REQUESTS")
        print(response) 
        if response.strip() == "":
            print("No chat requests available.")
        else:
            selected_user_id = input("Enter the UserID of the chat request you want to accept: ")
            response = send_receive(s, f"ACCEPT_CHAT:{selected_user_id}")
            print(f"Welcome to the chat room with {response}. Type 'EXIT' to leave the chat.")
            chat_room_interaction(selected_user_id)  


    else:
        print("Invalid action.")


