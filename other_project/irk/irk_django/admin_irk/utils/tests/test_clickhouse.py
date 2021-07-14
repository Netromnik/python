# coding=utf-8
from __future__ import unicode_literals

from StringIO import StringIO

from irk.utils.clickhouse import make_tsv


def test_make_tsv():
    assert make_tsv(['a', 'b', 'c']) == 'a\tb\tc'
    assert make_tsv([1, 2, 3]) == '1\t2\t3'
    assert make_tsv([1, 's\ts', 3]) == '1\ts-s\t3'


def test_dialect():
    """
    Проверяет диалект на соответствие правилам эскейпа Tsv кликхауса
    https://clickhouse.tech/docs/ru/interfaces/formats/#tabseparated
    """
    from irk.utils.clickhouse import csv
    csv.get_dialect('clickhouse')

    buffer = StringIO()
    writer = csv.writer(buffer, dialect='clickhouse')

    writer.writerow(['\n'])
    assert buffer.getvalue() == '\\\n' + '\n'  # слеш и перенос каретки

    buffer.truncate(0)
    writer.writerow(['\t'])
    assert buffer.getvalue() == '\\\t' + '\n'

    buffer.truncate(0)
    writer.writerow(['\t'])
    assert buffer.getvalue() == '\\\t' + '\n'

    buffer.truncate(0)
    writer.writerow(["a'b'c"])
    assert buffer.getvalue() == "a\\'b\\'c" + '\n'
