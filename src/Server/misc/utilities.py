from datetime import timedelta
from misc.database import cursor
from misc.storage import commands, prefix
from misc.message import Message, MessageType, MessageSubType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from misc.client import Client

async def format_time_left(time_left: timedelta):
    days, remainder = divmod(time_left.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 0:
        return f"{int(days)} days, {int(hours)} hours, and {int(minutes)} minutes remaining"
    elif hours > 0:
        return f"{int(hours)} hours and {int(minutes)} minutes remaining"
    else:
        return f"{int(minutes)} minutes and {int(seconds)} seconds remaining"
    
async def user_id_from_username(username: str) -> list:
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username, ))
    user_record = cursor.fetchone()
    return user_record

async def send_command_details(client: 'Client') -> None:
    cursor.execute(
        "SELECT permission_level FROM UserChannelPermissions WHERE user_id = ? AND channel_id = ?;",
        (
            client.id,
            client.current_channel.channel_id,
        ),
    )
    client_record = cursor.fetchone()
    client_permission_level = client_record[0]
    client_permission_level = 100 # TODO REMOVE THIS
    available_slash_commands = []
    for command_name, command_data in commands.items():
        if command_data[4]:
            command_perm_level = command_data[1]
            if command_perm_level <= client_permission_level:
                available_slash_commands.append(command_name)
    data = {"prefix": prefix, "slash_commands": available_slash_commands}
    await client.send_message(
        Message(
            sender="Server",
            message=data,
            main_type=MessageType.INFO,
            sub_type=MessageSubType.SLASH_COMMANDS,
        )
    )
