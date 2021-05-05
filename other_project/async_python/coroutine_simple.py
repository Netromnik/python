def coroutine(func):
    def f (*args, **kwargs):
        g = func(*args, **kwargs)
        g.send(None)
        return g
    return f


@coroutine
def average():
    summ = 0
    count = 0
    _average = None
    while 1:
        try:
            x = yield
        except StopIteration:
            print("Done averege")
            break
        else:
            count += 1
            summ += x
            _average = summ // count
            print(_average)
    return _average