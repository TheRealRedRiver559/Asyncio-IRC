import datetime
import asyncio
import aioconsole
import json
import os
os.system('color')

host, port = ('localhost', 9090)

class color:
    BLUE = '\033[94m'
    GREY = '\033[90m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Client():
    """Client class for handling information about the host, port, username, and if it is connected"""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.username = None
        self.writer = None
        self.reader = None
        self.connected = False
        self.logged_in = False

    async def leave(self):
        self.connected = False
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

    #trys to connect to server until succesful
    async def connect(self):

        """Attempts to connect to the server / host until it is accepted. Using connect_ex to prevent exceptions"""
        while self.connected == False:
            print(f'Connecting to (HOST: {self.host}) (PORT: {self.port})...')
            try:
                self.reader, self.writer = await asyncio.open_connection(host, port)
                print(f"Connected to {self.writer.get_extra_info('peername')}\n")
                self.connected = True
            except ConnectionRefusedError:
                continue
        
    async def login(self):
        """Takes in the users login and saves the username, the password is just input and is not stored anywhere"""
        while self.logged_in == False:
            data = await self.receive_data()

            if data['message_type']  in ('REQUEST', 'INFO'):

                if data['message'] == 'LOGIN':
                    self.username = input('Username: ')
                    password = input('Password: ')
                    data = (json.dumps({'username':self.username, 'password':password})+'\n').encode()
                    self.writer.write(data)
                    await self.writer.drain()

                    print("Awaiting Confirmation...")

                elif data['message'] == 'PERMIT':
                    
                    self.logged_in = True
                    return
                elif data['message'] == 'DENY':
                    message = self.format_message(data)
                    print(message)
                
                continue
            else:
                continue

    
    @staticmethod
    async def get_time():
        """Gets the users current time and returns a time object"""
        time = datetime.datetime.now()
        return (time.strftime("%m/%d/%Y %#I:%M %p"))
    
    async def send_message(self, message):
        data = (json.dumps({'message':message})+'\n').encode()
        self.writer.write(data)
        await self.writer.drain()

    async def format_message(self, message_data):

        sender = message_data['sender']
        message = message_data['message']
        if sender == self.username: #Blue for your username
            return(f"{color.BLUE}{self.username}{color.GREY} : {color.END}{message} {color.GREY}{await self.get_time()}{color.END}")
        elif sender == 'Server':
            return(f"{color.YELLOW}{sender}{color.GREY} : {color.END}{message} {color.GREY}{await self.get_time()}{color.END}")
        else:
            return(f"{color.RED}{sender}{color.GREY} : {color.END}{message} {color.GREY}{await self.get_time()}{color.END}")

    async def receive_data(self):
        data = (await self.reader.readuntil(b'\n')).decode()
        data = json.loads(data)
        return data

    async def client_handler(self):
        """Recieves messages from the server and checks the message data for usernames. Basic coloring for other names and the server messages"""
        while self.logged_in:
            data = await self.receive_data()

            message = await self.format_message(data)
            print(message)

    async def receive_input(self):
        """Sends the message to the server / host machine."""
        while self.logged_in:
            message = (await aioconsole.ainput())
            #if message == 'spam':
                #message = ('spam'*17001)
            #message = 'spam'
            if len(message) > 200: #change this cap if you would like, serverside will send this info on first connection eventually
                print('Message Too Long!')
            else:
                try:
                    await self.send_message(message)
                except ConnectionResetError:
                    if self.connected:
                        await self.leave()
                    return
    
    async def run_client(self):
        await self.connect()
        await self.login()
        recieve_message = asyncio.create_task(client.client_handler())
        send_message = asyncio.create_task(client.receive_input())
        await asyncio.gather(recieve_message, send_message)

client = Client(host, port)
asyncio.run(client.run_client())
