import time
import json
import asyncio
from misc.storage import clients, user_events
from misc.message import Message
from misc.channel import Channel, hub_channel

class Client:
    keep_alive_wait_time = 20

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.logged_in = False
        self.connected = True
        self.pong_received = True
        self.command_history = []
        self.last_ping_time = time.time()

        self.id: int|None = None
        self.username: str = None
        self.current_channel: Channel = None

    async def receive_data(self) -> Message:
        data = (await self.reader.readuntil(b"\n")).decode()
        data = json.loads(data)
        message = await Message.from_dict(data)
        return message
    
    async def send_message(self, message: Message) -> None:
        if isinstance(message, Message):
            message = await message.to_dict()
        message = (json.dumps(message) + '\n')
        message = message.encode()
        self.writer.write(message)
        await self.writer.drain()

    async def leave(self) -> None:
        self.connected = False
        if self.username is not None:
            del clients[self.username]
            if self.id in user_events:
                del user_events[self.id]
            await self.leave_channel(self)
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

    async def leave_channel(self) -> None:
        if self.current_channel != hub_channel:
            await self.current_channel.leave_channel(self)
        
    async def join_channel(self, channel: Channel) -> None:
        if channel != hub_channel:
            channel.join_channel(self)
