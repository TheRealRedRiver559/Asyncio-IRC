import asyncio
import json
import Commands
import aiofiles
import os
import ssl

current_path = os.path.dirname(os.path.realpath(__file__))
#version 1.3
"""
+ Added SSL
- Removed Commands untill I find a better solution
+ Added an async message history with a 30 second timer
+ Better message handling with codes for custom clients
Still some issues, but id rather log it then not show anything
"""

cert, key = rf"{current_path}\selfsigned.crt", rf"{current_path}\selfsigned.key"

#this is a test server, some features (most) are not working
#also a lot of things will be changed in the future such as message formats.

host, port = ('localhost', 9090)
clients = dict()
banned_users = set() #temp removed , add usernames manaully
message_history =  [] #temp history, resets every 30 seconds
chat_history = True
message_size = 200 #temp removed for testing
username_len = 10

file_writing = False

async def timer():
    while True:
        await asyncio.sleep(2)

        if chat_history == True:
            if len(message_history) > 0:
                file_writing = True
                async with aiofiles.open(fr"{current_path}/logs.txt", mode='a') as f:
                    for line in message_history:
                        await f.write(json.dumps(line)+"\n")

                    message_history.clear()
                file_writing = False



class Client:
    """Client class for storing client information such as task, username and more"""
    def __init__(self, reader, writer, task):
        self.reader = reader
        self.writer = writer
        self.task = task
        self.logged_in = False
        self.username = None
        self.connected = True

async def user_leave(client : Client):
    client.connected = False
    client.task.cancel()
    if client.username != None:
        del clients[client.username]
    if not client.writer.is_closing():
        client.writer.close()
        await client.writer.wait_closed()

async def send_data(client, data):
    if isinstance(data, dict):

        data = (json.dumps(data)+'\n')
    data = data.encode()
    client.writer.write(data)
    await client.writer.drain()


async def send_message(client, message : str, sender="Server", message_type="public"):
    format = {'sender':sender, 'message':message, 'message_type':message_type}

    if (message_type=='public'):
        message_history.append(json.dumps(format)+'\n')
    await send_data(client, format)

async def broadcast(data, sender='Server', message_type='public'):
    """broadcasts the message to all users, command and server side version"""
    format = {'sender':sender, 'message':data, 'message_type':message_type}

    if (message_type=='public'):
        message_history.append(json.dumps(format)+'\n')

    for client in clients.values():
        await send_data(client, format)

async def multi_cast(data, sender='Server', message_type='public', target_clients=[]):
    """broadcasts the message to all users, command and server side version"""
    data = ' '.join(data)
    format = {'sender':sender, 'message':data, 'message_type':message_type}

    if (message_type=='public'):
        message_history.append(json.dumps(format)+'\n')
    
    for target in target_clients:
        if isinstance(target, str):
            try:
                client = clients[target]
            except KeyError:
                pass
        elif isinstance(target, Client):
            await send_data(target, format)

    for client in clients.values():
        await send_data(client, format)


async def send_history(client):
    if file_writing == True:
       await asyncio.sleep(2)

    async with aiofiles.open(f"{current_path}/logs.txt", 'r') as f:
        history_lines = await f.readlines()
        if len(history_lines) > 0:
            for line in history_lines:
                line = line.strip("\n")
                line = json.loads(line)
                await send_data(client, line)

async def receive_data(client : Client): 
    try: 
        data = (await client.reader.readuntil(b'\n')).decode()
        data = json.loads(data)
        return data
    except (Exception):
        await user_leave(client)

async def handle_client(client : Client):
    while client.logged_in:
        data = await receive_data(client)
        if data == None:
            return
        try:
            message : str = data['message']
        except KeyError:
            await send_message(client, 'The message sent, is not in the correct format!')
            continue
        if len(message) > message_size:
            await send_message(client, 'Message exceeds the 200 char size limit.')
            continue
        elif len(message) == 0:
            continue

       # if message.startswith(Commands.prefix):
            #await Commands.check_command(client, message)
        #else:
            #await broadcast(client, message)
        await broadcast(message, sender=client.username)

async def login(client : Client):
    format = {'sender':'Server', 'message':'LOGIN', 'message_type':'REQUEST'} #These will end up being changed to something better
    while client.logged_in == False:
        await send_data(client, format)

        login_data = await receive_data(client)
        print(login_data)
        try:
            username = login_data['username']
        except (KeyError, TypeError):
            await user_leave(client)
            return

        if len(username) > username_len:
            await send_message(client, 'Username too long!', message_type='INFO')
            continue

        if username in banned_users:
            await send_message(client, 'You are banned!', message_type='INFO')
            await user_leave(client)

        await send_message(client, 'PERMIT', message_type='INFO')
        client.logged_in = True
        client.username = username
        clients[client.username] = client
        await send_message(client, 'Logged in!', message_type="INFO")

async def client_connected(reader, writer):
    print('Client Connected!')
    task = asyncio.current_task(loop=None) #magic to get current task
    client = Client(reader, writer, task)
    await login(client)
    if chat_history == True:
        await send_history(client)
    await handle_client(client)

async def run_server():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(cert, key)

    server = await asyncio.start_server(client_connected, host, port, ssl=ssl_context)

    print('Server started!')
    await timer()
    async with server:
        await server.serve_forever()
asyncio.run(run_server())
