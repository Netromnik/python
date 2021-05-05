# import socket
# from select import select
#
#
# def coroutine(f):
#     def func(*args,**kwargs):
#         g = f(*args,**kwargs)
#         g.send(None)
#         return g
#     return func
#
#
# def init_sock()->socket.socket:
#     soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     soc.setsockopt(socket.SOL_SOCKET,socket.SOCK_NONBLOCK,True)
#     soc.bind(('localhost',8080))
#     soc.listen()
#     return soc
#
# def server(soc:socket.socket):
#     loop_client = client()
#     try:
#         so_client, _ = soc.accept()
#         loop_client.
#
# @coroutine
# def client():
#     for soc in socket:
#         soc