import socket
import threading
import struct
import stdiomask
import datetime
from rich import print


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 9090))

username = input('Username : ').lower()
password = stdiomask.getpass(prompt='Password : ', mask='*') #Visual Password hiding.

#gets time for the message. Atm its just the hard dates
def time():
    time = datetime.datetime.now()
    setting = 'AM'
    hours = int(time.strftime("%H"))
    if hours > 12:
        setting = 'PM'
        hours -= 12
    return time.strftime(f"%d/%m/%Y {hours}:%M:%S {setting}")

def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: 
            pass
        buf += newbuf
        count -= len(newbuf)
    return buf

def client_receive():
    while True:
        try:
            message = recv_one_message(client).decode()
            if message == 'LOGIN':
                send_one_message(client, username.encode())
                send_one_message(client, password.encode())
                print(recv_one_message(client).decode())

            elif message == 'CLOSE':
                client.close()
                print('Connection ended...')
                break
            elif message.startswith(username):
                print(f"[blue]{message}[/blue] [grey37]{time()}")
            elif message.startswith('Server:'):
                print(f"[yellow]{message}")
            else:
                print(f"[red]{message}[/red]: [grey37]{time()}")
        except ConnectionAbortedError:
            print('Connection Lost...')
            client.close()
            break
        except ConnectionResetError:
            print('Server offline...')
            client.close()
            break
        
def client_send():
    while True:
        message = (input(""))
        send_one_message(client, message.encode())

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()
send_thread = threading.Thread(target=client_send)
send_thread.start()
