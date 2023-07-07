import asyncio
import json
import Commands as Commands
import aiofiles
import time


import ssl
from Temp import clients, send_data, banned_users, user_leave, Channel

# version 1.10

# this is a test server, some things may and will break
# also a lot of things will be changed in the future such as message formats, commands etc.

host, port = ("localhost", 9090)

# Max message size for incoming messages
message_size = 200
# Max Username length for users logging in
username_len = 10
# This is the total amount of time the server will wait before disconnecting a client if a client does not respond
keep_alive_wait_time = 10
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


class Message:
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    INFO = "INFO"
    ERROR = "ERROR"
    CHAT = "CHAT"
    PRIVATE = "PRIVATE"
    STATUS = "STATUS"
    PUBLIC = "PUBLIC"
    CLOSE = "CLOSE_CONN"
    LOGIN = "LOGIN"
    ACK = "ACK"
    SYN = "SYN"

    def __init__(
        self, sender, message: str, message_type: str, time: float=time.time(), post_flag: bool=False
    ):
        self.sender = sender
        self.message = message
        self.message_type = message_type
        self.time = time
        self.post_flag = post_flag

    def to_dict(self):
        return {
            "sender": self.sender,
            "message": self.message,
            "message_type": self.message_type,
            "time": self.time,
            "post_flag": self.post_flag,
        }

    @staticmethod
    def from_dict(data):
        return Message(
            sender=data.get("sender"),
            message=data.get("message"),
            message_type=data.get("message_type"),
            time=data.get("time"),
            post_flag=data.get("post_flag", False),
        )


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
        self.current_channel= None
        self.time = None
        self.pong_received = True
        self.permission_level = 1
        self.show_command = None

        self.command_history = []

    # reads until EOF and returns the unloaded data
    async def receive_data(self) -> Message | None:
        try:
            data = (await self.reader.readuntil(b"\n")).decode()
            data = json.loads(data)
            message = Message.from_dict(data)
            return message
        # TODO WIP, specific exception contexts to be added
        except Exception as e:
            await user_leave(self)
            return

    async def keep_alive(self, message: Message):
        # This checks the time difference and determines if the client is still connected / active.
        client_time = message.time
        time_now = time.time()
        delta_time = round(time_now - client_time)
        if delta_time > keep_alive_wait_time:
            message = Message(
                sender="Server",
                message="Connection issues..KEEP ALIVE.",
                message_type=Message.ERROR,
            )
            await self.send_message(message)
            await user_leave(self)
        self.pong_received = True

    async def send_message(self, message: Message):
        data_format = message.to_dict()
        if message.message_type == Message.PUBLIC:
            message_history.append(json.dumps(data_format) + "\n")
        await send_data(self, data_format)


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
        client: Client
        for client in clients.values():
            if client.connected:
                if client.pong_received:
                    client.pong_received = False
                else:
                    await user_leave(client)

                client.time = time.time()
                message = Message(
                    sender="Server",
                    message="Ping",
                    message_type=Message.SYN,
                    time=time.time(),
                    post_flag=True,
                )
                await send_message(client, message)

        await asyncio.sleep(delay=5)


async def broadcast(data, sender="Server", message_type=Message.CHAT):
    # Server side broadcast, this will broadcast the message to all other users in the same channel.
    data_format = {
        "sender": sender,
        "message": data,
        "message_type": message_type,
        "time": time.time(),
        "is_post:": True,
    }
    if chat_history:
        # Appends all messages to the temp message history list
        if message_type == Message.CHAT:
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


async def send_message(client, message: Message):
    data_format = message.to_dict()

    if message.message_type == Message.PUBLIC:
        message_history.append(json.dumps(data_format) + "\n")
    await send_data(client, data_format)


# Sends the log.txt contents to a client. This is still WIP considering it can and may
# Overflow the network stream with tons of data. I will have to add some sort of chunking
async def send_history(client):
    async with aiofiles.open("./logs.txt", "r") as f:
        history_lines = await f.readlines()
        if len(history_lines) > 0:
            for line in history_lines:
                line = line.strip("\n")
                line = json.loads(line)
                # no need for a Message instance since its already in format from the file, can just send
                await send_data(client, line)


