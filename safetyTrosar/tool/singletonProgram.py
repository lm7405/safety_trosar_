import socket
import threading


PORT_NUMBER = 8923


def is_port_enable():
    output = False
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serverSock.bind(('localhost', PORT_NUMBER))
        serverSock.listen(1)
        output = True
    except Exception:
        output = False
    finally:
        serverSock.close()
    return output


def start_listen():
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.bind(('localhost', PORT_NUMBER))
    serverSock.listen(1)

    while True:
        connectionSock, addr = serverSock.accept()
        msg = connectionSock.recv(1024)
        message = msg.decode('utf=8')
        print(message)


def send(message: str):
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.connect(('localhost', PORT_NUMBER))
    clientSock.send(message.encode('utf-8'))
