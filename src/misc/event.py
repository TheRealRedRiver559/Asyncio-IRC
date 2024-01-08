import asyncio
from misc.storage import user_events, channel_events, server_events

class Event:

    def __init__(self, context_type: str, context_id: int):
        self.response_event = asyncio.Event() # response event for when the user responds back to the event
        self.request_event = asyncio.Event() # request event. This is set when you await return data
        self.output_message: None|str = None
        self.context_type: str = context_type # context types (eg : user, channel, server) could be for specific users, or public games etc
        self.context_id = context_id # the id of the server, user, channel etc

    async def request(self) -> str:
        if self.context_type == 'user':
            user_queue:(asyncio.Queue|False) = user_events.get(self.context_id, False)
            if user_queue:
                await user_queue.put(self)
            else:
                user_queue = asyncio.Queue()
                user_events[self.context_id] = user_queue
                await user_queue.put(self)
        elif self.context_type == 'channel':
            channel_queue:(asyncio.Queue|False) = user_events.get(self.context_id, False)
            if channel_queue:
                await channel_queue.put(self)
            else:
                channel_queue = asyncio.Queue()
                channel_events[self.context_id] = channel_queue
                await channel_queue.put(self)

        elif self.context_type == 'server':
            await server_events.put(self)
                
        self.request_event.set()
        await self.response_event.wait()
        return self.output_message
    
    async def response(self, message: str) -> None: 
        if self.context_type == 'user':
            event_queue:asyncio.Queue = user_events[self.context_id]
            if event_queue.empty():
                user_events.pop(self.context_id)
        self.output_message = message
        self.response_event.set()
