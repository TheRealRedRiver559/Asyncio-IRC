import asyncio
import json
import Commands as Commands
import aiofiles
import time

import ssl
from Temp import clients, send_data, banned_users, user_leave

# version 1.10

# this is a test server, some things may and will break
# also a lot of things will be changed in the future such as message formats, commands etc.

host, port = ("localhost", 9090)

message_size = 200
username_len = 10
keep_alive_wait_time = 5 #weird name, but informative. in seconds
escape_code = "\\"
cert, key = "./certs/cert.pem", "./certs/private.key"  #self signed cert, and key
message_history = []

chat_history = False
ssl_connection = False # SSL connection using self signed certs, leave off for plain-text connections


#INFO
"""
Codes :
    -Types
        -INFO
        -ACCESS
        -
    -Messages
"""

class Client:
    """Client class for storing client information such as task info, username, current channel and more"""

    def __init__(self, reader, writer, task):
        self.reader = reader
        self.writer = writer
        self.task = task

        self.logged_in = False
        self.username = None
        self.connected = True
        self.current_channel = None
        self.time = None
        self.pong_recieved = True
        self.permission_level = 1
        self.show_command = None

        self.command_history = []

    async def receive_data(self): #reads until EOF and returns the unloaded data
        try:
            data = (await self.reader.readuntil(b"\n")).decode()
            data = json.loads(data)
            return data
        except Exception as e: # TODO WIP, specific exception contexts to be added
            await user_leave(self)
            return

    
    

async def log_timer():
    while True:
        await asyncio.sleep(5)
        if chat_history:
            if len(message_history) > 0:
                async with aiofiles.open(r"./logs.txt", mode="a") as f:
                    for line in message_history:
                        await f.write(json.dumps(line) + "\n")

                    message_history.clear()


time_log = dict()

async def keep_alive_timer():
    while True:
        unix_time = time.time()
        for client in clients.values():
            if client.connected:
                if client.pong_recieved:
                    client.pong_recieved = False
                else:
                    await user_leave(client)

                client.time = unix_time
                await send_message(client, 'Pong', message_type="SYN")
            else:
                pass

        await asyncio.sleep(5)

async def keep_alive(client, data):

    client_time = float(data['time'])
    time_now = time.time()
    delta_time = round(time_now - client_time)
    if delta_time > 5:
        await send_message(client, f"Connection issues...")
        user_leave(client)

async def broadcast(data, sender="Server", message_type="public"):  # broadcasts to all users
    """broadcasts the message to all users in a channel, or in the main user list if no channel is present"""
    data_format = {"sender": sender, "message": data, "message_type": message_type}
    if chat_history:
        if message_type == "public":
            message_history.append(json.dumps(data_format) + "\n")
    if isinstance(sender, Client):
        client = sender
        data_format["sender"] = client.username
        if client.current_channel is not None:
            channel = client.current_channel
            for client in channel.clients:
                await send_data(client, data_format)
        else:
            for client in clients.values():
                if client.current_channel is None:
                    await send_data(client, data_format)
    else:
        for client in clients.values():
            if client.current_channel is None:
                await send_data(client, data_format)

async def send_message(client, message: str, sender="Server", message_type="public"):  # sends a message to a client, given a client and a string. Defualt sende is "Server"
    if isinstance(sender, Client):
        sender = sender.username
    data_format = {"sender": sender, "message": message, "message_type": message_type}

    if message_type == "public":
        message_history.append(json.dumps(data_format) + "\n")
    await send_data(client, data_format)

#TODO Multi-cast (WIP. Has not been attempted to be implmented yet)
""" 
async def multi_cast(
        data, sender="Server", message_type="public", target_clients=None
):  # has not been tested yet
    # wil accept clients, or client usernames.
    if target_clients is None:
        target_clients = []
    data_format = {"sender": sender, "message": data, "message_type": message_type}

    if message_type == "public":
        message_history.append(json.dumps(data_format) + "\n")

    for target in target_clients:
        if isinstance(target, str):
            try:
                client = clients[target]
            except KeyError:
                pass
        elif isinstance(target, Client):
            await send_data(target, data_format)

    for client in clients.values():
        await send_data(client, data_format)
"""

async def send_history(client): #Sends the log.txt contents to a client
    async with aiofiles.open("./logs.txt", "r") as f:
        history_lines = await f.readlines()
        if len(history_lines) > 0:
            for line in history_lines:
                line = line.strip("\n")
                line = json.loads(line)
                await send_data(client, line)


async def handle_client(client: Client):
    """
    Handles the client and acts as the main guard for errors. 
    Will not work until the user has logged in."""
    while client.logged_in:
        data = await client.receive_data()
        if data is None:
            return
        try:
            message: str = data["message"]
        except Exception as e:
            await send_message(
                client, "The message sent, is not in the correct format!"
            )
            continue



        if len(message) > message_size:
            await send_message(client, f"Message exceeds the {message_size} char size limit.")
            continue
        elif len(message.strip()) == 0:
            continue

        # escape_code = "\\"
        # prefix = Commands.Commands.prefix (defualt = //)

        if data['message_type'] == 'ACK':
            client.pong_recieved = True
            await keep_alive(client, data)
            continue

        if message.startswith(Commands.Commands.prefix) and len(message) > len(Commands.Commands.prefix):
 
            status = await Commands.check_command(client, message)
            if status is not None:
                if client.show_command:
                    await broadcast(message)
                    await broadcast(status)
                else:
                    await send_message(client ,message, sender=client)
                    await send_message(client, status)
            
        else:
            message = message.replace(
                escape_code + Commands.Commands.prefix, Commands.Commands.prefix
            )
            await broadcast(message, sender=client)


async def login(client: Client):
    data_format = {
        "sender": "Server",
        "message": "LOGIN",
        "message_type": "REQUEST",
    }  # These will end up being changed to something better
    await send_data(
        client, {"username_length": username_len, "message_length": message_size}
    )

    while not client.logged_in:
        await send_data(client, data_format)

        login_data = await client.receive_data()
        try:
            username = login_data["username"]
        except (KeyError, TypeError) as e:
            await user_leave(client)
            return

        if len(username) > username_len:
            await send_message(client, "LENGTH", message_type="DENY")
            continue

        if username in banned_users:
            await send_message(client, "BANNED", message_type="DENY")
            await user_leave(client)
            return

        if username in clients.keys():
            await send_message(client, "TAKEN", message_type="DENY")
            continue

        await send_message(client, "LOGIN", message_type="PERMIT")
        client.logged_in = True
        client.username = username
        clients[client.username] = client
        await send_message(client, "Logged in!", message_type="INFO")


async def client_connected(reader : asyncio.StreamReader, writer : asyncio.StreamWriter):
    task = asyncio.current_task() 
    client = Client(reader, writer, task)
    await login(client)
    if chat_history:
        await send_history(client)
    await handle_client(client)


async def run_server():
    if ssl_connection:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain(cert, key)
        server = await asyncio.start_server(client_connected, host, port, ssl=ssl_context)
    else:
        server = await asyncio.start_server(client_connected, host, port)

    print("Server started!")
    #await log_timer()
    await keep_alive_timer()
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
