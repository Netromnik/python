"""
  Последовательный метод работы ,невытесняющая многозадачность
  работает через повторения
"""
# Tcp server multitask
# import socket
# from select import select
#
# list_sock = []
# def create_socket()->socket.socket:
#     socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     socket_tcp.bind(('127.0.0.1', 8001))
#     socket_tcp.listen()
#     return socket_tcp
#
# def accept_socket(_socket: socket.socket):
#     so_client, _ = _socket.accept()
#     list_sock.append(so_client)
#
#
# def send_message(so_client: socket.socket):
#     request = so_client.recv(4096)
#     if request:
#         so_client.send(b"Hello\n")
#     else:
#         so_client.close()
#
# def event_loop(server_socket):
#     while True:
#         ready_to_read,_,_ = select(list_sock,[],[])
#         for sock in ready_to_read:
#             if sock is server_socket:
#                 accept_socket(sock)
#             else:
#                 send_message(sock)
#
# if __name__ == '__main__':
#     sock = create_socket()
#     list_sock.append(sock)
#     event_loop(sock)
#

# UDP server multitask
# import socket
#
# def create_socket()->socket.socket:
#     socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     socket_udp.bind(('127.0.0.1', 8001))
#     return socket_udp
#
# def send_message(socket_udp: socket.socket):
#     while True:
#         request,addr = socket_udp.recvfrom(1024)
#         if request:
#             socket_udp.sendto(b"Hello\n",addr)
#         else:
#             socket_udp.close()
#
# if __name__ == '__main__':
#     sock = create_socket()
#     send_message(sock)