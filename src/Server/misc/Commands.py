import inspect
import typing

from misc.client import Client
from misc.utilities import user_id_from_username, send_command_details
from misc.storage import clients, banned_users, channels, reload_event, commands, killed_commands, prefix
from misc.database import conn, cursor
from misc.channel import (
    Channel,
    PrivateMessageChannel,
    main_channel,
    hub_channel,
    check_private_channel,
)
from misc.event import Event
from misc.message import Message, MessageType, MessageSubType


class Commands:

    def command(
        name: str,
        permission=1,
        show_usage=True,
        slash_command=True,
        description="No description available.",
    ) -> typing.Awaitable:
        def wrapper(command: typing.Awaitable) -> typing.Awaitable:
            commands[name] = [
                command,
                permission,
                show_usage,
                description,
                slash_command,
            ]
            return command

        return wrapper

async def update_command_history(client, command_message: str):
    try:
        if len(client.command_history) == 5:  # 5, is total log amount cap
            client.command_history.pop()
        client.command_history.append(" ".join(command_message))
    except Exception as e:
        print(e)


async def help_text(client: Client) -> str:
    description_text = "--Commands--\n"
    cursor.execute(
        "SELECT permission_level FROM UserChannelPermissions WHERE user_id = ? AND channel_id = ?;",
        (
            client.id,
            client.current_channel.channel_id,
        ),
    )
    client_record = cursor.fetchone()
    client_permission_level = client_record[0]
    available_command_names = list(
        filter(
            lambda command_name: int(commands[command_name][1])
            <= int(client_permission_level),
            commands,
        )
    )
    for command_name in available_command_names:
        command_description = commands[command_name][3]
        command_level = commands[command_name][1]
        description_text += f"{prefix}{command_name}:(Lvl:{command_level}) -- {command_description}\n"

    return description_text


async def perm_change_send(
    channel: Channel, before_perm_level: int, after_perm_level: int
) -> None:
    lower_bound, upper_bound = sorted([before_perm_level, after_perm_level])
    cursor.execute(
        "SELECT user_id from UserChannelPermissions WHERE channel_id = ? AND permission_level BETWEEN ? AND ?",
        (channel.channel_id, lower_bound, upper_bound),
    )

    affected_user_ids = [row[0] for row in cursor.fetchall()]
    affected_clients = [c for c in clients.values() if c.id in affected_user_ids]
    for affected_client in affected_clients:
        await send_command_details(affected_client)


async def server_broadcast(message: Message) -> None:
    channel: Channel
    for channel in channels:
        await channel.broadcast(message)


async def execute_command(message: Message) -> None:
    message_data = message.message
    client: Client = clients[message.sender]
    command_data = message_data.removeprefix(prefix).split()
    function_name = command_data[0]
    command_data = command_data[1:]

    valid_command = commands.get(function_name, False)

    await client.send_message(message)
    if not valid_command:
        message = Message(
            sender="Server",
            message=f"{function_name}, is not a command.",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.INVALID_COMMAND,
        )
        await client.send_message(
            message
        )  # can replace with current_channel.broadcast for public error displaying
        return

    command_permission_level = commands[function_name][1]
    show_command_usage = commands[function_name][2]
    if client.current_channel == hub_channel:
        show_command_usage = False
    if show_command_usage:
        send = client.current_channel.broadcast
    else:
        send = client.send_message

    cursor.execute(
        "SELECT permission_level FROM UserChannelPermissions WHERE user_id = ? AND channel_id = ?;",
        (
            client.id,
            client.current_channel.channel_id,
        ),
    )
    client_record = cursor.fetchone()
    client_permission_level = client_record[0]

    if client_permission_level < command_permission_level:
        message = Message(
            sender="Server",
            message=f"You do not have access to this command.",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.INVALID_ACCESS,
        )
        await send(message)
        return

    if function_name in killed_commands:
        message = Message(
            sender="Server",
            message=f"Command: {function_name} is disabled.",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.DISABLED,
        )
        await send(message)
        return

    await update_command_history(
        client, command_data
    )  # TODO update this to use the DB.

    function = commands[function_name][0]
    func_data = inspect.getfullargspec(function)

    func_args = func_data.args
    func_defaults = list(func_data.defaults or [])
    func_kwonlydefaults = func_data.kwonlydefaults or {}
    func_varargs = func_data.varargs

    args = []
    kwargs = {}

    if "client" in func_args:
        args.append(client)
        func_args.remove("client")

    for i, arg in enumerate(func_args):
        if i < len(command_data):
            args.append(command_data[i])
        elif func_defaults:
            args.append(func_defaults.pop(0))
        else:
            message = Message(
                sender="Server",
                message=f"Missing parameter: {arg}",
                main_type=MessageType.CHAT,
                sub_type=MessageSubType.COMMAND_ERROR,
            )
            await send(message)
            return

    if func_varargs:
        args.extend(command_data[len(func_args) :])

    for kwarg in func_data.kwonlyargs:
        kwarg_value = next(
            (
                item.split("=")[1]
                for item in command_data
                if item.startswith(f"--{kwarg}=")
            ),
            func_kwonlydefaults.get(kwarg),
        )
        if kwarg_value is not None:
            kwargs[kwarg] = kwarg_value
    try:
        await function(*args, **kwargs)
    except Exception as e:
        print("Command Error:" + str(e))


