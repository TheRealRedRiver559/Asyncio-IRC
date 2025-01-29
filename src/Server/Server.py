import asyncio
import time
import importlib
import misc.Commands as Commands
from misc.Commands import server_broadcast
from misc.authorization import handle_authorization
from misc.message import Message, MessageType, MessageSubType
from misc.event import Event
from misc.client import Client
from misc.channel import Channel, main_channel, hub_channel
from misc.storage import reload_event, clients, user_events, channel_events, server_events, prefix, channels, message_queue
from misc.database import cursor, conn
from misc.settings import MESSAGE_SIZE, ESCAPE_CODE, USERNAME_LEN, HOST, PORT, PING_INTERVAL, PING_THRESHOLD
from misc.logging import add_log, process_log_queue



async def reload_event_waiter() -> None:
    # waits for a reload event for hot-reloading commands.py without restarting the server.
    while True:
        await reload_event.wait()
        importlib.reload(Commands)
        reload_event.clear()

async def keep_alive_timer() -> None:
    while True:
        current_time = time.time()
        client: Client
        for client in clients.values():
            if client.connected:
                if client.last_ping_time is None:
                    client.last_ping_time = current_time
                time_dif = current_time - (client.last_ping_time+PING_INTERVAL)
                if time_dif < PING_THRESHOLD:
                    client.last_ping_time = current_time
                    ping_message = Message(sender="Server", message="Ping", main_type=MessageType.CONN, sub_type=MessageSubType.SYN)
                    await client.send_message(ping_message)
                else:
                    await client.leave()
        await asyncio.sleep(PING_INTERVAL)

async def check_events(client:Client, message:Message) -> bool:
    # ran on every input message, checks for event responses where the server may be asking for something.
    client_id = client.id
    client_channel = client.current_channel
    if user_events:
        if client_id in user_events:
            user_queue = user_events[client_id]
            user_event:Event = await user_queue.get()
            await user_event.response(message=message)
            return True
    elif channel_events:
        if client_channel.id in channel_events:
            channel_queue = channel_events[client_channel.id]
            if channel_queue.empty():
                return False
            channel_event = await channel_queue.get()
            await channel_event.response(message=message)
            return True
    elif not server_events.empty():
        server_event:Event = await server_events.get()
        await server_event.response(message=message)
        return True

async def process_messages() -> None:
    while True:
        try:
            message: Message
            client: Client
            client, message = await message_queue.get()
            await client._send(message)       
            message_queue.task_done()
        except (asyncio.IncompleteReadError, ConnectionResetError, ConnectionAbortedError):
            continue

async def broadcast(message: Message, channel: Channel = None, from_server=False) -> None:
    # broadcasts a message to all clients, or to a certain channel when specified
    if from_server:
        message.sender = 'Server' 
    if channel:
        await channel.broadcast(message)
        await add_log('MESSAGE', message.message)
    else:
        for channel in channels.items():
            channel.broadcast(message)

async def handle_client(client: Client) -> None:
    message = Message("Server", 
                      'Welcome to the server! This is the Hub channel, only you can see your messages. To chat publicly, join another channel or create one.',
                      main_type=MessageType.CHAT, sub_type=MessageSubType.GENERAL)
    await client.send_message(message)
    # handles the client. Recieves messages, sends messages, handles Ping / Pong and more
    while client.connected:
        message: (Message|None) = await client.receive_data()
        if message is None:
            await client.leave()
            return

        message_data = message.message
        if isinstance(message_data, dict):
            continue
        if len(message_data) > MESSAGE_SIZE:
            message = Message(
                sender="Server",
                message=f"Message exceeds the {MESSAGE_SIZE} char size limit.",
                main_type=MessageType.ERROR,
                sub_type=MessageSubType.MESSAGE_LENGTH
            )
            await client.send_message(message)
            continue
        elif len(message_data.strip()) == 0:
            continue
        if message.sub_type == MessageSubType.ACK: # If ACK (Ping) update the current time.
            client.last_ping_time = time.time()
            continue

        events = await check_events(client, message=message)
        if events: # If an event is active, the message will be used for that event instead of being broadcasted.
            # its up to the event on what happens with the data next.
            continue

        if message_data.startswith(prefix) and len(message_data) > len(prefix): # checks if the message starts with a command prefix and has length.
            async with asyncio.TaskGroup() as tg, asyncio.timeout(10): # TODO 10 second command timeout. Need to grab this dynamically from the command.
                tg.create_task(Commands.execute_command(message))

        else:
            message_data = message_data.replace(
                ESCAPE_CODE + prefix, prefix
            )
            channel:Channel = client.current_channel
            if channel != hub_channel:
                await channel.broadcast(message)
            else:
                await client.send_message(message)

