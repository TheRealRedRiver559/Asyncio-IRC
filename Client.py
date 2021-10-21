import socket
import threading
import datetime
from rich import print

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9090))

username = input('Username : ').lower()
password = input('Password : ')
#gets time for the message.
def get_time():
    time = datetime.datetime.now()
    setting = 'AM'
    hours = int(time.strftime("%H"))
    if hours > 12:
        setting = 'PM'
        hours -= 12
    return time.strftime(f"%m/%d/%Y {hours}:%M {setting}")

def client_receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'LOGIN':
                client.send(f'I{username}'.encode())
                client.send(f'I{password}'.encode())
                print(client.recv(1024).decode())
            elif len(message) == 0:
                client.close()
                break
            elif message.startswith(username):
                print(f"[blue]{message[:message.find(':')]}[white]{message[message.find(':'):]}: [grey37]{get_time()}")
            elif message.startswith('Server:'):
                print(f"[yellow]{message}")
            else:
                print(f"[red]{message[:message.find(':')]}[white]{message[message.find(':'):]}: [grey37]{get_time()}")
        except ConnectionAbortedError:
            print('Connection Ended...')
            client.close()
            break
        except ConnectionResetError:
            print('Server Offline...')
            client.close()
            break

        
def client_send():
    while True:
        message = input("")
        #print(f"\033[A{' '*len(message)}\033[A") currently testing. Seems to only work in the IDE
        client.send(message.encode())

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()
send_thread = threading.Thread(target=client_send)
send_thread.start()
