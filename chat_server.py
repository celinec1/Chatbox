import socket
import threading

# Configuration
HOST = "10.0.0.31"
PORT = 30000

# Databases
users_db = {}  # userID: userName
friends_db = {}  # userID: [friendIDs]
active_users = {}  # userID: connection
next_user_id = 1
chat_requests = {}  # userID: [list of userIDs who requested a chat]
chat_sessions = {}  # (userID1, userID2): [list of messages]

def handle_chat_request(from_user, to_user):
    # Add a chat request from from_user to to_user
    if to_user in chat_requests:
        chat_requests[to_user].append(from_user)
    else:
        chat_requests[to_user] = [from_user]

def list_chat_requests(user_id):
    # Return a list of chat requests for user_id
    return chat_requests.get(user_id, [])

def start_chat_session(user_id, friend_id):
    # Start a chat session between user_id and friend_id
    session_key = tuple(sorted([user_id, friend_id]))
    chat_sessions[session_key] = []

def add_chat_message(from_user, to_user, message):
    # Add a message to the chat session between from_user and to_user
    session_key = tuple(sorted([from_user, to_user]))
    if session_key in chat_sessions:
        chat_sessions[session_key].append((from_user, message))

def get_chat_messages(user_id, friend_id):
    # Get messages from the chat session between user_id and friend_id
    session_key = tuple(sorted([user_id, friend_id]))
    return chat_sessions.get(session_key, [])


def handle_new_user(user_name):
    global next_user_id
    user_id = str(next_user_id)
    next_user_id += 1
    users_db[user_id] = user_name
    friends_db[user_id] = []
    return user_id

def add_friend(user_id, friend_id):
    print(f"Attempting to add friend: user_id={user_id}, friend_id={friend_id}")  # used to debug
    print(f"Current users_db: {users_db}")  #  # used to debug
    if friend_id in users_db and user_id != friend_id:
        friends_db[user_id].append(friend_id)
        print(f"Added friend successfully: {friends_db[user_id]}")  #  # used to debug
        return True
    else:
        if friend_id not in users_db:
            print("friend_id not in users_db")  #  # used to debug
        if user_id == friend_id:
            print("user_id is the same as friend_id")  #  # used to debug
        return False


def get_active_friends(user_id):
    if user_id is None or user_id not in friends_db:
        return []
    unique_active_friends = set(friend_id for friend_id in friends_db[user_id] if friend_id in active_users)
    return list(unique_active_friends)

def exit_chat_session(user_id):
    for key in list(chat_sessions.keys()):
        if user_id in key:
            user1, user2 = key
            other_user_id = user2 if user_id == user1 else user1
            other_user_conn = active_users.get(other_user_id)
            if other_user_conn:
                try:
                    message = "CHAT_SESSION_ENDED"
                    other_user_conn.sendall(message.encode())
                except Exception as e:
                    print(f"Error sending chat end notification: {e}")
            del chat_sessions[key]
            break



def handle_client(conn, addr):
    print(f"Connected by {addr}")
    user_id = None
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break  
            
            # Split the received data into command and parameters
            command, *params = data.split(":")
            
            if command == "NEW":
                user_name = params[0]
                user_id = handle_new_user(user_name)
                active_users[user_id] = conn
                response = f"Registered with UserID {user_id}"
                
            elif command == "RETURNING":
                temp_user_id = params[0]
                if temp_user_id in users_db:
                    user_id = temp_user_id
                    active_users[user_id] = conn
                    response = "Welcome back."
                else:
                    response = "UserID not found. Please check your UserID or register as a new user."
                    user_id = None  

            elif command == "ADD_FRIEND":
                _, command_user_id, command_friend_id = data.split(":")
                print(f"Server Debug: Received ADD_FRIEND with user_id={command_user_id} and friend_id={command_friend_id}")
                if add_friend(command_user_id, command_friend_id):
                    response = "Friend added successfully."
                else:
                    response = "Failed to add friend."
            elif command == "CHECK_ACTIVE_FRIENDS":
                if user_id is None:
                    response = "Error: User ID not set. Please log in or register."
                else:
                    active_friend_ids = get_active_friends(user_id)
                    active_friends_info = [f"{users_db[friend_id]}:{friend_id}" for friend_id in active_friend_ids]
                    response = "Active friends: " + ", ".join(active_friends_info)


            elif command == "CHAT_REQUEST":
                # Assuming params[0] is the friend's user_id
                to_user = params[0]
                handle_chat_request(user_id, to_user)
                response = f"Chat request sent to {users_db[to_user]}."

            elif command == "ACCEPT_CHAT":
                # Start a chat session between user_id and params[0]
                friend_id = params[0]
                start_chat_session(user_id, friend_id)
                # response = f"Now in chatroom with {users_db[friend_id]}."

            elif command == "SEND_CHAT":
                _, from_user, to_user, message = data.split(":", 3)
                session_key = tuple(sorted([from_user, to_user]))
                if session_key in chat_sessions:
                    recipient_id = to_user if from_user == user_id else from_user
                    recipient_conn = active_users.get(recipient_id)
                    if recipient_conn:
                        try:
                            forwarded_message = f"{users_db[from_user]} says: {message}"
                            recipient_conn.sendall(forwarded_message.encode())
                            # response = "Message sent."
                        except Exception as e:
                            response = f"Failed to send message: {e}"
                    else:
                        response = "Recipient not found."
                else:
                    response = "No active chat session."



            elif command == "EXIT_CHAT":
                exit_chat_session(user_id) 
                response = "Exited chat."

            elif command == "DISCONNECT":
                if user_id:
                    del active_users[user_id]
                    print(f"User {user_id} disconnected.")
                break  
            
            # Send the response to the client
            conn.sendall(response.encode())
    finally:
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("Server is listening...")
    
    while True:
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

