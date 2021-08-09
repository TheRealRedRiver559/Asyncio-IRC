import socket
import threading
import hashlib
import mysql.connector as mysql
import struct

db_name = ''
db_pass = ''

def main():
    host = 'localhost'
    port = 9090

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    banned_users = [] #will add to db soon :(
    clients = []
    users = []
    commands = {}

    #Command decorator, for adding new commands
    def command(name, role_id):
        def inner(func):
            commands[name] = [func, role_id]
            return func
        return inner

    #broadcasts a message (int) of current connections
    @command('//connections', 1)
    def client_connections(username, message):
        client_connections = len(clients)
        broadcast(f'{username}: {message}'.encode())
        broadcast(f'Server: Clients online: {client_connections}'.encode())
    
    #broadcasts a list of users online
    @command('//users', 2)
    def users_online(username, message):
        broadcast(f'{username}: {message}'.encode())
        user_list = [user for user in users]
        broadcast(f'Server: Users: {user_list}'.encode())
    
    #bans users
    @command('//ban', 2)
    def ban_user(username, command_name, arguments, reason=None):

        index = users.index(username)
        client = clients[index]

        if len(arguments) >= 2:
            reason = " ".join(arguments[1:])
        #Example input data for "arguments"
        # "test this is the second arg"
        if username == arguments[0]:
            send_one_message(client, 'Server: You cannot ban your self!'.encode())
            return

        with mysql.connect(
                host = 'localhost',
                user = 'root',
                password = db_pass,
                database = db_name
            ) as conn:

                cursor = conn.cursor()
                cursor.execute("SELECT role_id FROM users WHERE user_name = %s;", (username,))
                user_role_id = cursor.fetchone()[0]
                cursor.execute("SELECT role_id FROM users WHERE user_name = %s;", (arguments[0],))
                target_role_id = cursor.fetchone()
                target_username = arguments[0]

        if target_role_id == None:
            send_one_message(client, f'Server: No user named {target_username} was found!'.encode())
            return
        if user_role_id <= target_role_id[0]:
            send_one_message(client, f'Server: Cannot ban user with higher or equal permissions!'.encode())
            return
        if arguments[0] in banned_users:
            send_one_message(client, f'Server: User: {target_username} already banned!'.encode())
            return
        if arguments[0] not in users:
            broadcast(f'{username}: {command_name} {target_username} {reason}'.encode())
            broadcast(f'Server: {target_username} has been banned for: Reason: {reason}'.encode())
            banned_users.append(target_username)
            print(f'{target_username} banned...')
            return

        index = users.index(target_username)
        target_client = clients[index]

        send_one_message(target_client, f'Server You have been banned for : Reason: {reason}'.encode())
        send_one_message(target_client, 'CLOSE'.encode())
        broadcast(f'{username}: {command_name} {target_username} {reason}'.encode())
        broadcast(f'Server: {target_username} has been banned for: Reason: {reason}'.encode())
        banned_users.append(target_username)
        print(f'{target_username} banned...')

    #unbans users
    @command('//unban', 2)
    def unban_user(username, command_name, arguments):
        index = users.index(username)
        client = clients[index]

        with mysql.connect(
                host = 'localhost',
                user = 'root',
                password = db_pass,
                database = db_name
            ) as conn:

                cursor = conn.cursor()
                cursor.execute("SELECT role_id FROM users WHERE user_name = %s;", (username,))
                user_role_id = cursor.fetchone()[0]
                cursor.execute("SELECT role_id FROM users WHERE user_name = %s;", (arguments[0],))
                target_role_id = cursor.fetchone()
                target_username = arguments[0]

        if target_role_id == None:
            send_one_message(client, f'Server: No user named {target_username} was found!'.encode())
            return
        if len(arguments) != 1:
            send_one_message(client, f'Server: This command only takes 1 argument. {len(arguments)} Given!'.encode())
            return
        if username == target_username: #unban your self check
            send_one_message(client, 'Server: Why would you even type this?'.encode())
            return
        if user_role_id <= target_role_id[0]: #permission check
            send_one_message(client, f'Server: Cannot unban user with higher or equal permissions!'.encode())
            return
        if target_username not in banned_users: #checks to see if they are not in users
            send_one_message(client, 'Server: Cannot unban user that is not banned!'.encode())
            return
        broadcast(f'{username}: {command_name} {target_username}'.encode())
        broadcast(f'Server: User: {target_username} has been unbanned by: {username}...'.encode())
        banned_users.remove(target_username)
        print(f'{target_username} unbanned...')
    
    #message for missing permission
    def missing_permissions(client, message):
        send_one_message(client, f'Server: Missing permissions for the command named: {message.lower()}'.encode())

