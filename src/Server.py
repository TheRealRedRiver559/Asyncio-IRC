import asyncio
import socket

clients = []
async def broadcast(message):
    for client in clients:
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(client, message.encode())

async def handle_client(client):
    loop = asyncio.get_event_loop()
    while True:
        try:
            message = (await loop.sock_recv(client, 1024)).decode()
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
        client, adr = await loop.sock_accept(server)
        clients.append(client)
        loop.create_task(handle_client(client))

asyncio.run(run_server())
