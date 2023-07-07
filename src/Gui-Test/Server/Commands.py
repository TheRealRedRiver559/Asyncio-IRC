import inspect
from Temp import (
    clients,
    send_data,
    banned_users,
    user_leave,
    channels,
    Channel,
    message_event,
)
import asyncio
import random
import string

# more commands.
# + ban
# + banned-users
# + users
# + user-count
# + much better and improved error handling, covers all cases (hopefully)


class Commands:
    prefix = "//"
    commands = {}
    killed_commands = set()

    def command(name: str, permission=1, public_output=False):
        def wrapper(command):
            Commands.commands[name] = [command, permission, public_output]
            return command

        return wrapper


async def help_text():
    text = f"""
    Commnads:
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


async def broadcast(
    data, sender="Server", message_type="public"
):  # broadcasts to all users
    """broadcasts the message to all users in a channel, or in the main user list if no channel is present"""
    if not isinstance(data, dict):
        data_format = {"sender": sender, "message": data, "message_type": message_type}
    else:
        data_format = data

    if not isinstance(sender, str):
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

    else:  # broadcasts to ALL
        for client in clients.values():
            await send_data(client, data_format)


async def update_command_history(client, message):
    if len(client.command_history) == 5:  # 5, is total log amount cap
        client.command_history.pop()
    client.command_history.append(" ".join(message))


async def check_command(client, data: str):
    try:
        """Checks if the command usage is valid and if it is an actual command"""
        message = data.removeprefix(
            Commands.prefix
        ).split()  # removes the command prefix from the message
        function_name = message[0]

        if function_name in Commands.commands:
            await update_command_history(client, message)

            if function_name in Commands.killed_commands:
                return f"Command: {function_name} is disabled."
            function = Commands.commands[function_name][0]
        else:
            return f"Command: {function_name}, not found"

        public_output = Commands.commands[function_name][2]
        if public_output:
            client.show_command = True
        else:
            client.show_command = False

        command_permission_level = Commands.commands[function_name][1]
        if client.permission_level < command_permission_level:
            return f"Missing access to this command."

        function_data = inspect.getfullargspec(function)
        args = function_data.args
        varargs = function_data.varargs

        pass_client = "client" in args
        if pass_client:
            args.remove("client")

        if len(message) > 1:
            parameters = message[1:]
        else:
            parameters = []

        if len(parameters) < len(args):
            missing_parameters = args[len(parameters) :]
            return f"Missing parameter(s): {', '.join(missing_parameters)}"

        if varargs or parameters:
            arg_parameters = parameters[: len(args)]
            varargs_parameters = parameters[len(args) :]
            if pass_client:
                output = await function(client, *arg_parameters, *varargs_parameters)
            else:
                output = await function(*arg_parameters, *varargs_parameters)
        else:
            if pass_client:
                output = await function(client)
            else:
                output = await function(*parameters)

        if public_output:
            await broadcast(data, sender=client)
            await broadcast(output)
        else:
            data_format = {
                "sender": client.username,
                "message": data,
                "message_type": "public",
            }
            await send_data(client, data_format)
            await send_data(client, output)

    except TypeError as e:
        return f"Invalid usage: {str(e)}"
    except Exception as e:
        return f"Error occurred: {str(e)}"


@Commands.command("broadcast", 2)
async def broadcast_command(client, *message):
    if len(message) > 0:
        message = " ".join(message)
    format = {"sender": "Server", "message": message, "message_type": "public"}
    for client in clients.values():
        await send_data(client, format)
    return format


@Commands.command("users", 1, public_output=True)
async def users_online():
    user_list = [x for x in clients.keys()]
    message = f"Users online: {user_list}"
    format = {"sender": "Server", "message": message, "message_type": "public"}
    return format
    # await send_data(client, format)


@Commands.command("channels", 1, public_output=True)
async def get_channels():
    channel_list = [x for x in channels.keys()]
    message = f"Channels: {channel_list}"
    format = {"sender": "Server", "message": message, "message_type": "public"}
    return format
    # await send_data(client, format)


@Commands.command("user-count", 5)
async def users_online():
    message = f"Number of users online: {len(clients)}"
    format = {"sender": "Server", "message": message, "message_type": "public"}
    return format
    # await send_data(client, format)


@Commands.command("banned-users", 5)
async def users_banned():
    # will be combined with users function eventually
    """Sends a list of all banned users"""
    banned_list = [x for x in banned_users]
    message = f"Banned Users: {banned_list}"
    format = {"sender": "Server", "message": message, "message_type": "public"}
    return format
    # await send_data(client, format)


@Commands.command("ban", 1)
async def ban_user(client, *data):
    format = {
        "sender": "Server",
        "message": "You have been banned!",
        "message_type": "private",
    }
    target_username = data[0]
    if target_username in clients:
        target_client = clients[target_username]
        data = data[1 : len(data)]
    elif target_username in banned_users:
        format["message"] = "User is already banned."
        await send_data(client, format)
        return
    else:
        format["message"] = "User not found."
        await send_data(client, format)
        return

    if len(data) >= 1:
        data = " ".join(data)
        format["message"] = f"You have been banned for: {data}"

    await send_data(target_client, format)

    banned_users.add(target_username)
    await user_leave(target_client)
    format["message"] = f"{target_username} has been banned."
    return format
    # await send_data(client, format)


@Commands.command("unban", 5)
async def unban_user(*data):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    target_username = data[0]
    if target_username in banned_users:
        banned_users.remove(target_username)
        format["message"] = f"{target_username} has been unbanned."
        # await send_data(client, format)
        return format
    elif target_username in clients:
        format["message"] = "User is not banned."
        # await send_data(client, format)
        return format
    else:
        format["message"] = "User not found."
        # await send_data(client, format)
        return format


@Commands.command("help", 1, public_output=True)
async def help():
    message = await help_text()
    format = {
        "sender": "Server",
        "message": f"Commands: {message}",
        "message_type": "private",
    }
    # await send_data(client, format)
    return format


@Commands.command("set-prefix", 5)
async def change_prefix(prefix):
    Commands.prefix = prefix
    format = {
        "sender": "Server",
        "message": f"Prefix has been changed to: {prefix}",
        "message_type": "private",
    }
    return format
    # await send_data(client, format)


@Commands.command("disable-command", 5)
async def turn_off_command(command_name):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    if command_name in Commands.commands:
        if command_name not in Commands.killed_commands:
            if command_name == "enable-command":
                format["message"] = f"The command {command_name} can not be disabled."
            else:
                Commands.killed_commands.add(command_name)
                format["message"] = f"{command_name} has been disabled."
        else:
            format["message"] = f"{command_name} is already disabled."
    else:
        format["message"] = f"{command_name} not found."

    # await send_data(client, format)
    return format


@Commands.command("enable-command", 5)
async def turn_on_command(command_name):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    if command_name in Commands.commands:
        if command_name in Commands.killed_commands:
            Commands.killed_commands.remove(command_name)
            format["message"] = f"{command_name} has been enabled."
        else:
            format["message"] = f"{command_name} is already enabled."
    else:
        format["message"] = f"{command_name} not found."

    return format
    # await send_data(client, format)


@Commands.command("join-channel", 5)
async def join_channel(client, channel_name):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    if channel_name in channels.keys():
        channel = channels[channel_name]
        if client in channel.clients:
            format["message"] = f"You are already in this channel."
        else:
            await send_data(
                client,
                {
                    "sender": "Server",
                    "message": channel_name,
                    "message_type": "CHANNEL_CHANGE",
                },
            )
            format["message"] = f"You have joined the channel named, {channel_name}."
            client.current_channel = channel
            channel.clients.add(client)
    else:
        format["message"] = f"The channel {channel_name}, does not exist."

    return format
    # await send_data(client, format)


@Commands.command("leave-channel", 5)
async def leave_channel(client):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    if client.current_channel is not None:
        channel = client.current_channel
        channel.clients.remove(client)
        client.current_channel = None
        format["message"] = f"You have left the channel."
    else:
        format["message"] = f"You are not in a channel."

    await send_data(
        client, {"sender": "Server", "message": None, "message_type": "CHANNEL_CHANGE"}
    )
    return format
    # await send_data(client, format)


@Commands.command("create-channel", 5)
async def create_channel(channel_name):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    if channel_name in channels.keys():
        format["message"] = f"The channel {channel_name}, already exists."
    else:
        channel = Channel(channel_name)
        channels[channel_name] = channel
        format["message"] = f"The channel {channel_name}, has been created."

    return format
    # await send_data(client, format)


@Commands.command("delete-channel", 5)
async def delete_channel(client, channel_name):
    format = {"sender": "Server", "message": "", "message_type": "private"}
    if channel_name in channels.keys():
        channel = channels[channel_name]
        for client in channel.clients:  # removes all users
            client.current_channel = None
        del channels[channel_name]
        format["message"] = f"The channel {channel_name} has been deleted."
    else:
        format["message"] = f"The channel {channel_name} does not exist."

    await send_data(client, format)


@Commands.command("set-perm", 1)
async def change_channel_perm(*data):
    format = {"sender": "Server", "message": "", "message_type": "public"}

    target_username = data[0]
    permission_level = data[1]
    try:
        permission_level = int(permission_level)
    except Exception as e:
        print(e)
        format["message"] = "Permission must be an integer."
        # await send_data(client, format)
        return format

    if target_username in clients:
        target_client = clients[target_username]
        data = data[1 : len(data)]
    elif target_username in banned_users:
        format["message"] = "User is banned."
        # await send_data(client, format)
        return format
    else:
        format["message"] = "User not found."
        # await send_data(client, format)
        return format

    if len(data) >= 1:
        data = " ".join(data)
        format["message"] = f"Your permission are set to: {permission_level}"
        target_client.permission_level = permission_level

    await send_data(target_client, format)

    format[
        "message"
    ] = f"{target_username} has had their permissions set to {permission_level}."
    return format
    # await send_data(client, format)


@Commands.command("command-history", 5)
async def show_client_command_history(client):
    # will be combined with users function eventually
    """Sends a list of all banned users"""
    command_list = client.command_history
    message = f"Command History: {command_list}"
    format = {"sender": "Server", "message": message, "message_type": "public"}

    return format


# WIP broken command
@Commands.command("input-test", 1, public_output=True)
async def input_test(client):
    format_1 = {
        "sender": "Server",
        "message": "Please enter a number below",
        "message_type": "public",
    }

    while True:
        data = await client.receive_data()
        if client.show_command:
            await broadcast(format_1)
        else:
            send_data(client, format_1)

        if data["message_type"] == "ACK":
            client.pong_received = True
            await client.keep_alive(data)
            continue

        message = data["message"]

        format_1[
            "message"
        ] = f"You have entered the number : {int(message)}"  # no error handleing because testing
        return format_1
