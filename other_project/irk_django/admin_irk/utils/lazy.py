# -*- coding: UTF-8 -*-
try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc


class LazyList(collections_abc.Sequence):
    """
    Список, который заполняется данными при первом обращении к элементам

    >>> fill_func = lambda: [1,2,3]
    >>> items = LazyList(fill_func)
    >>> assert items[0] == 1  # вызовется fill_func
    >>> assert items[2] == 2

    TODO: надо проверить, может эти функции есть в django.utils.functional,
    по крайней мере там есть LazyObject
    """

    def __init__(self, fill_func):
        self.data = None
        self.fill_func = fill_func

    def __len__(self):
        if not self.data:
            self._fill()
        return len(self.data)

    def __getitem__(self, index):
        if not self.data:
            self._fill()
        return self.data[index]

    def _fill(self):
        self.data = self.fill_func()


class LazyDict(collections_abc.Mapping):
    """
    Словарь, который запрашивает значение только в момент обращения

    >>> some = LazyDict({'photos': long_computation_func})
    >>> some['photos']  # запустит вычисления
    """
    def __init__(self, lazy_data):
        self.lazy_data = lazy_data
        self.data = dict()

    def __getitem__(self, key):
        if key not in self.data:
            self.data[key] = self.lazy_data[key]()
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
