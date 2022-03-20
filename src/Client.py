import threading
import socket
import datetime
from rich import print
import json

username = input('Username: ')

def get_time():
    time = datetime.datetime.now()
    setting = 'AM'
    hours = int(time.strftime("%H"))
    if hours > 12:
        setting = 'PM'
        hours -= 12
    return time.strftime(f"%m/%d/%Y {hours}:%M {setting}")

def send_message(client):
    while True:
        message = input()
        data = json.dumps({'username':username, 'message':message})
        client.send(data.encode())

def recv_message(client):
    while True:
        message_data = json.loads(client.recv(1024).decode())
        message = f"{message_data['username']}: {message_data['message']}"

        if message_data['username'] == username: #Blue for your username
            print(f"[blue]{message[:len(username)]} [white]{message[len(username):]} [grey37]{get_time()}")
        else:
            print(f"[red]{message[:len(message_data['username'])]} [white]{message[len(message_data['username']):]} [grey37]{get_time()}")

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect_ex(('127.0.0.1', 9090))
    recv_thread = threading.Thread(target=recv_message, args=(client,))
    recv_thread.start()
    message_thread = threading.Thread(target=send_message, args=(client,))
    message_thread.start()

run_client()
