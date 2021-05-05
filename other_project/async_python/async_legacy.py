import asyncio
import logging

logging.getLogger('asyncio').setLevel(logging.WARNING)


@asyncio.coroutine
def print_number():
    for i in range(20):
        print("test")
        yield from asyncio.sleep(3)


@asyncio.coroutine
def print_time():
    for i in range(20):
        if i % 3:
            print(i)
        yield from asyncio.sleep(1)


@asyncio.coroutine
def main():
    task1 = asyncio.ensure_future(print_number())
    task2 = asyncio.ensure_future(print_time())
    yield from asyncio.gather(task1, task2)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
