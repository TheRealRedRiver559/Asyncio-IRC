import inspect
import time

from misc.Temp import (
    clients,
    banned_users,
    channels,
    Channel,
    Message,
    Client,
    command_response_event,
    command_request_event,
    Output,
    main_channel,
    send_message,
)

        
# Command holder and decorator for adding new commands
# Takes in name, permission for commands, usage, and whether it show as a slash command
class Commands:
    prefix = "//"
    commands = {}
    slash_commands = {}
    killed_commands = set()

    def command(name: str, permission=1, show_usage=True, slash_command=True):
        def wrapper(command):
            if slash_command:
                Commands.slash_commands[name] = permission
            Commands.commands[name] = [command, permission, show_usage]
            return command

        return wrapper


async def help_text(): # Just generic help text. Badly formatted
    text = f"""Commnads:
        {Commands.prefix}help   ->  returns a useful list of available commands and their usages.
        {Commands.prefix}create-channel <channel name> (private)  ->   Creates a channel with the specified name.
        {Commands.prefix}join-channel <channel name>   ->  Joins specified channel.
        {Commands.prefix}leave-channel  ->  leaves the current channel you are in. 
        {Commands.prefix}delete-channel <channel name>   ->  Deletes the specified channel name if it exists.
        {Commands.prefix}users  ->  returns a list of all online users in the server.
        {Commands.prefix}user-count     ->  returns a numeric amount of users online.
        {Commands.prefix}banned-users   ->  returns a list of all banned-users.
        {Commands.prefix}broadcast <message>    ->  broadcasts a message as the server.
        {Commands.prefix}ban <username> (reason)    ->  bans a user with an optional reason.
        {Commands.prefix}unban <username> ->    unbans a specified user.
        {Commands.prefix}disable-command <command name>     ->  diables the specified command.
        {Commands.prefix}enable-command <command name>  ->  enables the specified command.
        {Commands.prefix}set-prefix <new prefix>  ->  changes commmand prefix.
        {Commands.prefix}channels  ->  returns a list of active channels.
        {Commands.prefix}command-history  ->  returns a list of prevously used commands by the user.
        {Commands.prefix}set-perm <username> <permission level>  ->  changes the permission level of a user."""
    return text

# This sends messages 
async def send(client : Client, message : Message, to_all=False, to_channel=False):
    try:
        usage = f'{Commands.prefix}{message.message}'
        usage_message = Message(sender=message.sender, message=usage, message_type=Message.CHAT, time=time.time(), post_flag=True)
        if to_channel:
            channel = client.current_channel
            for client in channel.clients:
                await send_message(client, message)
        elif to_all:
            for client in clients:
                await send_message(client, message)
        else:
            await send_message(client, message)
    except Exception as e:
        print(e)

# Broadcasts to all users or to a certain channel
async def broadcast(message : Message, to_all=False):  # broadcasts to all users
        
        if to_all:
            for client in clients:
                await send_message(client, message)
        else:

            if isinstance(message.sender, Client):
                client : Client = message.sender
                if client.current_channel is not None:
                    channel : Channel = client.current_channel
                    for client in channel.clients:
                        await send_message(client, message)
            else:
                for client in clients.values():
                    if client.current_channel is None:
                        await send_message(client, message)

# Command history for users when they use a command. Usage is also logged
async def update_command_history(client, command_message: str):
    try:
        if len(client.command_history) == 5:  # 5, is total log amount cap
            client.command_history.pop()
        client.command_history.append(" ".join(command_message))
    except Exception as e:
        print(e)

# Executes the command. This is the command checker
async def execute_command(message: Message):
    command_response_event.clear()
    command_request_event.clear()

    message_data = message.message
    client = clients[message.sender]
    command_data = message_data.removeprefix(Commands.prefix).split()
    try: # Tries getting the command, else its not a true command
        function_name = command_data[0]
        command_permission_level = Commands.commands[function_name][1]
        show_usage = Commands.commands[function_name][2]
    except KeyError:
        await send(client, message, to_channel=True)
        message = Message(
            sender='Server',
            message=f"{function_name}, is not a command.",
            message_type=Message.CHAT
        )
        await send(client, message, to_channel=True)
        return
    
    await update_command_history(client, command_data)
    await send(client, message, to_channel=show_usage)

    if function_name in Commands.killed_commands: #Killed commands are just disabled. No one can use them
        message = Message(
            sender='Server',
            message=f"Command: {function_name} is disabled.",
            message_type=Message.CHAT
        )
        await send(client, message, to_channel=show_usage)
        return

    function = Commands.commands[function_name][0]
    func_data = inspect.getfullargspec(function)
    func_defualts = func_data.defaults or []
    func_args = func_data.args


    if len(func_args) > 0:
        func_defualts = func_args[len(func_args)-len(func_defualts):]

    if client.permission_level < command_permission_level:
        message = Message(
            sender='Server',
            message=f"Missing access to this command.",
            message_type=Message.CHAT
        )
        await send(client, message, to_channel=show_usage)
        return

    pass_client = "client" in func_args
    if pass_client:
        func_args.remove("client")

    data_args = []
    if len(command_data) > 1:
        data_args = command_data[1:]
    required_args = len(func_args) - len(func_defualts)

    if len(data_args) < required_args:
        missing_parameters = func_args[:required_args]
        message = Message(
            sender="Server",
            message=f"Missing parameter(s): {', '.join(missing_parameters)}",
            message_type=Message.CHAT,
            time=time.time()
        )
        await send(client, message)
        return
    
    if pass_client:
        await function(client, *data_args)
    else:
        await function(*data_args)

