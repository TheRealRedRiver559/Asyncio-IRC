from misc.database import cursor, conn
from misc.message import Message, MessageType, MessageSubType
from misc.storage import clients
from misc.client import Client
from misc.channel import hub_channel

async def login(client: Client, username: str, password: str) -> bool:
    cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
    user_record = cursor.fetchone()
    if user_record is None:
        await client.send_message(Message(sender="Server", message='Invalid username or password.', main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
        return False

    user_id, record_username, record_password = user_record
    client.id = user_id
    if username != record_username or password != record_password:
        await client.send_message(Message(sender="Server", message='Invalid username or password.', main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
        return False

    if username in clients.keys():  # User already logged in.
        await client.send_message(Message(sender="Server", message="User is already online.", main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
        return False

    return True

async def register(client: Client, username: str, password: str) -> bool: # TODO add a fallback for commititing to the DB. Also maybe add conn pools.
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?);", (username, password,))
        client.id = cursor.lastrowid
        cursor.execute("INSERT INTO UserChannelPermissions (user_id, channel_id, permission_level) VALUES (?, ?, ?);", (client.id, hub_channel.channel_id, 99,))
        conn.commit()
        return True

async def handle_authorization(client: Client, message: Message, username: str, password: str) -> bool:
    status: bool

    cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
    user_record = cursor.fetchone()
    
    if message.sub_type == MessageSubType.LOGIN:
        if user_record is None:
            await client.send_message(Message(sender="Server", message='Invalid username or password.', main_type=MessageType.ERROR, sub_type=MessageSubType.FAILED_LOGIN))
            return False
        status = await login(client, username, password)
    else:
        if user_record is not None:
            await client.send_message(Message(sender="Server", message='Username is already taken.', main_type=MessageType.ERROR, sub_type=MessageSubType.USERNAME_TAKEN))
            return False
        status = await register(client, username, password)
        
    return status