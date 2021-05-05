import asyncio


async def handle_echo(reader, writer):
    while True:
        data = await reader.read(100)
        addr = writer.get_extra_info('peername')
        message = data.decode()
        print(f"Received {message!r} from {addr!r}")
        writer.write(data)
        await writer.drain()
        if '' == message:
            break
    print("Close the connection")
    writer.close()


async def main(socket:tuple):
    """ init server """
    server = await asyncio.start_server(
        handle_echo, socket[0],socket[1])

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        #  Start loop server
        await server.serve_forever()


if __name__ == '__main__':
    socket = ('127.0.0.1', 8888)
    asyncio.run(main(socket))
