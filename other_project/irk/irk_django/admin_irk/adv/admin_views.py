from __future__ import unicode_literals

import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from adv import clickhouse
from utils.http import json_response
from utils.helpers import parse_date


@staff_member_required
def place_stat(request):
    """
    Статистика по показам баннерных мест (админский интерфейс)
    """
    return render(request, 'admin/adv/place_stat.html', {})


@json_response
@staff_member_required
def places_json(request):
    """
    API для получения строк таблицы просмотра рекламных мест
    """
    # фильтр по дате через гет-параметры
    filters = get_filters(request)

    data = clickhouse.place_report(**filters)
    data = clickhouse.place_report_add_titles(data)

    data = sorted(data, key=lambda item: int(item['Loads']), reverse=True)

    return data


def get_filters(request):
    filters = {}

    # даты по-умолчанию служат как защита от дурака
    today = datetime.datetime.today()
    date_start_default = today - datetime.timedelta(30)
    date_end_default = today

    filters['date_start'] = parse_date(request.GET.get('dateStart'), '%Y%m%d') or date_start_default
    filters['date_end'] = parse_date(request.GET.get('dateEnd'), '%Y%m%d') or date_end_default

    return filters
