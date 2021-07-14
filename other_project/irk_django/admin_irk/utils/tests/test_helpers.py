# coding=utf-8
import datetime

from irk.utils.helpers import parse_date


def test_parse_date():
    assert parse_date('2020-09-21', '%Y-%m-%d') == datetime.datetime(2020, 9, 21)
    assert parse_date('ass', '%Y-%m-%d') is None