#To make a basic command
# Show usage shows the actual typing of the command to other users. NOT the output
@Commands.command("test", permission=1, show_usage=True, slash_command=True)
async def test(client, x=10):
    text = 'This is a test command'
    message = Message(sender="Server", message=test, message_type=Message.CHAT, post_flag=True)
    await send(client=client, message=message, to_channel=True, to_all=False) # Sends to all in channel. 

#Broadcasts a comand to the channel
@Commands.command("broadcast", 1, show_usage=False)
async def broadcast_command(client, *message):
    if len(message) > 0:
        message = " ".join(message)
    message = Message(sender="Server", message=message, message_type=Message.CHAT, post_flag=True)

    await send(client, message, to_channel=True)

#Gives a list of users to the user
@Commands.command("users", 1, show_usage=False)
async def users_online(client):

    user_list = [x for x in clients.keys()]
    message_data = f"Users online: {user_list}"
    message = Message(sender="Server", message=message_data, message_type=Message.CHAT, time=time.time(), post_flag=True)
    await send(client, message)

# Shows a list of channels to all users in channel if using a CLI client
@Commands.command("channels", 1, show_usage=True, slash_command=True)
async def get_channels(client):
    channel_list = [x for x in channels.keys()]
    message_data = f"Channels: {channel_list}"
    message = Message(sender="Server", message=message_data, message_type=Message.CHAT, time=time.time(), post_flag=True)
    await send(client, message, to_channel=True)

# Gives a user count
@Commands.command("user-count", 1, show_usage=True, slash_command=True)
async def users_online(client):
    message = f"Number of users online: {len(clients)}"
    message = Message(sender="Server", message=message, message_type=Message.CHAT, time=time.time(), post_flag=True)
    await send(client, message, to_channel=True)

# Shows a list of banned users to the client
@Commands.command("banned-users", 1, show_usage=False)
async def users_banned(client):
    banned_list = [x for x in banned_users]
    message = f"Banned Users: {banned_list}"
    message = Message(sender="Server", message=message, message_type=Message.CHAT, time=time.time(), post_flag=True)
    await send(client, message)

#
@Commands.command("ban", 1, show_usage=True)
async def ban_user(client, *data):
    message = Message(sender="Server", message='You have been banned!', message_type=Message.INFO, time=time.time(), post_flag=True)
    target_username = data[0]

    if target_username in clients:
        target_client = clients[target_username]
        data = data[1 : len(data)]
    elif target_username in banned_users:
        message.message = "User is already banned."
        await send(client, message, to_channel=True)
        return
    else:
        message.message = "User not found."
        await send(client, message, to_channel=True)
        return

    if len(data) >= 1:
        data = " ".join(data)
        message.message = f"You have been banned for: {data}"
        await send(target_client, message, to_channel=True)

    banned_users.add(target_username)
    await target_client.leave()
    message.message = f"{target_username} has been banned."
    await send(client, message, to_channel=True)

#
@Commands.command("unban", 1)
async def unban_user(client, *data):
    message = Message(sender="Server", message='', message_type=Message.INFO, time=time.time(), post_flag=True)
    target_username = data[0]

    if target_username in banned_users:
        banned_users.remove(target_username)
        message.message = f"{target_username} has been unbanned."
        await send(client, message)
    elif target_username in clients:
        message.message = "User is not banned."
        await send(client, message)

    else:
        message.message = "User not found."
        await send(client, message)

#
@Commands.command("help", 1)
async def help(client):
    message = await help_text()

    message = Message(sender="Server", message={'help':message}, message_type=Message.INFO, time=time.time())
    await send_message(client, message)

#
@Commands.command("set-prefix", 1, show_usage=False)
async def change_prefix(client, prefix):
    Commands.prefix = prefix
    message_data = f"Prefix has been changed to: {prefix}"
    message = Message(sender="Server", message=message_data, message_type=Message.CHAT, time=time.time(), post_flag=True)
    await send_message(client, message)

