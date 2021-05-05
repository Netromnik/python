## generator async

def gen_1(name: str) -> str:
    for i in name:
        yield i


def get_2(number: int) -> int:
    for i in range(number):
        yield i


def sub_gen():
    x = "test_gen"
    message = yield x
    print("message: ", message)


task_list = [gen_1("username"), get_2(12)]
while True:
    try:
        task = task_list.pop(0)
        print(next(task))
        task_list.append(task)
    except StopIteration:
        pass
    except IndexError:
        print("end")
        break
