import socket
from select import select

task_list = []
write_list = {}
read_list = {}


def init_socket() -> tuple:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    sock.bind(("localhost", 8080))
    sock.listen()
    while True:
        yield ('read', sock)
        client_sock, addr = sock.accept()
        print("Connect adr", addr)
        task_list.append(client(client_sock))


def client(sock: socket.socket) -> tuple:
    while True:
        yield ('read', sock)
        data = sock.recv(1024)
        if not data:
            break
        else:
            response = "Hi 2021\n\r".encode()
            yield ('write', sock)
            sock.send(response)
    sock.close()


def event_loop():
    while any([task_list, read_list, write_list]):
        while not task_list:
            ready_to_read, ready_to_write, _ = select(read_list, write_list, [])
            for sock in ready_to_read:
                task_list.append(read_list.pop(sock))
            for sock in ready_to_write:
                task_list.append(write_list.pop(sock))

        try:
            task = task_list.pop(0)
            target, sock = next(task)
            if target == 'read':
                read_list[sock] = task
            elif target == 'write':
                write_list[sock] = task
        except StopIteration:
            pass


task_list.append(init_socket())
event_loop()
