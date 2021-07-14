# coding=utf-8

import datetime
from mock import patch, Mock

from irk.adv.management.commands import adv_update_log


def test_find_log_files():

    # допустим, лог-файлы такие:
    ret = [
        ('file1', '[01/Dec/2020:06:25:07 +0800]'),
        ('file2', '[30/Nov/2020:06:25:06 +0800]'),
        ('file3', '[30/Nov/2020:18:00:00 +0800]'),
        ('file4', '[29/Nov/2020:06:25:08 +0800]'),
        ('file5', '[28/Nov/2020:06:25:08 +0800]'),
        ('file6', '[27/Nov/2020:06:25:08 +0800]')
    ]
    file_heads_mock = Mock(return_value=ret)

    # где тут лог-файлы с данными за 30 ноября?
    search_date = datetime.date(2020, 11, 30)
    with patch.object(adv_update_log, 'file_heads', file_heads_mock):
        found = adv_update_log.find_log_files('some', search_date)
    assert found == ['file2', 'file3', 'file4']

    # в последнем лог-файле могут быть данные за любую новую дату
    search_date = datetime.date(2020, 12, 25)
    with patch.object(adv_update_log, 'file_heads', file_heads_mock):
        found = adv_update_log.find_log_files('some', search_date)
    assert found == ['file1']

    # даты, раньше логов, быть не может
    search_date = datetime.date(1998, 12, 25)
    with patch.object(adv_update_log, 'file_heads', file_heads_mock):
        found = adv_update_log.find_log_files('some', search_date)
    assert found == []


def test_generator():
    gen = adv_update_log.log_filename_generator()
    assert next(gen) == 'access-irk.log'
    assert next(gen) == 'access-irk.log.1'
    assert next(gen) == 'access-irk.log.2.gz'
    assert next(gen) == 'access-irk.log.3.gz'
