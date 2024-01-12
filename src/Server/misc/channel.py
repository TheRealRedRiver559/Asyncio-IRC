import hashlib
import datetime
from misc.database import cursor, conn
from misc.message import Message, MessageType, MessageSubType
from misc.storage import channels, clients
from misc.utilities import format_time_left, send_command_details
from misc.client import Client

class Channel:
    def __init__(self, name: str, private_channel: bool = False, channel_password: str|None = None, channel_id: int|None = None, is_visible: bool = True) -> None:
        self.name = name
        self.private_channel = private_channel
        self.channel_password = channel_password
        self.channel_id = channel_id
        self.is_visible = is_visible
        self.channel_clients = set()

        if self.channel_id is None: # channels created from commands do not have DB ids
            cursor.execute("INSERT INTO channels (channel_name, password, is_private, is_visible) VALUES (?, ?, ?, ?);", 
            (self.name, self.channel_password, self.private_channel,self.is_visible,))
            conn.commit()
            self.channel_id = cursor.lastrowid
        channels[self.name] = self
    
    async def broadcast(self, message:Message) -> None:
        client:Client
        for client in self.channel_clients:
            await client.send_message(message)
        
    @staticmethod
    async def update_channels(client: Client|None = None) -> None:
        async def send_channel_list(client: Client) -> None:
            cursor.execute("""
                SELECT channel_name 
                FROM channels 
                WHERE is_visible = 1;
            """)
            visible_channels_records = cursor.fetchall()
            visible_channels = [channel[0] for channel in visible_channels_records]
            # Retrieve all non-visible channels this user has permission to access
            cursor.execute("""
                SELECT c.channel_name 
                FROM channels c
                JOIN UserChannelPermissions ucp ON c.channel_id = ucp.channel_id 
                WHERE ucp.user_id = ? AND c.is_visible = 0;
            """, (client.id,))
            non_visible_channels_records = cursor.fetchall()
            non_visible_channels = [channel[0] for channel in non_visible_channels_records]

            # Merge the lists
            all_channels = list(set(visible_channels + non_visible_channels))

            message = Message(sender="Server", message=all_channels, main_type=MessageType.INFO, sub_type=MessageSubType.CHANNEL_LIST)
            await client.send_message(message)

        if client is not None:
            await send_channel_list(client)
        else:
            for client in clients.values():
                await send_channel_list(client)

    

    async def update_channel_users(self) -> None:
        usernames = [client.username for client in self.channel_clients]
        message = Message(sender="Server", message=usernames, main_type=MessageType.INFO, sub_type=MessageSubType.USER_LIST)
        client: Client
        for client in self.channel_clients:
            await client.send_message(message)
            await send_command_details(client)

    async def join_channel(self, client: Client) -> None:
        client_channel = client.current_channel
        if client_channel is not None:
            await client_channel._remove_user(client)
        await self._add_user(client)

    async def leave_channel(self, client: Client) -> None:
        await self._remove_user(client)
        await hub_channel._add_user(client)
    
    async def _add_user(self, *new_clients: tuple):
        message = Message(sender="Server", message=self.name, main_type=MessageType.STATUS ,sub_type=MessageSubType.CHANNEL_JOIN)
        conn_changes = False

        client: Client
        for client in new_clients:
            if client in self.channel_clients:
                continue
            self.channel_clients.add(client)
            cursor.execute("SELECT user_id FROM UserChannelPermissions WHERE channel_id = ? AND user_id = ?;", (self.channel_id,client.id,))
            channel_record = cursor.fetchone()
            if not channel_record:
                cursor.execute("INSERT INTO UserChannelPermissions (user_id, channel_id, permission_level) VALUES (?, ?, ?);", (client.id, self.channel_id, 1,))
                conn_changes = True
            client.current_channel = self
            await client.send_message(message)
        if conn_changes:
            conn.commit()
        await self.update_channel_users()

    async def _remove_user(self, *clients_to_remove: tuple) -> None:
        message = Message(sender="Server", message=hub_channel.name, main_type=MessageType.STATUS, sub_type=MessageSubType.CHANNEL_LEAVE)
        client: Client
        for client in clients_to_remove:
            if client in self.channel_clients:
                self.channel_clients.remove(client)
                await client.send_message(message)
        await self.update_channel_users()

    async def delete_channel(self) -> None:
        await hub_channel._add_user(self.channel_clients)
        self.channel_clients.clear()
        del channels[self.name]
        await self.update_channels()

    async def check_ban(self, client: Client):
        cursor.execute("SELECT * FROM BannedUsersChannel WHERE user_id = ? AND channel_id = ?;", (client.id, self.channel_id,))
        ban_record = cursor.fetchone()

        if ban_record:
            ban_timestamp = datetime.strptime(ban_record[3], '%Y-%m-%d %H:%M:%S')
            ban_duration = datetime.timedelta(days=ban_record[4])
            ban_end_time = ban_timestamp + ban_duration
            current_time = datetime.now()
            time_left = ban_end_time - current_time

            if time_left.total_seconds() > 0:
                # Ban is active
                time_left_format = await format_time_left(time_left)
                ban_reason = ban_record[5]
                return {"banned": True, "reason": ban_reason, "time_left": time_left_format}
            else:
                # Ban has expired, delete the record
                cursor.execute("DELETE FROM BannedUsersChannel WHERE ban_id = ?;", (ban_record[0],))
                conn.commit()
                return {"banned": False}

        return {"banned": False}

