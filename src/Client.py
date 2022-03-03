import socket
import threading
import datetime
from rich import print

def run_client():
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

  def recv_message(client):
      messageWL = client.recv(1024).decode()
      message = messageWL[3:]
      if len(message) == 0:
          return message
      length = int(messageWL[:3])
      if length != len(message):
          return (f'{message[:length]}')
      return message
  def send_message(client, message):
      length = str(len(message)).zfill(3)
      client.send(f'{length}{message}'.encode())
      return

  def client_receive():
      while True:
          try:
              message = recv_message(client)
              if message == 'LOGIN':
                  send_message(client, f'I{username}')
                  send_message(client, f'I{password}')
                  print(recv_message(client))
              elif len(message) == 0: #Connection Stopped
                  client.close()
                  break
              elif message.startswith(username): #Blue for your username
                  print(f"[blue]{message[:message.find(':')]}[white]{message[message.find(':'):]} [grey37]{get_time()}")
              elif message.startswith('Server:'): #Yellow for server
                  print(f"[yellow]{message}")
              else: #Red for other clients
                  print(f"[red]{message[:message.find(':')]}[white]{message[message.find(':'):]} [grey37]{get_time()}")
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
          send_message(client, message)

  receive_thread = threading.Thread(target=client_receive)
  receive_thread.start()
  send_thread = threading.Thread(target=client_send)
  send_thread.start()
if __name__ == '__main__':
  run_client()
