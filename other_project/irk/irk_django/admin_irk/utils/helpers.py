# -*- coding: utf-8 -*-

import contextlib
import datetime
import email.utils as email_utils
import locale
import os
import re
import shutil
import threading
import time
import types
from itertools import repeat
from math import ceil

# import chardet
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import ValidationError, validate_ipv4_address
from django.db import connection
from django.shortcuts import _get_queryset
from django.utils.encoding import DjangoUnicodeDecodeError
# from django.utils.text import force_unicode as fu
from pytils.numeral import choose_plural

# from map.models import Cities
# from options.models import Site


def iptoint(ip):
    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])

    return long(hexn, 16)


def get_client_ip(request):
    """Получение IP адреса клиента

    Параметры::
        request: объект класса `django.http.HttpRequest`

    >>> get_client_ip(request)
    '192.168.99.13'

    Возвращает `None`, если не удалось определить адрес

    >>> get_client_ip(request)
    None
    """

    ip = None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
        try:
            validate_ipv4_address(ip)
        except (ValidationError, DjangoUnicodeDecodeError):
            ip = None

    if ip is None:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def inttoip(n):
    d = 256 * 256 * 256
    q = []
    while d > 0:
        m, n = divmod(n, d)
        q.append(str(m))
        d /= 256

    return '.'.join(q)


# def force_unicode(text):
#     """Стараемся привести введенный текст к unicode"""
#
#     try:
#         text = fu(text)
#     except DjangoUnicodeDecodeError:
#         d = chardet.detect(text)
#         try:
#             text = text.decode(d.get('encoding', 'utf-8'))
#         except Exception as e:
#             raise DjangoUnicodeDecodeError(text, *e.args)
#
#     return text


def view_date_gte_now(request, year, month, day, *args, **kwargs):
    """ Проверяет тек. дата или из будущего передана во вьюху. (afisha,tv,) """

    now = datetime.datetime.now()
    try:
        date = datetime.date(int(year), int(month), int(day))
    except ValueError:
        return False
    return date >= now.date()


def get_week_range(date):
    """ По дате возвращает соответствующую ей неделю """
    weekday = date.isocalendar()[2] - 1
    monday = (date - datetime.timedelta(weekday))

    return [(monday + datetime.timedelta(delta)) for delta in range(7)]


def parse_email_date(date):
    """Парсит дату из письма"""
    date_tuple = email_utils.parsedate_tz(date)
    if date_tuple:
        # naive datetime в местном часовом поясе
        return datetime.datetime.fromtimestamp(email_utils.mktime_tz(date_tuple))

    return None


def parse_date(value, format='%Y-%m-%d'):
    """Парсит дату или нет"""
    try:
        return datetime.datetime.strptime(value, format)
    except (ValueError, TypeError):
        return None


@contextlib.contextmanager
def write_lock(model):
    """Блокирование таблицы модели на запись

    Использование:
        with lock(MyModel):
            # Пишем что-то важное

    http://dev.mysql.com/doc/refman/5.6/en/lock-tables.html
    """

    cursor = connection.cursor()
    cursor.execute('LOCK TABLES %s WRITE' % model._meta.db_table)
    yield
    cursor.execute('UNLOCK TABLES')


def time_combine(dt, tm):
    """Сумма даты и времени
    Параметры:
        dt: тип datetime.datetime
        tm: тип datetime.time
    """

    if not tm:
        return dt

    return dt + datetime.timedelta(hours=tm.hour, minutes=tm.minute, seconds=tm.second)


