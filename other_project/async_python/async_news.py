import asyncio


async def print_number():
    for i in range(20):
        print(i)
        await asyncio.sleep(1)


async def print_hi():
    for i in range(20):
        if i % 3 == 0:
            print("hi")
        await asyncio.sleep(1)


async def main():
    task1 = asyncio.create_task(print_number())
    task2 = asyncio.create_task(print_hi())
    await asyncio.gather(task2, task1)


if __name__ == '__main__':
    loop = asyncio.run(main(), debug=True)
