import asyncio
import time
import importlib
import misc.commands as Commands
from misc.commands import server_broadcast
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

# TODO re add keep-alive
async def keep_alive_timer() -> None:
    # loops through the connected clients and sends a SYN ("ping") message every PING_INTERVAL seconds.
    # If the time diff is greater than PING_THRESHOLD, the user is disconncted due to timeout.
    while True:
        current_time = time.time()
        client: Client
        for client in clients.copy().values():
            if client.connected:
                if client.last_ping_time is None:
                    client.last_ping_time = current_time
                time_dif = current_time - client.last_ping_time
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
    elif not server_events.empty(): #unsure of order. User then channel? Or both? Not sure
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
            client.pong_received = True
            client.last_ping_time = time.time()

        events = await check_events(client, message=message)
        if events: # If an event is active, the message will be used for that event instead of being broadcasted.
            # its up to the event on what happens with the data next.
            continue

        if message_data.startswith(prefix) and len(message_data) > len(prefix): # checks if the message starts with a command prefix and has length.
            async with asyncio.TaskGroup() as tg, asyncio.timeout(10):
                tg.create_task(Commands.execute_command(message))

        else:
            message_data = message_data.replace(
                ESCAPE_CODE + prefix, prefix
            )
            channel:Channel = client.current_channel
            await channel.broadcast(message)

async def send_connect_data(client: Client) -> None:
    # sends common data on first connection such as max message lengths and more.
    data = {"username_length": USERNAME_LEN, "message_length": MESSAGE_SIZE}
    await client.send_message(
        Message(
            sender="Server", message=data, main_type=MessageType.INFO, sub_type=MessageSubType.CONNECT_DATA 
        )
    )
# TODO move to seperate folder where "register" and "login" will be stored. Same with delete account and other user funcs. 
async def login(client:Client) -> None:
    # Asks the user to login. Checks the login against databases and other login checks.
    while not client.logged_in:
        message: Message = await client.receive_data()
        if not message:
            continue
        try:
            message_data = message.message
            username: str = message_data["username"]
            password: str = message_data["password"]
        except (KeyError, TypeError) as e:
                await client.send_message(Message(
                        sender="Server",
                        message="Invalid Login Format. Correct format is: {'username':data, 'password':data}",
                        main_type=MessageType.ERROR,
                        sub_type=MessageSubType.INVALID_FORMAT
                    )
                )
                await client.leave()
                return

        if len(username) > USERNAME_LEN:
            await client.send_message(Message(sender="Server",message=f"Username exceeds the {USERNAME_LEN} character limit.", main_type=MessageType.ERROR, sub_type=MessageSubType.USERNAME_LENGTH))
            continue
        cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
        user_record = cursor.fetchone()
        
        if message.sub_type == MessageSubType.LOGIN:
            if user_record is None:
                await client.send_message(Message(sender="Server", message='Invalid username or password.', main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
                continue

            user_id, record_username, record_password = user_record
            client.id = user_id
            if username != record_username or password != record_password:
                await client.send_message(Message(sender="Server", message='Invalid username or password.', main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
                continue

            if username in clients.keys():  # User already logged in.
                await client.send_message(Message(sender="Server", message="User is already online.", main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
                continue

        elif message.sub_type == MessageSubType.REGISTER: # TODO move this to a seperate function or file.
            if user_record is not None:
                await client.send_message(Message(sender="Server", message='Username is already taken.', main_type=MessageType.ERROR, sub_type=MessageSubType.USERNAME_TAKEN))
                continue

            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?);", (username, password,))
            client.id = cursor.lastrowid
            cursor.execute("INSERT INTO UserChannelPermissions (user_id, channel_id, permission_level) VALUES (?, ?, ?);", (client.id, hub_channel.channel_id, 1,))
            conn.commit()
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
    await login(client)
    await handle_client(client)
    
# This is the main function, this starts the server and accepts all connections
async def run_server() -> None:
    server = await asyncio.start_server(client_connected, HOST, PORT)

    await add_log('SYSTEM', 'Server Started!')
    print("Server started!")
    
    async with asyncio.TaskGroup() as tg:
        tg.create_task(process_messages())
        #tg.create_task(keep_alive_timer())
        tg.create_task(reload_event_waiter())
        tg.create_task(process_log_queue())

    server.close()

asyncio.run(run_server())