import asyncio
import misc.Commands as Commands
import time
#from passlib.hash import argon2

import ssl
from misc.Temp import clients, banned_users, Channel, Message, Client, Status,\
    command_response_event, command_request_event, Output, main_channel,send_message

# WARNING
# This is a test server, there is currently no encrpytion or checks to prevent agasint exploits
# Please do no tuse this for any purpose except for learning at the moment. It is still in devolopment!

host, port = ("localhost", 9090)

message_size = 200
username_len = 10
escape_code = "\\"
cert, key = "./certs/cert.pem", "./certs/private.key"  # self signed cert, and

ssl_connection = False

async def keep_alive_timer():
    while True:
        for client in clients.values():
            if client.connected:
                if client.pong_received:
                    client.pong_received = False
                else:
                    await client.leave()

                client.time = time.time()
                message = Message(sender="Server",message="Ping",message_type=Message.SYN,time=time.time(),post_flag=True)
                await send_message(client, message)

        await asyncio.sleep(5)


async def broadcast(message : Message, to_all=False, channel=main_channel):
    sender = message.sender
    if to_all:
        for client in clients.values():
            await send_message(client, message)
            return
            
    if isinstance(sender, Client):
        client = sender
        channel :Channel= client.current_channel
        print(channel, channel.name, channel.clients)

        for client in channel.clients:
            await send_message(client, message)
    elif sender in clients:
        client = clients[sender]
        channel :Channel= client.current_channel
        await channel.send(message)
    else:
        for client in clients.values():
            await send_message(client, message)


async def handle_client(client: Client):
    await main_channel.add_user(client)
    await Channel.update_channels(target=client)
    while True:
        message: (Message|None) = await client.receive_data()
        if message is None:
            return
        
        message_data = message.message
        if command_request_event.is_set():
            if message.message_type != Message.ACK:
                Output.command_output = message
                command_response_event.set() # TODO make this not a global event, very easy (accidentlly made public interactions)
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

        if message.message_type == Message.ACK:
            try:
                await client.keep_alive(message)
            except Exception as e:
                print(e)
            continue
            

        if message_data.startswith(Commands.Commands.prefix) and len(message_data) > len(Commands.Commands.prefix):
            asyncio.create_task(Commands.execute_command(message))

        else:
            message_data = message_data.replace(
                escape_code + Commands.Commands.prefix, Commands.Commands.prefix
            )
            await broadcast(message)

async def send_connect_data(client:Client):
    data = {"username_length": username_len, "message_length": message_size}
    await send_message(client, 
        Message(
            sender="Server", message=data, message_type=Message.INFO, post_flag=True
        )
    )

async def send_details(client:Client):
    client_perm = client.permission_level
    slash_commands = []
    for name, command_perm in Commands.Commands.slash_commands.items(): # name, permission_level
        if client_perm >= command_perm:
            slash_commands.append(name)
    data = {"prefix": Commands.Commands.prefix, "slash_commands": slash_commands}
    await send_message(client, 
        Message(
            sender="Server", message=data, message_type=Message.INFO, post_flag=True
        )
    )

async def login(client:Client):
    while not client.logged_in:
        message: Message = await client.receive_data()

        try:
            message_data = message.message
            username: str = message_data["username"]
            password: str = message_data["password"]
        except (KeyError, TypeError) as e:
                await send_message(client,
                    Message(
                        sender="Server",
                        message="Invalid Login Format",
                        message_type=Message.ERROR,
                        time=time.time(),
                    )
                )
                await client.leave()
                return

        if len(username) > username_len:
            await send_message(client,
                Message(
                    sender="Server",
                    message=Status.USER_LENGTH,
                    message_type=Message.INFO,
                )
            )
            continue

        if message.message_type == Message.LOGIN:
            if username in banned_users:
                await send_message(client,
                    Message(
                        sender="Server", message=Status.BANNED, message_type=Message.STATUS
                    )
                )
                await client.leave()
                return

            if username in clients.keys():
                await send_message(client,
                    Message(
                        sender="Server", message=Status.TAKEN, message_type=Message.INFO
                    )
                )
                continue

        await send_message(client,
            Message(sender="Server", message=Status.PERMIT, message_type=Message.STATUS)
        )
        client.logged_in = True
        client.username = username
        async with lock:
            clients[client.username] = client
        await send_message(client,
            Message(
                sender="Server", message=Status.LOGGED_IN, message_type=Message.STATUS
            )
        )


# This is the first function that is called when a client connections, it makes a client object and starts everything.
async def client_connected(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    task = asyncio.current_task()
    client = Client(reader, writer, task)
    await send_connect_data(client)
    await login(client)
    await send_details(client)
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

    keep_alive_task = asyncio.create_task(keep_alive_timer())
    
    async with server:
        await asyncio.gather(server.serve_forever(), keep_alive_task)

asyncio.run(run_server())
