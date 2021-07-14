from django.db.models import Max


def get_price_center_coordinate(price) -> type[int, int]:
    """Возвращает координаты центра банера"""

    top_y, top_x = price.coordinate_top_left.split(',')
    high, width = price.height_width.split(',')

    center_y = (int(top_y) + int(high)) - (int(high) / 2)
    center_x = (int(top_x) + int(width)) - (int(width) / 2)

    return int(center_x), int(center_y)


def separate_thousand(number) -> str:
    """Возвращает строку с числом разделенным пробелом по тысячному разряду"""

    number = str(number)

    value = ''
    for i, letter in enumerate(number[::-1], start=1):
        value += letter
        if i % 3 == 0:
            value += ' '
    value = value[::-1]

    return value.strip()


def count_ratio_percent(queryset, percent_field='percent'):
    """
    Определяем максимальный процент у выбранных объектов. Считаем ratio относительно этого значения и заполняем
    новый список со словарем из объекта и посчитанного значения

    :param QuerySet queryset: Объект QuerySet
    :param str percent_field: Имя поля процентов
    :return: Список словарей состоящих из object (элемент queryset) и ratio (Относительное значение процента)
    """

    max_value = queryset.aggregate(Max(percent_field)).get('{}__max'.format(percent_field))

    rows = []
    for item in queryset:
        percent = getattr(item, percent_field)
        ratio = 0 if not max_value else percent * 100 / max_value
        rows.append({'object': item, 'ratio': ratio})

    return rows
