import json
import time
import asyncio
from misc.settings import Settings


# temp solution to having 2 files needing access to the same data and
# functions, as per the name Temp.py

clients = dict()
banned_users = set()
channels = dict()
# TODO add a channel permission dict and use that instead. 
# This will allow for channels to have thier own permission
# Special permissions will override all others, this is a future feature

# These are events that are used for commands such as input-test shown in Commands.py
command_response_event = asyncio.Event()
command_request_event = asyncio.Event()

class Output:
    command_output = None

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
    COMMAND = "COMMAND"
    CHANNEL_LEAVE = "CHANNEL_LEAVE"
    CHANNEL_JOIN = "CHANNEL_LEAVE"
    CHANNEL_CREATE = "CHANNEL_LEAVE"

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


# Sends a message to the client
async def send_message(client, message): #Delimter = '\n' EOF marker
    if client.connected:
        if isinstance(message, Message):
            message = message.to_dict()
        message = (json.dumps(message) + '\n')
        message = message.encode()
        client.writer.write(message)
        await client.writer.drain()

class Client:
    """
    Client class. This class stores information about the instance such as permission levels, usernames, tasks,
    command history's and more. It is what is passed around in the server.
    """
    keep_alive_wait_time = 10 # Waits 10 seconds before disconnecting of no response.

    def __init__(self, reader, writer, task):
        self.reader = reader
        self.writer = writer
        self.task = task

        self.logged_in = False
        self.username = None
        self.connected = True
        self.current_channel:Channel = None
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
            await self.leave()
            return

    async def keep_alive(self, message: Message):
        # This checks the time difference and determines if the client is still connected / active.
        client_time = message.time
        time_now = time.time()
        delta_time = round(time_now - client_time)
        if delta_time > Client.keep_alive_wait_time:
            message = Message(
                sender="Server",
                message="Connection issues..KEEP ALIVE.",
                message_type=Message.ERROR,
            )
            await send_message(self, message)
            await self.leave()
        self.pong_received = True

    async def leave(self):  # Closes the connection server side, client is responsible for closing on their side
        self.connected = False
        self.task.cancel()
        if self.username is not None:
            del clients[self.username]
            if self.current_channel is not None:
                await self.current_channel.remove_user(self)
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

class Channel:
    def __init__(self, name):
        self.name = name
        self.clients = []
        channels[name] = self
    
    async def send(self, message:Message):
        for client in self.clients:
            await send_message(client, message)

    @staticmethod
    async def update_channels(target=None):
        # Sends a list of the channels to all clients after a creation or deletion
        channel_names = [name for name in channels.keys()]
        message = Message(sender="Server", message={'channels':channel_names}, message_type=Message.INFO, time=time.time(), post_flag=True)
        
        if target is not None:
            await send_message(target, message)
        else:
            for client in clients.values():
                await send_message(client, message)

    async def update_channel_users(self):
        # Sends a message to all users of the new user list
        usernames = [client.username for client in self.clients]
        message = Message(sender="Server", message={'users':usernames}, message_type=Message.INFO, time=time.time(), post_flag=True)
        for client in self.clients:
            await send_message(client, message)

    async def add_user(self, *clients):
        message = Message(sender="Server", message=self.name, message_type=Message.CHANNEL_JOIN, time=time.time(), post_flag=True)
        for client in clients:
            previous_channel = client.current_channel
            if isinstance(previous_channel, Channel):
                # Transfer case, 1 channel to the next.
                await previous_channel.remove_user(client)
            self.clients.append(client)
            client.current_channel = self  # Update the client's current_channel
            await send_message(client, message)
        await self.update_channel_users()

    async def remove_user(self, *clients):
        message = Message(sender="Server", message=main_channel.name, message_type=Message.CHANNEL_LEAVE, time=time.time(), post_flag=True)
        for client in clients:
            if client in self.clients:
                self.clients.remove(client)
                #client.current_channel = None  # Update the client's current_channel
                await send_message(client, message)
        await self.update_channel_users()

    async def delete_channel(self):
        await main_channel.add_user(*self.clients)
        self.clients.clear()
        del channels[self.name]
        await self.update_channels()

main_channel = Channel('Main')
channels[main_channel.name] = main_channel


class Status:
    TAKEN = "TAKEN"  # Username is taken
    BANNED = "BANNED"  # User is banned
    USER_LENGTH = "USER_LENGTH"  # User name length is too long or short
    PERMIT = "PERMIT"  # Lets user know action was succesful
    DENY = "DENY"  # Lets user know that they were denied
    LOGGED_IN = "LOGGED_IN"  # Lets user know they are logged in