@Commands.command(
    "test",
    permission=1,
    show_usage=True,
    slash_command=True,
    description="Test message.",
)
async def test(client: Client, x=10) -> None:
    text = f"This is a test command {x}"
    message = Message(
        sender="Server",
        message=text,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)


@Commands.command(
    "broadcast",
    4,
    show_usage=False,
    description="Broadcasts a message to users in the channel.",
)
async def channel_broadcast_command(client: Client, *message: str) -> None:
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)


@Commands.command(
    "server-broadcast",
    5,
    show_usage=False,
    description="Broadcasts a message to all users in the server.",
)
async def server_broadcast_command(*message) -> None:
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await server_broadcast(message)


# TODO (1) set hard cap for informational commands so a massive stream of data isnt being sent over the network in special cases.
# V.1
@Commands.command(
    "users", 1, show_usage=False, description="Shows a list of all online users."
)
async def users_online(client: Client) -> None:
    channel = client.current_channel
    channel_client_usernames = [client.username for client in channel.channel_clients]

    message_data = f"Users online: {channel_client_usernames}"
    message = Message(
        sender="Server",
        message=message_data,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)


@Commands.command(
    "channels",
    1,
    show_usage=True,
    slash_command=True,
    description="Shows a list of all available channels.",
)
async def get_channels(
    client: Client,
) -> None:  # will ONLY grab the visible channels for the user who uses the command.
    # if a user with higher permissions uses this command the lower users may see channels that they were unaware of in the list.
    cursor.execute("SELECT channel_name FROM channels WHERE is_visible = ?", (True,))
    visible_channels = [channel_name[0] for channel_name in cursor.fetchall()]
    message_data = f"Channels: {visible_channels}"
    message = Message(
        sender="Server",
        message=message_data,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)



@Commands.command(
    "user-count",
    1,
    show_usage=True,
    slash_command=True,
    description="Displayes the amount of server-wide users currently online.",
)
async def users_online(client: Client) -> None:
    message = f"Number of users online: {len(clients)}"
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)


@Commands.command(
    "banned-users",
    4,
    show_usage=False,
    description="Shows a list of all banned members.",
)
async def users_banned(client: Client) -> None:
    channel_id = client.current_channel.channel_id
    cursor.execute(
        "SELECT user_id FROM BannedUsersChannel WHERE channel_id = ?", (channel_id,)
    )
    banned_users = [user[0] for user in cursor.fetchall()]
    message = f"Banned Users: {banned_users}"
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)

