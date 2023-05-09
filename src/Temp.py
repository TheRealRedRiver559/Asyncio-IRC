import json

# temp solution to having 2 files needing access to the same data and
# functions, as per the name Temp.py

clients = dict()
banned_users = set()
channels = dict()

async def send_data(client, data): #Delimter = '\n' EOF marker
    if isinstance(data, dict):
        data = (json.dumps(data) + '\n')
    data = data.encode()
    client.writer.write(data)
    await client.writer.drain()


async def user_leave(client):  # Closes the connection server side, client is responsible for closing on their side
    client.connected = False
    client.task.cancel()
    if client.username is not None:
        del clients[client.username]
        channel = client.current_channel
        if channel is not None:
            channel.users.remove(client)
            client.current_channel = None
    if not client.writer.is_closing():
        client.writer.close()
        await client.writer.wait_closed()

class Channel:
    def __init__(self, name):
        """Channel classs for storing clients and the name of the channel
        There is no unique indentifiers. Only 1 name at the moment since there is no GUI yet. 
        Adding IDs with a CLI interface would be terrible. It would be like PED processes"""
        self.name = name
        self.clients = set()
