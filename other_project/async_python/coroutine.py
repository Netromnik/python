def coroutine(f):
    def func(*args, **kwargs):
        g = f(*args, **kwargs)
        g.send(None)
        return g
    return func

@coroutine
def sub_gen():
    while True:
        try:
            message = yield
        except StopIteration:
            break
        else:
            print('message:', message)
    return "is ok"


@coroutine
def delegator(g):
    # data =  yield from g
    try:
        data = yield
        g.send(data)
    except StopIteration as e:
        print(e.value)
        g.send(StopIteration)
    g.send('hi is work')