def generate_private_channel_tag(user_ids: list) -> str:
    sorted_ids = sorted(user_ids)
    combined = '_'.join(map(str, sorted_ids))  # Example: '12_34' for user IDs 12 and 34
    # hash the combined string
    channel_name = hashlib.sha256(combined.encode()).hexdigest()
    return channel_name

async def check_private_channel(user_ids: list) -> list|None:
    sorted_ids = sorted(user_ids)
    combined = '_'.join(map(str, sorted_ids))
    channel_name = hashlib.sha256(combined.encode()).hexdigest()
    cursor.execute("SELECT channel_name FROM channels WHERE channel_name = ?", (channel_name,))
    record = cursor.fetchone()
    return record[0] if record else None

class PrivateMessageChannel(Channel):
    def __init__(self, client_ids: list, name: str|None = None, private_channel: bool = True, channel_password: str = None, channel_id: int = None, is_visible:bool = False) -> None:
        if channel_id is None:
            name = generate_private_channel_tag(client_ids)
        super().__init__(name, private_channel, channel_password, channel_id, is_visible)
        if channel_id is None:
            client_id: int
            for client_id in client_ids:
                cursor.execute("INSERT INTO UserChannelPermissions (user_id, channel_id, permission_level) VALUES (?, ?, ?);", (client_id, self.channel_id, 1))
            conn.commit()

    async def _add_user(self, *new_clients: tuple) -> None:
        message = Message(sender="Server", message=self.name, main_type=MessageType.STATUS, sub_type=MessageSubType.CHANNEL_JOIN)
        conn_changes = False
        
        client: Client
        for client in new_clients:
            if client in self.channel_clients:
                continue
            self.channel_clients.add(client)
            cursor.execute("SELECT user_id FROM UserChannelPermissions WHERE channel_id = ? AND user_id = ?;", (self.channel_id, client.id))
            channel_record = cursor.fetchone()
            if not channel_record:
                cursor.execute("INSERT INTO UserChannelPermissions (user_id, channel_id, permission_level) VALUES (?, ?, ?);", (client.id, self.channel_id, 1))
                conn_changes = True
            client.current_channel = self
            await client.send_message(message)
        if conn_changes:
            client_ids = [client.id for client in self.channel_clients]
            new_name = generate_private_channel_tag(*client_ids)

            cursor.execute("UPDATE channels SET channel_name = ? WHERE channel_id = ?;", (new_name, self.channel_id))
            conn.commit()

        await self.update_channel_users()


def create_channels() -> None:
    cursor.execute("SELECT * FROM channels")
    record_channels = cursor.fetchall()
    if not record_channels:
        # saves / updates in class, no need to do it here.
        Channel('Hub') # hub channel for joining users and a place to go when you are kicked or banned from a channel. 
        Channel('Main') # general channel for messaging. 
    else:
        for channel in record_channels:
            channel_id, channel_name, channel_password, private_channel, is_visible = channel[0], channel[1], channel[2], channel[3], channel[4]

            is_visible = channel[4]
            if is_visible == 0:
                is_visible = False
                cursor.execute("SELECT user_id FROM UserChannelPermissions WHERE channel_id = ?", (channel_id,))
                user_ids = [user[0] for user in cursor.fetchall()]
                PrivateMessageChannel(user_ids ,channel_name, private_channel, channel_password, channel_id, is_visible)
            elif is_visible == 1:
                is_visible = True
                Channel(channel_name, private_channel, channel_password, channel_id, is_visible)

create_channels()
hub_channel: Channel = channels["Hub"]
main_channel: Channel = channels['Main']