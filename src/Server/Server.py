import asyncio
import json
import Commands as Commands
import aiofiles
import time

import ssl
from Temp import clients, send_data, banned_users, user_leave

# version 1.12

# this is a test server, some things may and will break
# also a lot of things will be changed in the future such as message formats, commands etc.

host, port = ("localhost", 9090)

# Max message size for incoming messages
message_size = 200
# Max Username length for users logging in
username_len = 10
# This is the total amount of time the server will wait before disconnecting a client if a client does not respond
keep_alive_wait_time = 5
# Escape sequence code, this is used for breaking command line prefixes
escape_code = "\\"
# Cert and key file locations
cert, key = "./certs/cert.pem", "./certs/private.key"  # self signed cert, and
message_history = []

# Chat history logs all messages to a log file. Leave OFF / False for now. WIP
chat_history = False
# SSL connection using self-signed certs, leave off for plain-text connections
# Client AND Server must both have this enabled to have a connection at the moment
ssl_connection = False


class Client:
    """
    Client class. This class stores information about the instance such as permission levels, usernames, tasks,
    command history's and more. It is what is passed around in the server.
    """

    def __init__(self, reader, writer, task):
        self.reader = reader
        self.writer = writer
        self.task = task

        self.logged_in = False
        self.username = None
        self.connected = True
        self.current_channel = None
        self.time = None
        self.pong_received = True
        self.permission_level = 1
        self.show_command = None

        self.command_history = []

    # reads until EOF and returns the unloaded data
    async def receive_data(self):
        try:
            data = (await self.reader.readuntil(b"\n")).decode()
            data = json.loads(data)
            return data
        # TODO WIP, specific exception contexts to be added
        except Exception as e:
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


# This is a timer that sends out messages to the client every (n) seconds to make sure it's still active.
async def keep_alive_timer():
    while True:
        # Unix time is the easiest to implement considering it's the same for everyone.
        # It gets converted to the user's local time client side.
        unix_time = time.time()
        for client in clients.values():
            if client.connected:
                if client.pong_received:
                    client.pong_received = False
                else:
                    await user_leave(client)

                client.time = unix_time
                await send_message(client, 'Pong', message_type="SYN")
            else:
                pass

        await asyncio.sleep(5)


async def keep_alive(client, data):
    # This checks the time difference and determines if the client is still connected / active.
    client_time = float(data['time'])
    time_now = time.time()
    delta_time = round(time_now - client_time)
    if delta_time > 5:
        await send_message(client, f"Connection issues...")
        await user_leave(client)


async def broadcast(data, sender="Server", message_type="public"):
    # Server side broadcast, this will broadcast the message to all other users in the same channel.
    data_format = {"sender": sender, "message": data, "message_type": message_type}
    if chat_history:
        # Appends all messages to the temp message history list
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


async def send_message(client, message: str, sender="Server",message_type="public"):
    # Sends a message given a string to the specified client. Sender and message type can be changed.

    # This is a check in case you want to send by username instead (for some reason)
    if isinstance(sender, Client):
        sender = sender.username
    data_format = {"sender": sender, "message": message, "message_type": message_type}

    if message_type == "public":
        message_history.append(json.dumps(data_format) + "\n")
    await send_data(client, data_format)


# TODO Multi-cast (WIP. Has not been attempted to be implemented yet)
async def multi_cast():
    pass


# Sends the log.txt contents to a client. This is still WIP considering it can and may
# Overflow the network stream with tons of data. I will have to add some sort of chunking
async def send_history(client):
    async with aiofiles.open("./logs.txt", "r") as f:
        history_lines = await f.readlines()
        if len(history_lines) > 0:
            for line in history_lines:
                line = line.strip("\n")
                line = json.loads(line)
                await send_data(client, line)


# This is the client handler, this is responsible for all client actions
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
            await send_message(client, "The message sent, is not in the correct format!")
            continue

        if len(message) > message_size:
            await send_message(client, f"Message exceeds the {message_size} char size limit.")
            continue
        elif len(message.strip()) == 0:
            continue

        # default escape_code = "\\"
        # prefix = Commands.Commands.prefix (default = //)

        # This checks to see if the message type is an ACK, can also be added to all client side messages for a better.
        # Reference for messages
        if data['message_type'] == 'ACK':
            client.pong_received = True
            await keep_alive(client, data)
            continue

        if message.startswith(Commands.Commands.prefix) and len(message) > len(Commands.Commands.prefix):

            # Returns a status from the Commands.py file, either None, or a String error.
            status = await Commands.check_command(client, message)
            if status is not None:
                if client.show_command:
                    # If the command is set to public, the usage and the output will be shown for everyone.
                    await broadcast(message)
                    await broadcast(status)
                else:
                    # Other-wise it will be a local message. Only the person who sent it will see.
                    await send_message(client, message, sender=client)
                    await send_message(client, status)

        else:
            message = message.replace(escape_code + Commands.Commands.prefix, Commands.Commands.prefix)
            await broadcast(message, sender=client)


# Login will wait until a correct username and pass have been submitted.
# There is no checking password, usernames and no database at the moment.
# Purely for testing and annoyance of testing.

# TODO add a optional login option

async def login(client: Client):
    data_format = {"sender": "Server", "message": "LOGIN", "message_type": "REQUEST",}
    await send_data(client, {"username_length": username_len, "message_length": message_size})

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


# This is the first function that is called when a client connections, it makes a client object and starts everything.
async def client_connected(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    task = asyncio.current_task()
    client = Client(reader, writer, task)
    await login(client)
    if chat_history:
        await send_history(client)
    await handle_client(client)


# This is the main function, this starts the server and accepts all connections
async def run_server():
    # Optional SSL
    if ssl_connection:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain(cert, key)
        server = await asyncio.start_server(client_connected, host, port, ssl=ssl_context)
    else:
        server = await asyncio.start_server(client_connected, host, port)

    print("Server started!")
    # await log_timer()
    # WIP, so it is commented out even if you attempt to use the variable
    await keep_alive_timer()
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
