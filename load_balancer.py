import socket
from _thread import *
import sys

host = "127.0.0.1"
port = 6423

servers = [8000, 8001]

def main():

    ServerSocket = socket.socket()
    ServerSocket.bind((host, port))

    print('Listening..')
    ServerSocket.listen(5)

    turn = 0
    while True:
        Client, address = ServerSocket.accept()
        data = Client.recv(2048).decode('utf-8')
        sp = str(servers[turn])
        turn = (turn+1)%2 
        Client.sendall(str.encode(sp))

    ServerSocket.close()


main()

