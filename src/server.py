import asyncio
import time
import importlib
import misc.commands as Commands
from misc.message import Message, MessageType, MessageSubType
from misc.event import Event
from misc.client import Client
from misc.channel import Channel, main_channel, hub_channel
from misc.storage import reload_event, clients, user_events, channel_events, server_events
from misc.database import cursor, conn
from misc.settings import MESSAGE_SIZE, ESCAPE_CODE, USERNAME_LEN, HOST, PORT, PING_INTERVAL
from misc.logging import add_log, process_log_queue

async def reload_event_waiter():
    while True:
        await reload_event.wait()
        importlib.reload(Commands)
        reload_event.clear()

async def keep_alive_timer():
    while True:
        current_time = time.time()
        for client in clients.copy().values():
            if client.connected:
                # Check if the interval has passed since the last ping
                if current_time - client.last_ping_time > PING_INTERVAL:
                    client.last_ping_time = current_time  # Update the last ping time

                    if not client.pong_received:
                        await client.leave()  # Disconnect if pong not received
                    else:
                        client.pong_received = False  # Reset pong received status

                    # Send new ping message
                    ping_message = Message(sender="Server", message="Ping", main_type=MessageType.CONN, sub_type=MessageSubType.SYN)
                    await client.send_message(ping_message)
        
        await asyncio.sleep(5)

async def check_events(client:Client, message:Message): # Checks the event in a dict of events. If the user id matches it returns that event
    client_id = client.id
    client_channel = client.current_channel
    try:
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
    except Exception as e:
        print('error2 ', e)

async def broadcast(message : Message,to_all=False, channel=main_channel):
    sender = message.sender
    if sender != "Server":
        client = clients[sender]
    
    if to_all:
        for client in clients.values():
            await add_log('MESSAGE', message.message)
            await client.send_message(message)
    else:
        channel :Channel= client.current_channel
        if channel == hub_channel: # cannot broadcast messages to others in hub_channel
            await add_log('MESSAGE', message.message)
            await client.send_message(message) # relays the senders message for viewing
        else:
            for client in channel.channel_clients:
                await add_log('MESSAGE', message.message)
                await client.send_message(message)


async def handle_client(client: Client):
    while True:
        message: (Message|None) = await client.receive_data()
        if message is None:
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

        if message.sub_type == MessageSubType.ACK:
            client.last_ping_time = time.time()

        events = await check_events(client, message=message)
        if events:
            continue

        if message_data.startswith(Commands.Commands.prefix) and len(message_data) > len(Commands.Commands.prefix):
            async with asyncio.TaskGroup() as tg, asyncio.timeout(20):
                tg.create_task(Commands.execute_command(message))

        else:
            message_data = message_data.replace(
                ESCAPE_CODE + Commands.Commands.prefix, Commands.Commands.prefix
            )
            await broadcast(message)

async def send_connect_data(client:Client):
    data = {"username_length": USERNAME_LEN, "message_length": MESSAGE_SIZE}
    await client.send_message(
        Message(
            sender="Server", message=data, main_type=MessageType.INFO, sub_type=MessageSubType.CONNECT_DATA 
        )
    )

async def login(client:Client):
    while not client.logged_in:
        message: Message = await client.receive_data()
        if not message:
            continue
        try:
            message_data = message.message
            username: str = message_data["username"]
            password: str = message_data["password"]
        except (KeyError, TypeError) as e:
                await client.send_message(                    Message(
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

        elif message.sub_type == MessageSubType.REGISTER:
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


# This is the first function that is called when a client connections, it makes a client object and starts everything.
async def client_connected(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    await add_log('CONNNECTION', 'Client connected')
    client = Client(reader, writer)
    await send_connect_data(client)
    await login(client)
    await add_log('INFO', f'{client.username} logged in.')
    await handle_client(client)

# This is the main function, this starts the server and accepts all connections
async def run_server():
    server = await asyncio.start_server(client_connected, HOST, PORT)

    await add_log('SYSTEM', 'Server Started!')
    print("Server started!")
    
    async with asyncio.TaskGroup() as tg:
        tg.create_task(keep_alive_timer())
        tg.create_task(reload_event_waiter())
        tg.create_task(process_log_queue())

    server.close()

asyncio.run(run_server())