async def send_connect_data(client: Client) -> None:
    # sends common data on first connection such as max message lengths and more.
    data = {"username_length": USERNAME_LEN, "message_length": MESSAGE_SIZE}
    await client.send_message(
        Message(
            sender="Server", message=data, main_type=MessageType.INFO, sub_type=MessageSubType.CONNECT_DATA 
        )
    )
    
async def handle_credentials(client:Client) -> None:
    while not client.logged_in:
        message: Message = await client.receive_data()
        if not message:
            continue
        message_data = message.message

        if message.main_type != MessageType.AUTH:
            await client.send_message(Message(
                sender="Server",
                message="You must authorize before attempting to use other message types. Include MessageType.AUTH in main_type",
                main_type=MessageType.ERROR,
                sub_type=MessageSubType.INVALID_FORMAT))
            await client.leave()
            return
        
        invalid_data_message = Message(
            sender="Server",
            message="Invalid Login Format. Correct format is: {'username':data, 'password':data}",
            main_type=MessageType.ERROR,
            sub_type=MessageSubType.INVALID_FORMAT)
        
        if not isinstance(message_data, dict):
            await client.send_message(invalid_data_message)
            await client.leave()
            return

        username:str = message_data.get("username", False)
        password:str = message_data.get("password", False)
        if not all([username, password]):
            await client.send_message(invalid_data_message)
            await client.leave()
            return
        
        if message.sub_type in (MessageSubType.LOGIN, MessageSubType.REGISTER):
            if len(username) > USERNAME_LEN:
                await client.send_message(Message(sender="Server",message=f"Username exceeds the {USERNAME_LEN} character limit.", main_type=MessageType.ERROR, sub_type=MessageSubType.USERNAME_LENGTH))
                continue
        else:
            invalid_data_message.message = "Missing required MessageSubType. Must be MessageSubType.LOGIN or MessageSubType.REGISTER "
            await client.send_message(invalid_data_message)
            await client.leave()
            return
        
        authorized = await handle_authorization(client, message, username, password)
        if not authorized:
            continue

        await Channel.update_channels(client)
        cursor.execute("SELECT * FROM BannedUsersChannel WHERE user_id = ? AND channel_id = ?;", (client.id,hub_channel.channel_id,))
        channel_record = cursor.fetchone()
        if channel_record:
            await client.send_message(Message(sender="Server", message='You are banned from the server!', main_type=MessageType.STATUS, sub_type=MessageSubType.BANNED))
            client.leave()
            return

        client.logged_in = True
        client.username = username
        clients[client.username] = client
        await client.join_channel(hub_channel)

        await client.send_message(Message(sender="Server", message='Success', main_type=MessageType.STATUS, sub_type=MessageSubType.PERMIT))
        await client.send_message(Message(sender="Server", message='Logged in.', main_type=MessageType.STATUS, sub_type=MessageSubType.PASSED_LOGIN))
        await add_log('INFO', f'{client.username} logged in.')


async def client_connected(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    # This is the first function that is called when a client connects, it makes a client object and starts everything.
    # Adds a client task, reader, and writer to object for future refrencing.
    await add_log('CONNNECTION', 'Client connected')
    task = asyncio.current_task()
    client = Client(reader, writer, task)
    await send_connect_data(client)
    await handle_credentials(client)
    await handle_client(client)
    
# This is the main function, this starts the server and accepts all connections
async def run_server() -> None:
    server = await asyncio.start_server(client_connected, HOST, PORT)

    await add_log('SYSTEM', 'Server Started!')
    print("Server started!")
    
    async with asyncio.TaskGroup() as tg:
        tg.create_task(process_messages())
        tg.create_task(keep_alive_timer())
        tg.create_task(reload_event_waiter())
        tg.create_task(process_log_queue())

    server.close()

asyncio.run(run_server())
