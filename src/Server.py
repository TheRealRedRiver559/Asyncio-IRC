from json.decoder import JSONDecodeError
import socket
import threading
import json

bannedUsers_path = 'storage\\banned-users.json'
users_path = 'storage\\users.json'
description_path = 'storage\\descriptions.json'

def run_server():
    host = 'localhost'
    port = 9090

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    clients = [] 
    #clients and users will be combined in a dictionary soon
    users = []
    commands = {}
    prefix = '//'

    with open(description_path, 'r') as f: #Opens the descriptions and replaces prefix
        descriptions = json.load(f)
        for command in descriptions:
            descriptions[command]['usage'] = descriptions[command]['usage'].replace('@@@', prefix)
            descriptions[command]['examples']= descriptions[command]['examples'].replace('@@@', prefix)

    error_message = { #error messages for certain events like users disconecting
        'Leave': 'Connection closed by client.',
        'Close': 'Connection closed by server.',
        'Connection': 'User already connected.',
        }

    #Command decorator, for adding new commands rather than adding each one to a dictionary and easier to use.
    def command(name, role_id):
        def inner(func):
            commands[name] = [func, role_id]
            return func
        return inner

    #broadcasts a message specifying the current # of connections
    @command('connections', 1)
    def client_connections(username : str):
        client_connections = len(clients)
        broadcast(f'{username}: {prefix}connections')
        broadcast(f'Server: Clients online: {client_connections}')
        print(f'Command: {prefix}connections (Username: {username})')
    
    #broadcasts a list of users online
    @command('users', 2)
    def users_online(username : str):
        broadcast(f'{username}: {prefix}users')
        user_list = [user for user in users]
        broadcast(f'Server: Users: {user_list}')
        print(f'Server: Command: {prefix}users (Username: {username})')
    
    #sends a list of all users inside the 'banned user' list
    @command('banned-users', 3)
    def users_banned(username : str):
        broadcast(f'{username}: {prefix}banned-users')
        with open(bannedUsers_path, 'r') as f:
            try:
                banned_users = json.load(f)
            except JSONDecodeError:
                banned_users = []
        banned_list = [user for user in banned_users]
        broadcast(f'Server: Banned Users: {banned_list}')
        print(f'Server: Command: {prefix}banned-users (Username: {username})')
    
    #bans users (Command syntax : ban <username> [silent] [reason])
    @command('ban', 3)
    def ban_user(username : str, arguments : list):
        reason = None
        silent_ban = False
        client = clients[users.index(username)]
        with open(bannedUsers_path, 'r') as f:
            try:
                banned_users = json.load(f)
            except JSONDecodeError:
                banned_users = []

        if len(arguments) >= 2:
            reason = " ".join(arguments[1:])
            if (arguments[1]).lower() == 'silent':
                silent_ban = True
                reason = " ".join(arguments[2:])

        with open(users_path, 'r') as f:
            data = json.load(f)

            user_role_id = data[username]['role_id']
            target_username = arguments[0]
            if target_username in data:
                target_role_id = data[arguments[0]]['role_id'] 
            else:
                send_message(client ,f"Server: No user named '{target_username}' was found!")
                return
            
        target_role_id = data[target_username]['role_id']

        if user_role_id <= target_role_id:
            send_message(client ,f'Server: Server: You cannot ban this member!')
            return
        if target_username in banned_users:
            send_message(client ,f"Server: '{target_username}' already banned!")
            return
        if target_username not in users:
            send_message(client ,f'Server: This user is not currently in the server')
            return

        with open(bannedUsers_path, 'r') as f:
            try:
                banned_users = json.load(f)
            except JSONDecodeError:
                banned_users = []
        with open(bannedUsers_path, 'w') as f:
            banned_users.append(target_username)
            json.dump(banned_users, f)
            
        target_client = clients[users.index(target_username)]
        send_message(target_client ,f'Server: You have been banned.\n\tReason: {reason}')
        print(f'Command: {prefix}ban {target_username} Silent={silent_ban} Reason:{reason} (Username: {username})')

        if silent_ban == True:
            send_message(client ,f'Server: {target_username} has been banned.\n\tReason: {reason}')
        else:
            broadcast(f"{username}: {prefix}ban {target_username} {reason}")
            broadcast(f"Server: '{target_username}' has been banned.\n\tReason: {reason}")
        user_leave(target_client, error_message['Close'])

    #unbans users
    @command('unban', 3)
    def unban_user(username : str, arguments : list):

        silent_unban = False
        client = clients[users.index(username)]

        with open(bannedUsers_path, 'r') as f:
            try:
                banned_users = json.load(f)
            except JSONDecodeError:
                banned_users = []

        if len(arguments) > 1:
            if (arguments[1]).lower() == 'silent':
                silent_unban = True

        with open(users_path, 'r') as f:
            data = json.load(f)

            user_role_id = data[username]['role_id']
            target_username = arguments[0]
            if target_username in data:
                target_role_id = data[arguments[0]]['role_id'] 
            else:
                send_message(client ,f'Server: No user named {target_username} was found!')
                return

        if len(arguments) > 2:
            send_message(client ,f'Server: This command only takes 2 argument. {len(arguments)} Given!')
            return
        if user_role_id <= target_role_id: #permission check
            send_message(client ,f'Server: Server: You cannot unban this member!')
            return
        if target_username not in banned_users: #checks to see if they are not in users
            send_message(client ,'Server: User is not currently banned!')
            return

        banned_users.remove(target_username)
        with open(bannedUsers_path, 'w') as f:
            json.dump(f, banned_users)
        
        if silent_unban == True:
            send_message(client ,f'Server: {target_username} has been unbanned.')
        else:
            broadcast(f'{username}: {prefix}unban {target_username}')
            broadcast(f'Server: {target_username} has been unbanned by: {username}.')

        print(f'Server: Command: {prefix}unban {target_username} silent={silent_unban} (Username: {username})')

    @command('kick', 2)
    def kick_user(username : str, arguments : list):
        #kicks users but still allows them to join back
        reason = None
        silent_kick = False
        client = clients[users.index(username)]
        with open(bannedUsers_path, 'r') as f:
            try:
                banned_users = json.load()
            except JSONDecodeError:
                banned_users = []

        if len(arguments) >= 2:
            reason = " ".join(arguments[1:])
            if (arguments[1]).lower() == 'silent':
                silent_kick = True
                reason = " ".join(arguments[2:])

        with open(users_path, 'r') as f:
            data = json.load(f)
            
            user_role_id = data[username]['role_id']
            target_username = arguments[0]
            if target_username in data:
                target_role_id = data[arguments[0]]['role_id'] 
            else:
                send_message(client ,f'Server: No user named {target_username} was found!')
                return
            
        target_role_id = data[target_username]['role_id']

        if user_role_id <= target_role_id:
            send_message(client ,f'Server: You cannot kick this member!')
            return
        if target_username in banned_users:
            send_message(client ,f'Server: This member is not currently in the server')
            return
        if target_username not in users:
            send_message(client ,f'Server: This member is not currently in the server')
            return

        target_client = clients[users.index(target_username)]
        send_message(target_client ,f'Server: You have been kicked.\n\tReason: {reason}')
        print(f'Command: {prefix}kick {target_username} Silent={silent_kick} Reason:{reason} (Username: {username})')

        if silent_kick == True:
            send_message(client ,f'{target_username} has been kicked\n\tReason: {reason}.')
        else:
            print(reason)
            broadcast(f'{username}: {prefix}kick {target_username} {str(reason)}')
            broadcast(f'Server: {target_username} has been kicked.\n\tReason: {str(reason)}')
        user_leave(target_client, error_message['Close'])

    @command('help', 2)
    def help_command(username : str, arguments=None):
        #sends a list of all commands. Can show specific details about a command with a argument (Command syntax : //help [command])
        #Soon to change to show commands accessable to that permission level.
        index = users.index(username)
        client = clients[index]

        if arguments != None:
            if len(arguments) != 1:
                send_message(client ,f'Server: This command only takes 1 argument. {len(arguments)} Given!')
                return
            command_name = arguments[0]
            try:
                role_id = commands[command_name][1]
                details = (f'-{command_name}-\n{descriptions[command_name]["description"]}\n\n-Usage-\n{descriptions[command_name]["usage"]}\n\n-Examples-\n{descriptions[command_name]["examples"]}\n\n-Permissions-\nPermission Level : {role_id}+')
                send_message(client ,f'Server:\n{details}')
                print(f'Server: Command: {prefix}help {command_name} (Username: {username})')
                return
            except KeyError:
                send_message(client ,f'Server: Could not find any command named: {command_name}')
                return
        index = users.index(username)
        client = clients[index]
        help_text = (f'Server: [bold white]Commands[/bold white][green]\n{prefix}help \[command]\n{prefix}users\n{prefix}connections\n{prefix}banned-users\n{prefix}kick\n{prefix}ban\n{prefix}unban\n')
        send_message(client ,help_text)

        print(f'Server: Command: {prefix}help (Username: {username})')
    
    #message for missing permission
    def missing_permissions(client : socket, message : str):
        send_message(client ,f'Server: Missing permissions for the command named: {message.lower()}')
    
    #broadcasts a message to all clients. Can send to all axcept certain clients.
    def broadcast(message : str, dont_send_to=None):
        for client in clients:
            if dont_send_to != None:
                if dont_send_to != client:
                    send_message(client ,message)
                else:
                    pass
            else:
                send_message(client ,message)

    #command proccesing, checks for permissions and command validity
    def proccess_command(client : socket, message : str, username : str):
        command_name, *arguments = message.split(" ")
        try:
            command = commands[command_name][0]
        except KeyError:
            send_message(client ,f'Server: Invalid Command! no command named: {command_name.lower()}')
            return

        with open(users_path, 'r') as f:
            data = json.load(f)

            role_id = data[username]['role_id']

        if role_id >= commands[command_name][1]: #checking if users perms is >= to command perms
            if len(message) > len(command_name):
                try:
                    command(username, arguments=arguments) #checks if message is valid for args
                except TypeError:
                    send_message(client ,f'Server: Command: {command_name} : Requires no arguments!')
                    return
            else:
                try:
                    command(username)
                except TypeError:
                    send_message(client ,f'Server: Command: {command_name} : Requires 1 or more arguments!')
                    return
        else:
            missing_permissions(client ,command_name)      

    def recv_message(client : socket):
        message = client.recv(1024).decode()
        return message[3:]
    def send_message(client : socket, message : str):
        length = str(len(message)).zfill(3)
        client.send(f'{length}{message}'.encode())
        return



    #main client listener for messages and commands.
    def handle_client(client : socket):
        while True:
            try:
                message = recv_message(client)
                username = users[clients.index(client)]
                
                if len(message) == 0:
                    pass
                elif len(message) > 200:
                    send_message(client ,'Server: Message size exceeds the 200 character limit!')
                    continue
                elif message[:len(prefix)] == prefix: #command prefix
                    proccess_command(client, message[len(prefix):].lower(), username)
                else:
                    broadcast(f'{username}: {message}')
            except ConnectionAbortedError:
                break #Server Closed Connetion
            except ConnectionResetError:
                user_leave(client, error_message['Leave'])
                break

    #error handling for users leaving. Leave message on ban is optional
    def user_leave(client : socket, leave_reason : str, broadcast_leave=True):
        address = client.getpeername()
        client.close()
        try:
            username = users[clients.index(client)]
            clients.remove(client)
            users.remove(username)
        except ValueError: #User did not finish login
            username = 'N/A'

        if broadcast_leave == True:
            broadcast(f'Server: {username} has disconnected...')
        print(f'Server: Client:({username} {address} has disconnected (Reason: {leave_reason})')
    
    def failed_login(client):
        send_message(client ,'Username or Password is incorrect!')
        user_leave(client, 'User failed login', broadcast_leave=False)

    #accepts clients, and checks login crediantials.
    def receive():
        while True:
            client, address = server.accept()
            print(f'{str(address)} has connected...')
            send_message(client ,'LOGIN') #Sends message to start the login proccess. May change to be the first 2 inputs rather than sending a message for Login.

            try:
                username = recv_message(client)[1:]
                password = recv_message(client)[1:]
            except ConnectionResetError: #User left during login
                user_leave(client, 'Left during login')
                continue

            with open(bannedUsers_path, 'r') as f:
                try:
                    banned_users = json.load(f)
                except JSONDecodeError:
                    banned_users = []

            if username in banned_users:
                send_message(client ,'You are banned!')
                print('User is banned. Connection ended...')
                client.close()
                continue
            if username in users:
                send_message(client ,'User already connected!')
                user_leave(client, error_message['Connection'], broadcast_leave=False)
                continue
            else:
                pass

            #No hashing or anything of the sort is being added until later.
            with open(users_path, 'r') as f:
                try:
                    data = json.load(f)
                except JSONDecodeError: #no users in json file
                    failed_login(client)
                    continue

                if username in data:
                    user_info = data[username]
                    user = (username, user_info['password'])
                else:
                    failed_login(client)
                    continue

                user_password = user[1]

                if user_password == password:
                    send_message(client ,'Logged In!')
                                        
                    clients.append(client)
                    users.append(username.lower())
                else:
                    failed_login(client)
                    continue

            broadcast(f'Server: {username} has connected...', dont_send_to=client) #sends a message to everyone but that client
            send_message(client ,f'Server: You are connected to : {address}')

            t1 = threading.Thread(target=handle_client, args=(client,))
            t1.start()


    print('Server is running and listening...')
    receive()

if __name__ == "__main__":
    run_server()