#
@Commands.command("disable-command", 1, show_usage=False)
async def turn_off_command(client, command_name):
    message = Message(sender="Server", message='', message_type=Message.CHAT, time=time.time(), post_flag=True)
    if command_name in Commands.commands:
        if command_name not in Commands.killed_commands:
            if command_name == "enable-command":
               message.message = f"The command {command_name} can not be disabled."
            else:
                Commands.killed_commands.add(command_name)
                message.message = f"{command_name} has been disabled."
        else:
            message.message = f"{command_name} is already disabled."
    else:
        message.message = f"{command_name} not found."

    await send(client, message)

#
@Commands.command("enable-command", 1, show_usage=False)
async def turn_on_command(client, command_name):
    message = Message(sender="Server", message='', message_type=Message.CHAT, time=time.time(), post_flag=True)
    if command_name in Commands.commands:
        if command_name in Commands.killed_commands:
            Commands.killed_commands.remove(command_name)
            message.message = f"{command_name} has been enabled."
        else:
            message.message = f"{command_name} is already enabled."
    else:
        message.message = f"{command_name} not found."

    await send(client, message)

#
@Commands.command("join-channel", 1, show_usage=False)
async def join_channel(client, channel_name, password=None):
    message = Message(sender="Server", message=f"You have joined the channel named, {channel_name}.", message_type=Message.CHAT, time=time.time(), post_flag=True)
    
    if channel_name in channels.keys():
        channel : Channel = channels[channel_name]
        if client in channel.clients:
            message.message = f"You are already in this channel."
            message.message_type = Message.CHAT
        else:
            if channel.password_protected:
                if password == channel.password:
                    await channel.add_user(client)
                elif password is None:
                    message.message = f"This channel is password protected."
                else:
                    message.message = f"Incorrect Password."                    

            
    else:
        message.message = f"The channel {channel_name}, does not exist."

    await send(client, message)

#
@Commands.command("leave-channel", 1)
async def leave_channel(client):
    message = Message(sender="Server", message='', message_type=Message.CHAT, time=time.time(), post_flag=True)
    if client.current_channel.name != main_channel.name:
        channel : Channel = client.current_channel
        await main_channel.add_user(client)
        message.message = f"You have left the {channel.name} channel."
    else:
        message.message = f"You are not in a channel."

    await send(client, message)

#
@Commands.command("create-channel", 1)
async def create_channel(client, channel_name, password=None):
    message = Message(sender="Server", message='', message_type=Message.CHAT, time=time.time(), post_flag=True)
    if channel_name in channels.keys() or channel_name == main_channel.name:
        message.message = f"The channel {channel_name}, already exists."
    else:
        channel = Channel(channel_name)
        if password is not None:
            password = str(password)
            channel.password_protected = True
            channel.password = password

        channels[channel_name] = channel
        message.message = f"The channel {channel_name}, has been created."
        await Channel.update_channels()

    await send(client, message)

#
@Commands.command("delete-channel", 1)
async def delete_channel(client, channel_name):
    message = Message(sender="Server", message=f"The channel {channel_name} has been deleted.", message_type=Message.CHAT, time=time.time(), post_flag=True)
    if channel_name in channels.keys() and channel_name != main_channel.name:
        channel:Channel = channels[channel_name]
        await channel.delete_channel()
    else:
        message.message_type = Message.CHAT
        message.message = f"The channel {channel_name} does not exist."

    await send(client, message)

#
@Commands.command("set-perm", 1)
async def change_user_perm(client, target_username, permission_level):
    message = Message(sender="Server", message=None, message_type=Message.INFO, time=time.time(), post_flag=True)
    try:
        permission_level = int(permission_level)
    except Exception as e:
        message.message = "Permission must be an integer."
        await send(client, message)
        return

    if target_username in clients:
        target_client = clients[target_username]

    elif target_username in banned_users:
        message.message = "User is banned."
        await send(client, message)
        return
    else:
        message.message = "User not found."
        await send(client, message)
        return

    message.message = f"Your permission are set to: {permission_level}"
    target_client.permission_level = permission_level

    await send(client, message)

#
@Commands.command("command-history", 1, show_usage=False)
async def show_client_command_history(client):


    command_list = client.command_history
    message_data = f"Command History: {command_list}"
    message = Message(sender="Server", message=message_data, message_type=Message.INFO, time=time.time(), post_flag=True)
    await send(client, message)

async def request_input():
    command_request_event.set()
    await command_response_event.wait()

    output_message : Message = Output.command_output
    command_request_event.clear()
    command_response_event.clear()
    return   output_message
    
# interactive command example
@Commands.command("input-test", 1, show_usage=True)
async def input_test(client):
    message = Message(sender="Server", message="Please enter a number below", message_type=Message.CHAT, time=time.time())
    await send(client, message)
    output_message = await request_input()
    
    try:
        message = Message(sender="Server", message=f"You have entered the number : {int(output_message.message)}", message_type=Message.CHAT, time=time.time())
    except ValueError:
        message = Message(sender="Server", message=f"Must be ant int", message_type=Message.CHAT, time=time.time())
    await send(client, message, to_channel=True)

