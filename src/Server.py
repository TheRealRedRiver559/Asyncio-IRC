import asyncio
import json
import socket

clients = []

async def broadcast(message):
    for client in clients:
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(client, message)

async def handle_client(client):
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            message = json.loads((await loop.sock_recv(client, 1024)).decode())
            
            if message['length'] > 200:
                message = json.dumps({'username':'Server', 'message':'Message too large'}).encode()
                await loop.sock_sendall(client, message)
            else:
                message = json.dumps({'username':message['username'], 'message':message['message']}).encode()
                await broadcast(message)
        except ConnectionResetError:
            client.close()
            clients.remove(client)
            return

async def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 9090))
    server.listen(5)
    server.setblocking(False)

    loop = asyncio.get_event_loop()
    while True:
        client, addr = await loop.sock_accept(server)
        clients.append(client)
        login_data = json.loads((await loop.sock_recv(client, 1024)).decode())
        print(login_data)
        print(addr)
        
        loop.create_task(handle_client(client))

asyncio.run(run_server())