# This is the client handler, this is responsible for all client actions
async def handle_client(client: Client):
    """
    Handles the client and acts as the main guard for errors.
    Will not work until the user has logged in."""
    while client.logged_in:
        message: (Message|None) = await client.receive_data()
        if message is None:
            return
        try:
            message_data: str = message.message
        except Exception as e:
            message = Message(
                sender="Server",
                message="The message sent is not in the correct format!",
                message_type=Message.ERROR,
                time=time.time(),
            )
            await send_message(client, message)
            continue

        if len(message_data) > message_size:
            message = Message(
                sender="Server",
                message=f"Message exceeds the {message_size} char size limit.",
                message_type=Message.ERROR,
                time=time.time(),
            )
            await send_message(client, message)
            continue
        elif len(message_data.strip()) == 0:
            continue

        # default escape_code = "\\"
        # prefix = Commands.Commands.prefix (default = //)

        # This checks to see if the message type is an ACK, can also be added to all client side messages for a better.
        # Reference for messages
        print(message.message)
        print(message_data)
        if message.message_type == Message.ACK:
            await client.keep_alive(message)
            continue
        print(message_data)
        if message_data.startswith(Commands.Commands.prefix) and len(
            message_data
        ) > len(Commands.Commands.prefix):
            print("w")
            # Returns a status from the Commands.py file, either None, or a String error.
            status = await Commands.check_command(client, message_data)
            if status is not None:
                if client.show_command:
                    # If the command is set to public, the usage and the output will be shown for everyone.
                    await broadcast(message_data)
                    await broadcast(status)
                else:
                    # Other-wise it will be a local message. Only the person who sent it will see.
                    await client.send_message(
                        Message(
                            sender=client,
                            message=message_data,
                            message_type=Message.PUBLIC,
                            time=time.time(),
                        )
                    )
                    await client.send_message(
                        Message(
                            sender=client,
                            message=status,
                            message_type=Message.PUBLIC,
                            time=time.time(),
                        )
                    )

        else:
            message_data = message_data.replace(
                escape_code + Commands.Commands.prefix, Commands.Commands.prefix
            )
            await broadcast(message_data, sender=client)


# Login will wait until a correct username and pass have been submitted.
# There is no checking password, usernames and no database at the moment.
# Purely for testing and annoyance of testing.

# TODO add a optional login option


class Status:
    # Status messages for Message.STATUS
    TAKEN = "TAKEN"  # Username is taken
    BANNED = "BANNED"  # User is banned
    USER_LENGTH = "USER_LENGTH"  # User name length is too long or short
    PERMIT = "PERMIT"  # Lets user know action was succesful
    DENY = "DENY"  # Lets user know that they were denied
    LOGGED_IN = "LOGGED_IN"  # Lets user know they are logged in


async def login(client: Client):
    data = {"username_length": username_len, "message_length": message_size}
    await client.send_message(
        Message(
            sender="Server", message=data, message_type=Message.INFO, post_flag=True
        )
    )

    while not client.logged_in:
        message: Message = await client.receive_data()
        if message.message_type == Message.LOGIN:
            try:
                message_data = message.message
                print(message_data)
                username: str = message_data["username"]
                password: str = message_data[
                    "password"
                ]  # Do nothing with the password at the moment
            except (KeyError, TypeError) as e:
                await client.send_message(
                    Message(
                        sender="Server",
                        message="Invalid Login Format",
                        message_type=Message.ERROR,
                        time=time.time(),
                    )
                )
                await user_leave(client)
                return

        if len(username) > username_len:
            await client.send_message(
                Message(
                    sender="Server",
                    message=Status.USER_LENGTH,
                    message_type=Message.INFO,
                )
            )
            continue

        if username in banned_users:
            await client.send_message(
                Message(
                    sender="Server", message=Status.BANNED, message_type=Message.STATUS
                )
            )
            await user_leave(client)
            return

        if username in clients.keys():
            await client.send_message(
                Message(
                    sender="Server", message=Status.TAKEN, message_type=Message.INFO
                )
            )
            continue

        await client.send_message(
            Message(sender="Server", message=Status.PERMIT, message_type=Message.STATUS)
        )
        client.logged_in = True
        client.username = username
        clients[client.username] = client
        await client.send_message(
            Message(
                sender="Server", message=Status.LOGGED_IN, message_type=Message.STATUS
            )
        )


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
        server = await asyncio.start_server(
            client_connected, host, port, ssl=ssl_context
        )
    else:
        server = await asyncio.start_server(client_connected, host, port)

    print("Server started!")
    # await log_timer()
    # WIP, so it is commented out even if you attempt to use the variable
    await keep_alive_timer()
    async with server:
        await server.serve_forever()


asyncio.run(run_server())
