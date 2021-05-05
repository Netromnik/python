import selectors
import socket


selector = selectors.DefaultSelector()


def create_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.1.1', 8001))
    sock.listen()
    selector.register(fileobj=sock, events=selectors.EVENT_READ, data=accept_socket)


def accept_socket(sock: socket.socket):
    client_socket, _ = sock.accept()
    selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=push_messege)


def push_messege(sock: socket.socket):
    request = sock.recv(1024)
    if request:
        sock.send(b'Hello')
    else:
        sock.close()


def event_loop():
    while True:
        q = selector.select()
        for key, _ in q:
            collback = key.data
            collback(key.fileobj)


if __name__ == '__main__':
    create_server()
    event_loop()
