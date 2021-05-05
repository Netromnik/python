# TCP SERVER
# import socket
#
# socket_tcp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# socket_tcp.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
# socket_tcp.bind(('127.0.0.1',8000))
# socket_tcp.listen()
#
# while True:
#     print("accept")
#     so_client,addr = socket_tcp.accept()
#     while True:
#         request = so_client.recv(4096)
#         if not request:
#             break
#         else:
#             so_client.send(b"Hello\n")
#     so_client.close()
#
# socket_tcp.close()

## UDP server
# import socket
# socket_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# socket_udp.bind(('127.0.0.1',8000))
#
# while True:
#     request,addr = socket_udp.recvfrom(1024)
#     if not request:
#         break
#     else:
#         socket_udp.sendto(b"Hi I nooob",addr)
# socket_udp.close()