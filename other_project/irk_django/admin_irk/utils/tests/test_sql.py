# coding=utf-8
from __future__ import unicode_literals

from irk.utils.sql import select


def test_select_one():
    """
    SQL строит запрос
    """
    query = select('col').from_('db').where('1 = 1')\
        .group_by('col').order_by('col').format('JSON')

    sql = query.sql().replace('\n', ' ')

    assert sql == 'SELECT col FROM db ' \
        'WHERE 1 = 1 GROUP BY col ORDER BY col FORMAT JSON'


def test_select_multiple_where():
    """
    Несколько условий в where объединяются через AND
    """
    query = select('col').from_('db').where('1 = 1').where('2 = 2')

    sql = query.sql().replace('\n', ' ')

    assert sql == 'SELECT col FROM db ' \
        'WHERE 1 = 1 AND 2 = 2'
