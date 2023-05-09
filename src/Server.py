import asyncio
import json
import Commands as Commands
import aiofiles

import ssl
from Temp import clients, send_data, banned_users, user_leave

# version 1.1

# this is a test server, some things may and will break
# also a lot of things will be changed in the future such as message formats, commands etc.

host, port = ("localhost", 9090)

message_history = []
message_size = 200
username_len = 10
escape_code = "\\"
cert, key = "./src/certs/cert.pem", "./src/certs/private.key"  #self signed cert, and key

chat_history = False # Chat history, sends all messages to a new user (WIP)
ssl_connection = False # SSL connection using self signed certs, leave off for plain-text connections


async def timer():  # Timer for anything, currently used as a log writing mechanism
    while True:
        await asyncio.sleep(5)
        if chat_history:
            if len(message_history) > 0:
                async with aiofiles.open(r"./src/logs.txt", mode="a") as f:
                    for line in message_history:
                        await f.write(json.dumps(line) + "\n")

                    message_history.clear()

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


async def send_message(
        client, message: str, sender="Server", message_type="public"
):  # sends a message to a client, given a client and a string. Defualt sende is "Server"
    data_format = {"sender": sender, "message": message, "message_type": message_type}

    if message_type == "public":
        message_history.append(json.dumps(data_format) + "\n")
    await send_data(client, data_format)


async def broadcast(
        data, sender="Server", message_type="public"
):  # broadcasts to all users
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
                print(client)
                await send_data(client, data_format)
        else:
            for client in clients.values():
                print(client)
                if client.current_channel is None:
                    await send_data(client, data_format)
    else:
        for client in clients.values():
            print(client)
            if client.current_channel is None:
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
    async with aiofiles.open("./src/logs.txt", "r") as f:
        history_lines = await f.readlines()
        if len(history_lines) > 0:
            for line in history_lines:
                line = line.strip("\n")
                line = json.loads(line)
                await send_data(client, line)


async def receive_data(client: Client): #reads until EOF and returns the unloaded data
    try:
        data = (await client.reader.readuntil(b"\n")).decode()
        data = json.loads(data)
        print(data)
        print(len(data))
        return data
    except Exception: # TODO WIP, specific exception contexts to be added
        await user_leave(client)


async def handle_client(client: Client):
    """
    Handles the client and acts as the main guard for errors. 
    Will not work until the user has logged in."""
    while client.logged_in:
        data = await receive_data(client)
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

        if message.startswith(Commands.Commands.prefix) and len(message) > len(
                Commands.Commands.prefix
        ):
            status = await Commands.check_command(client, message)
            if status is not None:
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

        login_data = await receive_data(client)
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
    task = asyncio.current_task(loop=None)  # magic to get current task
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
    await timer()
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