#main functions

    def close_connection(client):
        send_one_message(client, 'CLOSE'.encode())
    
    #broadcasts a message to all clients, takes 2nd argument to send to all besides that client.
    def broadcast(message, dont_send_to=None):
        for client in clients:
            if dont_send_to != None:
                if dont_send_to != client:
                    send_one_message(client, message)
                else:
                    pass
            else:
                send_one_message(client, message)

    #command proccesing, checks for permissions and command validity
    def proccess_command(client, message, username):
        command_name, *arguments = message.split(" ")
        try:
            command = commands[command_name][0]
        except KeyError:
            send_one_message(client, f'Server: Invalid Command! no command named: {command_name.lower()}'.encode())
            return

        with mysql.connect(
        host = 'localhost',
        user = 'root',
        password = db_pass,
        database = db_name
        ) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role_id FROM users WHERE user_name = %s;", (username,))
            role_id = cursor.fetchone()
        if role_id[0] >= commands[command_name][1]: #checking if users perms is >= to command perms
            if len(message) > len(command_name):
                try:
                    command(username, command_name, arguments) #checks if message is valid for args
                except TypeError:
                    send_one_message(client, f'Server Command: {command_name} : Requires no arguments!'.encode())
                    return
            else:
                try:
                    command(username, command_name)
                except TypeError:
                    send_one_message(client, f'Server: Command: {command_name} : Requires 1 or more arguments!'.encode())
                    return
        else:
            missing_permissions(client ,command_name)      

    #main client listener for messages and commands.
    #command prefix is "//"
    def handle_client(client):
        while True:
            try:
                message = recv_one_message(client).decode()

                index = clients.index(client)
                username = users[index]

                if message.startswith('//'): #command syntax
                    proccess_command(client, message.lower(), username)
                else:
                    broadcast(f'{username}: {message}'.encode())


            except ConnectionResetError:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                username = users[index]
                print(f'{username} has left...')
                broadcast(f'Server: {username} has left...'.encode())
                users.remove(username)
                break
            except TypeError:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                username = users[index]
                print(f'{username} has left...')
                broadcast(f'Server: {username} has left...'.encode())
                users.remove(username)
                break
# Three main functions for sending and receiving data
    def send_one_message(sock, data):
        length = len(data)
        sock.sendall(struct.pack('!I', length))
        sock.sendall(data)

    def recv_one_message(sock):
        lengthbuf = recvall(sock, 4)
        length, = struct.unpack('!I', lengthbuf)
        return recvall(sock, length)

    def recvall(sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    #accepts clients, and checks logins.
    def receive():
        while True:
            client, address = server.accept()
            print(f'{str(address)} has connected...')
            send_one_message(client, 'LOGIN'.encode())

            username = (recv_one_message(client).decode()).lower()
            password = recv_one_message(client).decode()
            if username in banned_users:
                send_one_message(client, 'You are banned!'.encode())
                print('User is banned. Connection ended...')
                close_connection(client)
                continue
            if username in users:
                send_one_message(client, 'User already connected!'.encode())
                close_connection(client)
            else:
                pass

            with mysql.connect(
                host = 'localhost',
                user = 'root',
                password = db_pass,
                database = db_name
            ) as conn:

                cursor = conn.cursor()

                cursor.execute("SELECT user_name, user_hash, user_salt FROM users WHERE user_name = %s;", (username,))
                user = cursor.fetchone() #returns none or a tuple of the data

            if  user != None:
                hash, salt = bytes(user[1]), bytes(user[2]) #has, salt indexes in db
                new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 1000)

                if new_hash == hash:
                    send_one_message(client, 'Logged In!'.encode())
                                        
                    clients.append(client)
                    users.append(username.lower())
                else:
                    send_one_message(client, 'Username or Password is incorrect!'.encode())
                    print(f'{address} has failed login...')
                    close_connection(client) #incorrect password
                    continue
            else:
                send_one_message(client, 'Username or Password is incorrect!'.encode())
                print(f'{address} has failed login...')
                close_connection(client) #incorrect username
                continue

            print(f'The user of this client is : {username}')
            broadcast(f'Server: {username} has connected...'.encode(), dont_send_to=client) #sends a message to everyone but that client
            send_one_message(client, f'Server: You are connected to : {address}'.encode())

            t1 = threading.Thread(target=handle_client, args=(client,))
            t1.start()

    try:
        print('Server is running and listening...')
        receive()
    except ConnectionAbortedError:
        pass
    except ConnectionResetError:
        pass

if __name__ == "__main__":
    main()
