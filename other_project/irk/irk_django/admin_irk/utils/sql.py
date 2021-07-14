# coding=utf-8
"""
Простой конструктор SQL-запросов, который помогает формировать строку
для отправки в кликхаус.
"""

from __future__ import unicode_literals


class SelectQuery(object):
    def __init__(self):
        self._what = ''
        self._from = ''
        self._where = []
        self._group_by = None
        self._order_by = None
        self._format = None

    def select(self, select):
        self._what = select
        return self

    def from_(self, from_what):
        self._from = from_what
        return self

    def where(self, query, params=None):
        self._where.append(query)
        return self

    def group_by(self, group_by):
        self._group_by = group_by
        return self

    def order_by(self, order_by):
        self._order_by = order_by
        return self

    def format(self, format):
        self._format = format
        return self

    def sql(self):
        tokens = []
        tokens.append('SELECT {}'.format(self._what))
        tokens.append('FROM {}'.format(self._from))

        if self._where:
            if len(self._where) > 1:
                sql = ' AND '.join(self._where)
            else:
                sql = self._where[0]
            tokens.append('WHERE {}'.format(sql))

        if self._group_by:
            tokens.append('GROUP BY {}'.format(self._group_by))

        if self._order_by:
            tokens.append('ORDER BY {}'.format(self._order_by))

        if self._format:
            tokens.append('FORMAT {}'.format(self._format))

        return '\n'.join(tokens)


def select(what):
    return SelectQuery().select(what)