@Commands.command("ban", 5, show_usage=True, description="Bans the specified username.")
async def ban_user(client: Client, target_username: str, reason="No reason given.") -> None:
    target_record = await user_id_from_username(target_username)
    target_record = cursor.fetchone()
    if not target_record:
        message = f"User not found."
        message = Message(
            sender="Server",
            message=message,
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
        await client.send_message(message)
        return

    target_user_id:int = target_record[0]
    target_client:Client = clients[target_username]
    channel = client.current_channel
    channel_id = channel.channel_id
    ban_record = await channel.check_ban(target_client)

    if ban_record["banned"]:
        message = "User is already banned."
        message = Message(
            sender="Server",
            message=message,
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
        await client.send_message(message)
        return
    else:
        cursor.execute(
            "INSERT INTO BannedUsersChannel (user_id, channel_id, ban_duration, ban_reason) VALUES (?, ?, ?, ?);",
            (
                target_user_id,
                channel_id,
                1,
                reason,
            ),
        )
        conn.commit()
        if target_client.current_channel == channel:
            await target_client.leave_channel()

    message = f"You have been banned for : {reason}"
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.STATUS,
        sub_type=MessageSubType.BANNED,
    )
    await client.send_message(message)
    message = f"{target_username} has been banned for Reason: {reason}."
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await channel.broadcast(message)

@Commands.command("unban", 5, description="Unbans the specified user from the channel.")
async def unban_user(client: Client, target_username: str) -> dict:
    message = Message(
        sender="Server",
        message="",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    channel_id = client.current_channel.channel_id
    target_record = await user_id_from_username(target_username)
    target_record = cursor.fetchone()

    if not target_record:
        message.message = "User not found."
        await client.send_message(message)
        return

    target_id = target_record[0]
    cursor.execute(
        "SELECT user_id from BannedUsersChannel WHERE channel_id = ? AND user_id = ?",
        (
            channel_id,
            target_id,
        ),
    )
    banned_record = cursor.fetchone()

    if banned_record:
        cursor.execute(
            "DELETE FROM BannedUsersChannel WHERE user_id = ? AND channel_id = ?;",
            (
                target_id,
                channel_id,
            ),
        )
        conn.commit()
        message.message = f"{target_username} has been unbanned."
    else:
        message.message = "User is not banned."

    await client.send_message(message)

@Commands.command(
    "help",
    1,
    show_usage=True,
    description="Displayes a helpful list of commnads you can use.",
)
async def help(client: Client) -> None:
    message = await help_text(client)
    message = Message(
        sender="Server",
        message=message,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    channel = client.current_channel
    await channel.broadcast(message)


@Commands.command(
    "set-prefix",
    10,
    show_usage=False,
    description="Changes the current command prefix (server-wide).",
)
async def change_prefix(client: Client, prefix: str) -> None:
    prefix = prefix
    message_data = f"Prefix has been changed to: {prefix}"
    message = Message(
        sender="Server",
        message=prefix,
        main_type=MessageType.INFO,
        sub_type=MessageSubType.PREFIX_CHANGE,
    )
    await client.send_message(message)
    message = Message(
        sender="Server",
        message=message_data,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)

# TODO re-add disable, and enable command

@Commands.command(
    "join-channel", 1, show_usage=False, description="Joins the specified channel."
)
async def join_channel(client: Client, channel_name: str, password: str|None = None) -> None:
    # Check if the channel exists
    if channel_name in channels:
        channel: Channel = channels[channel_name]

        # Check for password protection
        if channel.channel_password and channel.channel_password != password:
            message_text = (
                "Incorrect Password."
                if password is not None
                else "This channel is password protected."
            )
            message = Message(
                sender="Server",
                message=message_text,
                main_type=MessageType.CHAT,
                sub_type=MessageSubType.COMMAND_RESPONSE,
            )
            await client.send_message(message)
            return

        # Check for ban status
        ban_data = await channel.check_ban(client)
        if ban_data["banned"]:
            ban_message = Message(
                sender="Server",
                message="You are banned from this channel!",
                main_type=MessageType.CHAT,
                sub_type=MessageSubType.COMMAND_RESPONSE,
            )
            await client.send_message(ban_message)
            ban_detail_message = Message(
                sender="Server",
                message={
                    "reason": ban_data["reason"],
                    "time_left": ban_data["time_left"],
                },
                main_type=MessageType.STATUS,
                sub_type=MessageSubType.BANNED,
            )
            await client.send_message(ban_detail_message)
            return

        # Join the channel
        await channel.join_channel(client)
        message = Message(
            sender="Server",
            message=f"You have joined {channel.name} channel.",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
        await client.send_message(message)
    else:
        # Channel does not exist
        message = Message(
            sender="Server",
            message=f"The channel {channel_name}, does not exist.",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
        await client.send_message(message)

@Commands.command(
    "leave-channel", 1, description="Leaves the current channel you are in."
)
async def leave_channel(client: Client) -> None:
    message = Message(
        sender="Server",
        message="",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    if client.current_channel.name != hub_channel.name:
        channel: Channel = client.current_channel
        await hub_channel.join_channel(client)
        message.message = f"You have left the {channel.name} channel."
    else:
        message.message = f"You cannot leave this channel."

    await client.send_message(message)

@Commands.command("create-channel", 1, description="Creates a new channel.")
async def create_channel(client: Client, channel_name: str, password: str|None = None) -> None:
    message = Message(
        sender="Server",
        message="",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    cursor.execute(
        "SELECT channel_name FROM channels WHERE channel_name = ?;", (channel_name,)
    )
    channel_available = cursor.fetchone()

    if channel_available:
        message.message = f"The channel {channel_name}, already exists."
        await client.send_message(message)
        return

    channel = Channel(channel_name, channel_password=password)

    channels[channel_name] = channel
    cursor.execute(
        "INSERT INTO UserChannelPermissions (user_id, channel_id, permission_level) VALUES (?, ?, ?);",
        (
            client.id,
            channel.channel_id,
            5,
        ),
    )
    await channel.update_channels()
    message.message = f"The channel {channel_name}, has been created."
    await client.send_message(message)

@Commands.command(
    "delete-channel", 1, description="Deletes the specified channel name."
)
async def delete_channel(client: Client, channel_name: str) -> None:
    message = Message(
        sender="Server",
        message=f"The channel {channel_name} has been deleted.",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    cursor.execute(
        "SELECT channel_id FROM channels WHERE channel_name = ?", (channel_name,)
    )
    channel_record = cursor.fetchone()

    if channel_record and channel not in (hub_channel, main_channel):
        channel_id = channel_record[0]
        cursor.execute("DELETE FROM channels WHERE channel_id = ?;", (channel_id,))
        channel: Channel = channels[channel_name]
        await channel.delete_channel()
        conn.commit()
    else:
        message.message = f"The channel {channel_name} does not exist."

    await client.send_message(message)


@Commands.command(
    "set-user-perm",
    5,
    description="Changes the permission of the specified user in the channel.",
)
async def change_user_perm(client: Client, target_username: str, permission_level: int) -> None:
    message = Message(
        sender="Server",
        message=None,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    try:
        permission_level = int(permission_level)
    except Exception as e:
        message.message = "Permission must be an integer."
        await client.send_message(message)
        return

    if target_username in clients:
        target_client: Client = clients[target_username]

    elif target_username in banned_users:
        message.message = "User is banned."
        await client.send_message(message)
        return
    else:
        message.message = "User not found."
        await client.send_message(message)
        return

    message.message = f"Permissions for {target_username}, have been changed to Lvl: {permission_level}."
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (target_username,))
    user_id = cursor.fetchone()[0]
    channel_id = client.current_channel.channel_id

    cursor.execute(
        "UPDATE UserChannelPermissions SET permission_level = ? WHERE channel_id = ? AND user_id = ?;",
        (
            permission_level,
            channel_id,
            user_id,
        ),
    )
    conn.commit()
    await send_command_details(target_client)

    await client.send_message(message)


# TODO add a structure for each channel to have a command or role table of somesort.
# maybe something like a single table with channel_ids, command_ids, and the permissions level so its a single table.
"""
@Commands.command(
    "perm", 1, show_usage=False, description="Shows your permission level."
)
async def show_perms(client: Client) -> None:
    message = Message(
        sender="Server",
        message=None,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    cursor.execute(
        "SELECT permission_level FROM UserchannelPermission WHERE user_id = ? AND channel_id = ?;",
        (
            client.id,
            client.current_channel.id,
        ),
    )
    permission_level = cursor.fetchall()[0]
    message.message = f"Permission Level: {permission_level}"
    await client.send_message(message)
"""

@Commands.command(
    "command-history",
    1,
    show_usage=False,
    description="Lists your prevously used commands and inputs.",
)
async def show_client_command_history(client: Client) -> None:
    command_list = client.command_history
    message_data = f"Command History: {command_list}"
    message = Message(
        sender="Server",
        message=message_data,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)

@Commands.command(
    "input-test", 3, show_usage=True, description="Enter a number for testing."
)
async def input_test(client: Client) -> None:
    message = Message(
        sender="Server",
        message="Please enter a number below",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    channel = client.current_channel
    await channel.broadcast(message)
    event = Event("user", client.id)
    message_output = await event.request()
    await channel.broadcast(message_output)

    try:
        message = Message(
            sender="Server",
            message=f"You have entered the number : {int(message_output.message)}",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
    except ValueError:
        message = Message(
            sender="Server",
            message=f"Must be ant int",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
    await channel.broadcast(message)

@Commands.command(
    "input-test2", 4, show_usage=True, description="Enter an animal name for testing."
)
async def input_test2(client: Client) -> None:
    message = Message(
        sender="Server",
        message="Please enter a animal below",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await server_broadcast(message)
    event = Event("server", None)
    message_output = await event.request()
    await server_broadcast(message_output)

    message = Message(
        sender="Server",
        message=f"{message_output.sender} has entered the name : {message_output.message}",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await server_broadcast(message)


# V.1
@Commands.command(
    "input-test3", 2, show_usage=True, description="Enter a name for testing."
)
async def input_test3(client: Client) -> None:
    message = Message(
        sender="Server",
        message="Please enter a name below",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    channel = client.current_channel
    await channel.broadcast(message)
    event = Event("channel", context_id=client.current_channel.id)
    message_output = await event.request()
    await channel.broadcast(message_output)  # Send to channel

    message = Message(
        sender="Server",
        message=f"{message_output.sender} has entered the name : {message_output.message}",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await channel.broadcast(message)

# TODO make this actually work
"""
@Commands.command(
    "reload-commands",
    permission=10,
    show_usage=True,
    description="Reloads all commands to be updated from a save file.",
)
async def reload_commands(client: Client) -> None:
    reload_event.set()
    await send_command_details(client)
    message = Message(
        sender="Server",
        message="Commands have been reloaded",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)
"""

@Commands.command(
    "clear",
    permission=5,
    show_usage=True,
    description="Clears a specified amount of messages (defualt=100).",
)
async def clear_channel_messages(client: Client, amount=100) -> None:
    try:
        amount = int(amount)
    except TypeError:
        message = Message(
            sender="Server",
            message="Amount must be an integer.",
            main_type=MessageType.ERROR,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
        await client.send_message(message)
        return

    if 1 <= amount <= 10_000:  # 10k hardcap
        message = Message(
            sender="Server",
            message=amount,
            main_type=MessageType.COMMAND,
            sub_type=MessageSubType.CLEAR,
        )
        await client.send_message(message)
    else:
        amount = 10_000
        message = Message(
            sender="Server",
            message=amount,
            main_type=MessageType.COMMAND,
            sub_type=MessageSubType.CLEAR,
        )
        await client.send_message(message)

    message = Message(
        sender="Server",
        message=f"{amount} message(s) have been cleared.",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)

@Commands.command(
    "private-message",
    permission=1,
    show_usage=True,
    description="Messages a user in private.",
)
async def private_message(client: Client, target_username: str, message_content: str) -> None:
    target_record = await user_id_from_username(
        target_username
    )  # checks if users exists
    if not target_record:
        message = Message(
            sender="Server",
            message="User not found.",
            main_type=MessageType.CHAT,
            sub_type=MessageSubType.COMMAND_RESPONSE,
        )
        await client.send_message(message)
        return
    target_id = target_record[0]

    private_channel_name = await check_private_channel(
        [target_id, client.id]
    )  # returns the private channel name
    if private_channel_name is not None:  # checks if the channel has been created.
        private_channel = channels[private_channel_name]
    else:
        private_channel = PrivateMessageChannel([target_id, client.id])

    # Update channels for the clients
    if target_username in clients:
        target_client = clients[target_username]
        # await Channel.update_channels(target=[target_client, client])
    else:
        pass
        # await Channel.update_channels(target=client)
    # Send the message in the private channel
    await client.join_channel(client)
    message = Message(
        sender=client.username,
        message=message_content,
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.GENERAL,
    )
    await private_channel.broadcast(message)

@Commands.command(
    "ping",
    permission=1,
    show_usage=True,
    description="Pings the server.",
)
async def ping(client: Client) -> None:
    message = Message(
        sender="Server",
        message="Pong!",
        main_type=MessageType.CHAT,
        sub_type=MessageSubType.COMMAND_RESPONSE,
    )
    await client.send_message(message)