def reformat_column_view(source_list, column_count):
    """
    Преобразование списка так, чтобы при его выводе построчно создавалась иллюзия, что он отсортирован по столбцам

    Пример:
    >>> a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> reformat_column_view(a, 2)
    [1, 6,
     2, 7,
     3, 8,
     4, 9,
     5]
    >>> reformat_column_view(a, 3)
    [1, 4, 7,
     2, 5, 8,
     3, 6, 9]
    >>> reformat_column_view(a, 4)
    [1, 4, 6, 8,
     2, 5, 7, 9,
     3]
    """

    source_list = list(source_list)
    element_in_column_count = int(ceil(len(source_list) / float(column_count)))
    cur_col_number = 0
    working_dict = [[] for _ in xrange(element_in_column_count)]
    residue = column_count - (column_count * element_in_column_count - len(source_list))

    for section in source_list:
        working_dict[cur_col_number].append(section)
        cur_col_number += 1
        if cur_col_number >= element_in_column_count:
            cur_col_number = 0
            residue -= 1
            if residue == 0:
                element_in_column_count -= 1

    result_list = []
    for elements in working_dict:
        result_list += elements

    return result_list


def equable_column_split(source_list, column_count):
    """
    Деление списка на колонки с равномерным распределением
    Параметры:
        :param list source_list: список элементов
        :param int column_count: количество колонок
    """

    columns_count_list = list(repeat(0, column_count))
    formatted_pages = list(repeat([], column_count))

    pages_in_col = int(ceil(len(source_list) / column_count))
    extended_column_cont = len(source_list) - pages_in_col * column_count

    i = 0
    while i < column_count:
        if extended_column_cont > 0:
            columns_count_list[i] = pages_in_col + 1
            extended_column_cont -= 1
        else:
            columns_count_list[i] = pages_in_col

        formatted_pages[i] = source_list[:columns_count_list[i]]
        source_list = source_list[columns_count_list[i]:]
        i += 1

    return formatted_pages


def int_or_none(value):
    """
    Привести `value` к типу `int`. В случае ошибок вернет None

    :rtype: int or None
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def float_or_none(value):
    """
    Привести `value` к типу `float`. В случае ошибок вернет None

    :rtype: float or None
    """

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_object_or_none(entity, *args, **kwargs):
    u"""
    Использует get(), чтобы вернуть объект или None, если объект не существует.

    :param entity: Сущность для которой происходит вызов метода get().
    :type entity: Model or Manager or QuerySet.
    :raises: MultipleObjectsReturned, если возвращаются несколько объектов по переданным аргументам.
    :rtype: Model or None
    """
    try:
        queryset = _get_queryset(entity)
        return queryset.get(*args, **kwargs)
    except (ObjectDoesNotExist, ValueError):
        return None


def seconds_to_text(seconds_count, start=0, end=5, length=6):
    """
    Переводит количество секунд в текст

    Примеры:
        >>> seconds_to_text(31536000)
        1 год
        >>> seconds_to_text(2 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1)
        2 года 3 месяца 25 дней 23 часа 45 минут 1 секунду
        >>> seconds_to_text(2 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1, length=2)
        2 года 3 месяца
        >>> seconds_to_text(2 * 31536000 + 3 * 2592000 + 15 * 86400 + 45 * 60 + 1, start=1, end=4)
        27 месяцев 25 дней 45 минут
        >>> seconds_to_text(2 * 31536000 + 3 * 2592000 + 15 * 86400 + 45 * 60 + 1, start=1, length=1)
        27 месяцев

    :param seconds_count: количество секунд
    :type seconds_count: int
    :param start: начальная точность (число от 0 до 5)
    :type start: int
    :param end: конечная точность (число от 0 до 5)
    :type end: int
    :param length: количество элементов в тексте (число от 0 до 5)
    :type length: int
    :return: Текст
    :rtype: str
    """

    accuracies = [
        (60 * 60 * 24 * 30 * 12 + 60 * 60 * 24 * 5, (u'год', u'года', u'лет')),  # 0
        (60 * 60 * 24 * 30, (u'месяц', u'месяца', u'месяцев')),  # 1
        (60 * 60 * 24, (u'день', u'дня', u'дней')),  # 2
        (60 * 60, (u'час', u'часа', u'часов')),  # 3
        (60, (u'минуту', u'минуты', u'минут')),  # 4
        (1, (u'секунду', u'секунды', u'секунд')),  # 5
    ]

    result_texts = []

    for accuracy in accuracies[start:end + 1]:
        if seconds_count >= accuracy[0]:
            count = int(seconds_count / accuracy[0])
            unit = choose_plural(count, accuracy[1])
            result_texts.append(u'{} {}'.format(count, unit))
            seconds_count -= count * accuracy[0]
            length -= 1
            if length <= 0:
                break

    return u' '.join(result_texts)


def unique(sequence):
    """
    Возвращает список содержащий уникальные элементы из sequence.
    Сохраняет порядок следования элементов.

    :param sequence: последовательность элементов
    :rtype: list
    """

    output = list()
    for elem in sequence:
        if elem not in output:
            output.append(elem)

    return output


def big_int_from_time():
    """Большое целое на основе количества секунд с момента начала эпохи"""

    return int(time.time() * 1000000)


def filter_invalid_xml_chars(text):
    """
    Удаление запрещенных в xml символов из текста
    :param text: str
    :rtype: str
    :return: Очищеная строка
    """

    def valid_xml_char_ordinal(char):
        codepoint = ord(char)
        return 0x20 <= codepoint <= 0xD7FF or \
               codepoint in (0x9, 0xA, 0xD) or \
               0xE000 <= codepoint <= 0xFFFD or \
               0x10000 <= codepoint <= 0x10FFFF

    return filter(valid_xml_char_ordinal, text)


# def grouper(iterable, n, fillvalue=None):
#     """
#     Итератор группировки по n элементов из iterable.
#
#     :param iterable: итерируемый объект
#     :param n: количество элементов в группе
#     :param fillvalue: значение подстановки, если не хватает элементов для формирования группы
#
#         >>> list(grouper('ABCDEFG', 3, 'x'))
#         >>> [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]
#     """
#
#     args = [iter(iterable)] * n
#     return izip_longest(fillvalue=fillvalue, *args)


