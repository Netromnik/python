# -*- coding: utf-8 -*-

"""
Методы сбора кастомных метрик через newrelic
https://newrelic.com/docs/docs/custom-metric-collection
https://newrelic.com/docs/python/python-tips-and-tricks

Счетчики можно использовать так:
newrelic.agent.record_custom_metric('Custom/Signups', 1)
"""

from __future__ import absolute_import, print_function

import functools
import logging
import time
from contextlib import contextmanager

import newrelic.agent

logger = logging.getLogger("newrelic.metrics")


class NewrelicTimingMetric(object):
    """
        Измеряет время выполнения блока кода:

        with NewrelicTimingMetric('Custom/Timer'):
            time.sleep(0.01)
    """

    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc, value, tb):
        if not self.start_time:
            return
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.debug('%s %f' % (self.name, duration))
        newrelic.agent.record_custom_metric(self.name, duration)


def newrelic_record_timing(name):
    """
        Измеряет время выполнения блока кода декоратором:

        @newrelic_record_timing('Custom/Timer')
        def function():
            time.sleep(0.01)
    """

    def _decorator(f):
        @functools.wraps(f)
        def _wrapper(*args, **kwargs):
            with NewrelicTimingMetric(name):
                return f(*args, **kwargs)

        return _wrapper

    return _decorator


def timing(func):
    """
    Хелпер для измерения времени работы функции

    @timing
    def some_work():
        pass
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        time_taken = time.time() - start_time
        print('[timing] {:.3f}s {}'.format(time_taken, func.__name__))
        return result
    return wrapper


@contextmanager
def timethis(label):
    """
    Хелпер-контекстный менеджер
    with timethis('some'):
        ...code...
    """
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print('{}: {}'.format(label, end - start))
