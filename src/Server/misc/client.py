import time
import json
import asyncio
from typing import TYPE_CHECKING
from misc.storage import clients, user_events, message_queue
from misc.message import Message

if TYPE_CHECKING:
    from misc.channel import Channel

class Client:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, task: asyncio.Task):
        self.reader = reader
        self.writer = writer
        self.task = task
        self.logged_in = False
        self.connected = True
        self.pong_received = True
        self.command_history = []
        self.last_ping_time = None

        self.id: int|None = None
        self.username: str = None
        self.current_channel: 'Channel' = None

    async def receive_data(self) -> Message:
        try:
            data = (await self.reader.readuntil(b"\n")).decode()
            data = json.loads(data)
            message = await Message.from_dict(data)
            return message
        except Exception as e:
            #print(f'Exception happend on recieving data with client: {self.username}. Exception: {e}')
            return None
    
    async def send_message(self, message: Message) -> None:
        await message_queue.put((self, message))
    
    async def _send(self, message: Message) -> None:
        message = await message.to_dict()
        message = (json.dumps(message) + '\n')
        message = message.encode()
        self.writer.write(message)
        await self.writer.drain()

    async def leave(self) -> None:
        if not self.connected:
            return
        self.connected = False
        del clients[self.username]
        if self.id in user_events:
            del user_events[self.id]
        await self.current_channel._remove_user(self)
        self.writer.close()

    async def leave_channel(self) -> None:
        await self.current_channel.leave_channel(self)
        
    async def join_channel(self, channel: 'Channel') -> None:
        await channel.join_channel(self)