def unixtime_to_datetime(value):
    """
    Преобразовать дату из unixtime в datetime

    :param value: дата представленная в unixtime
    :type value: int or str
    :rtype: datetime.datetime or None
    """

    timestamp = int_or_none(value)

    if timestamp is not None:
        return datetime.datetime.fromtimestamp(timestamp)


def datetime_to_unixtime(value):
    """
    Преобразовать дату из datetime в unixtime

    :param value: дата предстваленная в datetime
    :rtype: int or None
    """

    if hasattr(value, 'timetuple'):
        return int(time.mktime(value.timetuple()))


def first_or_none(sequence):
    """
    Если в последовательность sequence непустая, вернет первый элемент.
    Иначе вернет None.

    :type sequence: list or tuple
    """

    try:
        return sequence[0]
    except IndexError:
        return None


def normalize_number(value):
    """Нормализуем номер телефона"""

    if not value:
        return None

    if not isinstance(value, (types.IntType, types.LongType)):
        if value.startswith('+'):
            value = value.lstrip('+')
        value = re.sub('[^0-9]', '', value)
        try:
            value = int(value)
        except ValueError:
            return None

    if value > 80000000000:
        value -= 80000000000
    elif value > 70000000000:
        value -= 70000000000

    return int(value)


def get_cities(slug):
    """ Список гоодов используемых в разделе """
    try:
        cities = Site.objects.get_by_alias(slug).cities_set.all().order_by('pk')
    except Site.DoesNotExist:
        cities = Cities.objects.none()
    return cities


def yes_or_no(question):
    """ Подтверждение для консольной команды """
    reply = str(raw_input(question + ' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False

    return yes_or_no("please enter y or n")


def save_file(fsrc, targetpath):
    """ Сохраняет содержимое file-like object по пути targetpath """
    # Create all upper directories if necessary
    upperdirs = os.path.dirname(targetpath)
    if upperdirs and not os.path.exists(upperdirs):
        os.makedirs(upperdirs)

    with open(targetpath, 'wb') as fdst:
        shutil.copyfileobj(fsrc, fdst)

    return targetpath


LOCALE_LOCK = threading.Lock()


@contextlib.contextmanager
def setlocale(name):
    """
    Временно установить локаль в "C", чтобы отформатировать дату
    """
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)
