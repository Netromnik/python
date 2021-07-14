# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os
import logging
from calendar import monthrange
from copy import copy
from datetime import datetime, timedelta

import xlsxwriter
from django.core.management.base import BaseCommand

from irk.utils.grabber.yandex_merika import YandexMetrikaGrabber

log = logging.getLogger(__name__)


def to_percent(value):
    return value / 100


def to_minutes(value):
    return str(timedelta(seconds=round(value)))


REPORT_SETTINGS = {
    'device_category': {
        'mobile': 'Мобильные устройства',
        'desktop': 'Десктопы',
    },
    'sections': [
        {'name': 'Весь сайт'},
        {'name': 'Главная', 'goal': '4914494', 'filter': '/'},
        {'name': 'Новости', 'goal': '1993423', 'filter': '/news/.*'},
        {'name': 'Афиша', 'goal': '2103874', 'filter': '/afisha/.*'},
        {'name': 'Погода', 'goal': '3982102', 'filter': '/weather/.*'},
        {'name': 'Обед', 'goal': '3982108', 'filter': '/obed/.*'},
        {'name': 'Туризм', 'goal': '3982120', 'filter': '/tourism/.*'},
        {'name': 'Конкурсы', 'goal': '20680725', 'filter': '/contests/.*'},
    ],
    'metric_names': {
        'visits': {'name': 'Визиты', },
        'pageviews': {'name': 'Просмотры'},
        'users': {'name': 'Посетители'},
        'affinityIndexInterests': {'name': 'Аффинити‑индекс', 'format': 'percent', 'func': to_percent},
        'percentNewVisitors': {'name': 'Доля новых посетителей', 'format': 'percent', 'func': to_percent,
                               'total': 'avg'},
        'bounceRate': {'name': 'Отказы', 'format': 'percent', 'func': to_percent, 'total': 'avg'},
        'pageDepth': {'name': 'Глубина просмотра', 'format': 'float', 'total': 'avg'},
        'avgVisitDurationSeconds': {'name': 'Время на сайте', 'func': to_minutes, 'total': 'avg'},
        'goal<goal_id>conversionRate': {'name': 'Конверсия', 'format': 'percent', 'func': to_percent, 'no_filter': True,
                                        'total': 'avg'},  # Конверсия считается неверно при использовании фильтра
        'goal<goal_id>reaches': {'name': 'Достижения цели'},
        'goal<goal_id>visits': {'name': 'Визиты'},
        'goal<goal_id>users': {'name': 'Посетители'},
    },
    'metrics': {
        'full_attendance': {
            'base': ['visits', 'pageviews', 'users', 'percentNewVisitors', 'bounceRate', 'pageDepth',
                     'avgVisitDurationSeconds'],
            'goal': ['goal<goal_id>conversionRate', 'goal<goal_id>reaches', 'goal<goal_id>visits', 'pageviews',
                     'goal<goal_id>users', 'percentNewVisitors', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds'],
        },
        'short_attendance': {
            'base': ['pageviews', 'users'],
            'goal': ['goal<goal_id>reaches', 'goal<goal_id>users']
        },
        'short_audience': ['visits'],
        'full_audience': {
            'base': ['visits', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds'],
            'goal': ['goal<goal_id>conversionRate', 'goal<goal_id>reaches', 'goal<goal_id>visits', 'bounceRate',
                     'pageDepth', 'avgVisitDurationSeconds']
        },
        'full_device': {
            'base': ['visits', 'pageviews', 'users', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds'],
            'goal': ['goal<goal_id>conversionRate', 'goal<goal_id>reaches', 'goal<goal_id>visits', 'pageviews',
                     'goal<goal_id>users', 'bounceRate', 'pageDepth', 'avgVisitDurationSeconds'],
        },
        'short_device': {
            'base': ['visits', 'users'],
            'goal': ['goal<goal_id>visits', 'goal<goal_id>users']
        },
        'short_interests': ['visits', 'affinityIndexInterests'],
    },
}


def month_to_text(number):
    month_names = {
        1: 'январь',
        2: 'февраль',
        3: 'март',
        4: 'апрель',
        5: 'май',
        6: 'июнь',
        7: 'июль',
        8: 'август',
        9: 'сентябрь',
        10: 'октябрь',
        11: 'ноябрь',
        12: 'декабрь',
    }
    return month_names[int(number)]


def get_metric_name(alias):
    return REPORT_SETTINGS['metric_names'][alias]['name']


def get_device_category(alias):
    device_categories = REPORT_SETTINGS['device_category']
    return device_categories[alias] if alias in device_categories else ''


def format_metric_value(alias, value):
    metric = REPORT_SETTINGS['metric_names'][alias]
    if 'func' in metric:
        func = metric['func']
        value = func(value)
    return str(value)


class Command(BaseCommand):
    """Команда для генерации отчетов по яндекс метрике для отдела продаж"""

    def add_arguments(self, parser):
        parser.add_argument('path', help='Путь для экспорта', type=str)
        parser.add_argument('year', help='Год', type=int)
        parser.add_argument('month', help='Месяц', type=int)
        parser.add_argument('--device', help='Устройства', choices=['all', 'mobile', 'desktop'])

    def handle(self, **options):
        start_path = options['path']
        year = options['year']
        month = options['month']
        device = options['device']

        _, last_day = monthrange(year, month)

        start_date_str = '{}-{}-01'.format(year, month)
        end_date_str = '{}-{}-{}'.format(year, month, last_day)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        name = 'IRKru_stat_op_{}_{}'.format(year, month)

        if not device or device == 'all':
            full_path = os.path.join(start_path, '{}.xlsx'.format(name))
            report_xlsx = ReportXlsx(full_path, start_date, end_date)
            report_xlsx.run()

        if not device or device == 'mobile':
            full_path = os.path.join(start_path, '{}_mobile.xlsx'.format(name))
            report_xlsx = ReportXlsx(full_path, start_date, end_date)
            report_xlsx.run(device_category='mobile')

        if not device or device == 'desktop':
            full_path = os.path.join(start_path, '{}_desktop.xlsx'.format(name))
            report_xlsx = ReportXlsx(full_path, start_date, end_date)
            report_xlsx.run(device_category='desktop')


class ReportXlsx(object):
    """Формирование xlsx отчета"""

    def __init__(self, name, start_date, end_date):
        self.workbook = xlsxwriter.Workbook(name)
        self.start_date = start_date
        self.end_date = end_date

        # Форматы ячеек
        self.formats = {
            'h1': self.workbook.add_format({'bold': True, 'size': 20}),
            'h2': self.workbook.add_format({'bold': True, 'underline': True}),
            'h3': self.workbook.add_format({'bold': True}),
            'percent': self.workbook.add_format({'num_format': '0.00%'}),
            'float': self.workbook.add_format({'num_format': '0.00'}),
        }

    def run(self, device_category=None):
        log.debug('*'*60)
        log.debug('Создание отчета {}...'.format(get_device_category(device_category)))
        for section in REPORT_SETTINGS['sections']:
            log.debug('Создание листа {}...'.format(section['name']))

            ws = self._create_worksheet(section['name'])

            self.add_title(ws, (0, 0), section, device_category)
            self.add_short_attendance(ws, (2, 0), section, device_category)
            self.add_short_audience(ws, (9, 0), section, device_category)
            if not device_category:
                self.add_short_device(ws, (9, 7), section)

            self.add_short_interests(ws, (20, 0), section, device_category)

            # Больше не нужно
            # self.add_full_attendance(ws, (20, 0), section, device_category)

            self.add_full_audience(ws, (37, 0), section, device_category)
            if not device_category:
                self.add_full_device(ws, (50, 0), section)

    def _create_worksheet(self, name):
        """Создание листа"""

        ws = self.workbook.add_worksheet(name)

        # Ширина столбцов
        ws.set_column(0, 0, 25)
        ws.set_column(1, 12, 15)
        ws.set_row(0, 20)

        return ws

    def _get_metric_format(self, alias):
        metric = REPORT_SETTINGS['metric_names'][alias]
        if 'format' in metric:
            return self.formats[metric['format']]

    def _get_metric_func(self, alias, value):
        metric = REPORT_SETTINGS['metric_names'][alias]
        if 'func' in metric:
            return metric['func'](value)
        return value

    def _metrics_to_titles(self, ws, start_position, metrics):
        """Метрики в названия колонок"""
        row, col = start_position

        for metric in metrics:
            ws.write_string(row, col, get_metric_name(metric), self.formats['h3'])
            col += 1

    def _find_age_name(self, age_id, data):
        for item in data['data']:
            if item['dimensions'][1]['id'] == age_id:
                return item['dimensions'][1]['name']

    def _write_cell(self, ws, row, col, value, metric_alias):
        if metric_alias.startswith('ym:s:'):
            metric_alias = metric_alias.replace('ym:s:', '')
        ws.write(row, col, self._get_metric_func(metric_alias, value), self._get_metric_format(metric_alias))

    def add_title(self, ws, start_position, section, device_category=None):
        """Заголовок раздела"""

        log.debug('Генерация заголовка...')

        row, col = start_position

        ws.write_string(row, col, section['name'], self.formats['h1'])
        date_str = '{} {}'.format(month_to_text(self.start_date.month), str(self.start_date.year))
        ws.write_string(row, col + 1, date_str, self.formats['h3'])
        ws.write_string(row, col + 3, get_device_category(device_category), self.formats['h3'])

    def add_short_interests(self, ws, start_position, section, device_category=None):
        """Основные данные интерересы пользователей"""

        log.debug('Генерация "Основные данные интерересы пользователей"...')

        metrics = REPORT_SETTINGS['metrics']['short_interests']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_interest(section, metrics, device_category)

        row, start_col = start_position
        col = start_col

        # Заголовок
        ws.write_string(row, col, 'Интерересы', self.formats['h2'])

        row += 1

        # Названия колонок
        self._metrics_to_titles(ws, (row, col + 1), [metrics[0]])
        ws.write_string(row, col + 2, 'Визиты %', self.formats['h3'])
        self._metrics_to_titles(ws, (row, col + 3), [metrics[1]])

        row += 1

        # Данные
        for item in data['data']:
            col = start_col
            name = item['dimensions'][0]['name']
            ws.write_string(row, col, name)
            for i, metric_alias in enumerate(data['query']['metrics']):
                col += 1
                value = item['metrics'][i]
                self._write_cell(ws, row, col, value, metric_alias)

                # Добавляем кастомный столбец с процентами визитов
                if metric_alias == 'ym:s:visits':
                    col += 1
                    value = value / data['totals'][i]
                    ws.write_number(row, col, value, self.formats['percent'])

            row += 1

    def _add_short_attendance(self, ws, start_position, section, kind, title, device_category=None):
        goal = section.get('goal', '')
        metrics = REPORT_SETTINGS['metrics']['short_attendance']
        metrics = metrics['base'] if not goal else metrics['goal']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_attendance(section, metrics, kind, device_category)

        row, col = start_position

        # Заголовок
        ws.merge_range(row, col, row, col + 1, title, self.formats['h2'])
        row += 1

        # Названия колонок
        self._metrics_to_titles(ws, (row, col), metrics)

        # Для недель необходимо брать данные только от полных недель
        if kind == 'week':
            full_week_ids = []
            for idx, date_list in enumerate(data['time_intervals']):
                start_date = datetime.strptime(date_list[0], '%Y-%m-%d')
                end_date = datetime.strptime(date_list[1], '%Y-%m-%d')
                week_days_count = (end_date - start_date).days
                if week_days_count == 6:
                    full_week_ids.append(idx)

        for metric_data in data['data'][0]['metrics']:
            if kind == 'week':
                metric_data = metric_data[min(full_week_ids):max(full_week_ids) + 1]
            value = round(sum(metric_data) / float(len(metric_data)))
            ws.write_number(row + 1, col, value)
            if kind != 'month':
                ws.write_number(row + 2, col, max(metric_data))
                ws.write_number(row + 3, col, min(metric_data))
            col += 1

    def add_short_attendance(self, ws, start_position, section, device_category=None):
        """Основные данные посещений"""

        log.debug('Генерация "Основные данные посещений"...')

        row, col = start_position
        start_row = row

        ws.write_string(row + 2, 0, 'Среднее', self.formats['h3'])
        ws.write_string(row + 3, 0, 'Максимальное', self.formats['h3'])
        ws.write_string(row + 4, 0, 'Минимальное', self.formats['h3'])

        self._add_short_attendance(ws, (start_row, col + 1), section, 'day', 'Ежедневно', device_category)
        self._add_short_attendance(ws, (start_row, col + 3), section, 'week', 'Еженедельно', device_category)
        self._add_short_attendance(ws, (start_row, col + 5), section, 'month', 'Ежемесячно', device_category)

    # Отключен
    def _add_full_attendance(self, ws, start_position, section, kind, title, device_category=None):
        """Подробные данные посещений"""

        goal = section.get('goal', '')
        metrics = REPORT_SETTINGS['metrics']['full_attendance']
        metrics = metrics['base'] if not goal else metrics['goal']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_attendance(section, metrics, kind, device_category)

        row, start_col = start_position
        col = start_col

        # Заголовок
        ws.write_string(row, col, title, self.formats['h2'])

        row += 1

        # Названия колонок
        ws.write_string(row, col, 'Даты', self.formats['h3'])
        self._metrics_to_titles(ws, (row, col + 1), metrics)

        # Данные
        col = start_col

        row += 1

        # Итого
        ws.write_string(row, col, 'Итого/среднее', self.formats['h3'])

        # Итоговые значения
        for idx, metric in enumerate(metrics):
            value = data['totals'][0][idx]
            col += 1
            self._write_cell(ws, row, col, value, metric)

        row += 1
        col = start_col
        start_row = row

        # Столбец дат
        for start_date, end_date in data['time_intervals']:
            date = start_date if kind == 'day' else '{} - {}'.format(start_date, end_date)
            ws.write_string(row, col, date)
            row += 1

        # Данные метрик
        col += 1

        for idx, metric in enumerate(metrics):
            row = start_row
            metric_data = data['data'][0]['metrics'][idx]
            for value in metric_data:
                self._write_cell(ws, row, col, value, metric)
                row += 1
            col += 1

    # Отключен
    def add_full_attendance(self, ws, start_position, section, device_category=None):
        """Подробные данные посещений по дням"""

        log.debug('Генерация "Подробные данные посещений по дням"...')

        row, col = start_position

        self._add_full_attendance(ws, (row, col), section, 'day', 'Ежедневная посещаемость', device_category)
        self._add_full_attendance(ws, (row + 35, col), section, 'week', 'Еженедельная посещаемость', device_category)

    def add_short_audience(self, ws, start_position, section, device_category=None):
        """Основные данные по аудитории"""

        log.debug('Генерация "Основные данные по аудитории"...')

        metrics = REPORT_SETTINGS['metrics']['short_audience']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_audience(section, metrics, device_category)

        row, col = start_position

        # Названия колонок
        ws.write_string(row, col + 1, 'Мужчины', self.formats['h3'])
        ws.write_string(row, col + 2, 'Женщины', self.formats['h3'])
        ws.write_string(row, col + 3, 'Мужчины', self.formats['h3'])
        ws.write_string(row, col + 4, 'Женщины', self.formats['h3'])
        ws.write_string(row, col + 5, 'Всего (визиты)', self.formats['h3'])

        # Всего
        total_visits = data['totals'][0]
        ws.write_number(row + 1, col + 5, total_visits)

        row += 1
        start_row = row
        start_col = col

        # Данные
        gender_ids = ['male', 'female']
        age_ids = []
        for item in data['data']:
            age_ids.append(item['dimensions'][1]['id'])
        age_ids = sorted(list(set(age_ids)))

        prepared_data = {}

        for item in data['data']:
            gender_id = item['dimensions'][0]['id']
            age_id = item['dimensions'][1]['id']
            if age_id not in prepared_data:
                prepared_data[age_id] = {}
            prepared_data[age_id][gender_id] = item['metrics'][0]

        # Возроста
        for age_id in age_ids:
            ws.write_string(row, col, self._find_age_name(age_id, data))
            row += 1
        ws.write_string(row, col, 'Всего', self.formats['h3'])

        # Визиты
        row = start_row
        total_value = {'male': 0, 'female': 0}
        for age_id in age_ids:
            col = start_col + 1
            for gender_id in gender_ids:
                try:
                    value = prepared_data[age_id][gender_id]
                except KeyError:
                    value = 0
                ws.write_number(row, col, value)
                total_value[gender_id] += value
                col += 1
            row += 1

        # Итого
        col = start_col + 1
        ws.write_number(row, col, total_value['male'])
        ws.write_number(row, col + 1, total_value['female'])

        # Процентное соотношение
        row = start_row
        total_value = {'male': 0, 'female': 0}
        for age_id in age_ids:
            col = start_col + 3
            for gender_id in gender_ids:
                try:
                    value = prepared_data[age_id][gender_id] / float(total_visits)
                except KeyError:
                    value = 0
                ws.write_number(row, col, value, self.formats['percent'])
                total_value[gender_id] += value
                col += 1
            row += 1

        # Итого
        col = start_col + 3
        ws.write_number(row, col, total_value['male'], self.formats['percent'])
        ws.write_number(row, col + 1, total_value['female'], self.formats['percent'])

    def add_full_audience(self, ws, start_position, section, device_category=None):
        """Подробные данные по аудитории"""

        log.debug('Генерация "Подробные данные по аудитории"...')

        goal = section.get('goal', '')
        metrics = REPORT_SETTINGS['metrics']['full_audience']
        metrics = metrics['base'] if not goal else metrics['goal']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_audience(section, metrics, device_category)

        row, start_col = start_position
        col = start_col

        # Заголовок
        ws.write_string(row, col, 'Аудитория', self.formats['h2'])

        row += 1

        # Названия колонок
        col += 1
        for metric in metrics:
            ws.merge_range(row, col, row, col + 1, get_metric_name(metric), self.formats['h3'])
            ws.write_string(row + 1, col, 'Мужчины', self.formats['h3'])
            ws.write_string(row + 1, col + 1, 'Женщины', self.formats['h3'])
            col += 2

        # Данные
        gender_ids = ['male', 'female']
        age_ids = []
        for item in data['data']:
            age_ids.append(item['dimensions'][1]['id'])
        age_ids = sorted(list(set(age_ids)))

        prepared_data = {}

        for idx, metric in enumerate(metrics):
            if metric not in prepared_data:
                prepared_data[metric] = {}
            for item in data['data']:
                gender_id = item['dimensions'][0]['id']
                age_id = item['dimensions'][1]['id']
                if age_id not in prepared_data[metric]:
                    prepared_data[metric][age_id] = {}
                prepared_data[metric][age_id][gender_id] = item['metrics'][idx]

        # Возроста
        start_row = row + 2
        col = start_col
        row = start_row
        for age_id in age_ids:
            ws.write_string(row, col, self._find_age_name(age_id, data))
            row += 1
        ws.write_string(row, col, 'Всего', self.formats['h3'])

        # Данные
        start_col = col + 1
        for idx, metric in enumerate(metrics):
            total_value = {'male': 0, 'female': 0}
            row = start_row
            for age_id in age_ids:
                col = start_col + 2 * idx
                for gender_id in gender_ids:
                    try:
                        value = prepared_data[metric][age_id][gender_id]
                    except KeyError:
                        value = 0
                    self._write_cell(ws, row, col, value, metric)
                    total_value[gender_id] += value
                    col += 1
                row += 1

            # Итого
            col = start_col + 2 * idx

            if metric == 'goal<goal_id>conversionRate':
                # !!! Костыль !!! для верного определения средней конверсии по полу
                mq = ReportQueries()
                mq.set_dates(self.start_date, self.end_date)
                total_value['male'] = mq.get_audience_gender_conversion_total(section, device_category, 'male')
                total_value['female'] = mq.get_audience_gender_conversion_total(section, device_category, 'female')
            else:
                metric_params = REPORT_SETTINGS['metric_names'][metric]
                if 'total' in metric_params and metric_params['total'] == 'avg':
                    total_value['male'] = total_value['male'] / float(len(age_ids))
                    total_value['female'] = total_value['female'] / float(len(age_ids))
            self._write_cell(ws, row, col, total_value['male'], metric)
            self._write_cell(ws, row, col + 1, total_value['female'], metric)

    def add_full_device(self, ws, start_position, section):
        """Подробные данные по устройствам"""

        log.debug('Генерация "Подробные данные по устройствам"...')

        goal = section.get('goal', '')
        metrics = REPORT_SETTINGS['metrics']['full_device']
        metrics = metrics['base'] if not goal else metrics['goal']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_device(section, metrics)

        row, start_col = start_position
        col = start_col

        # Заголовок
        ws.write_string(row, col, 'Устройста', self.formats['h2'])

        row += 1

        # Названия колонок
        ws.write_string(row, col, 'Тип устройства', self.formats['h3'])
        self._metrics_to_titles(ws, (row, col + 1), metrics)

        # Данные

        row += 1

        # Итого
        ws.write_string(row, col, 'Итого/среднее', self.formats['h3'])

        # Итоговые значения
        for idx, metric in enumerate(metrics):
            value = data['totals'][idx]
            col += 1
            self._write_cell(ws, row, col, value, metric)

        row += 1
        start_row = row

        # Данные
        col = start_col

        # Столбец устройств
        for item in data['data']:
            ws.write_string(row, col, item['dimensions'][0]['name'])
            row += 1

        # Данные метрик
        row = start_row
        col += 1
        for item in data['data']:
            col = start_col
            for idx, metric in enumerate(metrics):
                value = item['metrics'][idx]
                col += 1
                self._write_cell(ws, row, col, value, metric)
            col += 1
            row += 1

    def add_short_device(self, ws, start_position, section):
        """Доли устройств"""

        log.debug('Генерация "Доли устройств"...')

        goal = section.get('goal', '')
        metrics = REPORT_SETTINGS['metrics']['short_device']
        metrics = metrics['base'] if not goal else metrics['goal']

        mq = ReportQueries()
        mq.set_dates(self.start_date, self.end_date)
        data = mq.get_device(section, metrics)

        row, start_col = start_position
        col = start_col

        # Названия колонок
        self._metrics_to_titles(ws, (row, col + 1), metrics)

        row += 1
        start_row = row

        # Столбец устройств
        for item in data['data']:
            ws.write_string(row, col, item['dimensions'][0]['name'], self.formats['h3'])
            row += 1

        # Данные долей
        row = start_row
        col += 1
        for item in data['data']:
            col = start_col
            for idx, metric in enumerate(metrics):
                total_value = data['totals'][idx]
                value = item['metrics'][idx] / float(total_value)
                col += 1
                ws.write(row, col, value, self.formats['percent'])
            col += 1
            row += 1

    def __del__(self):
        self.workbook.close()


class ReportQueries(object):

    def set_dates(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def _prepare_metrics_string(self, metrics):
        return ','.join(['ym:s:{}'.format(x) for x in metrics])

    def get_attendance(self, section, metrics, group, device_category):
        kind = 'bytime'

        params = {
            'group': group
        }
        return self.run_grabber(kind, params=params, section=section, metrics=metrics, device_category=device_category)

    def get_audience(self, section, metrics, device_category):
        params = {
            'dimensions': 'ym:s:gender,ym:s:ageInterval'
        }
        return self.run_grabber(params=params, section=section, metrics=metrics, device_category=device_category)

    def get_audience_gender_conversion_total(self, section, device_category, gender_id):
        """Запрос для получения средней конверсии по полу"""
        filters = ["ym:pv:gender=='{}'".format(gender_id)]

        metrics = ['goal<goal_id>conversionRate']
        params = {
            'dimensions': 'ym:s:ageInterval'
        }

        # Для конверссии не нужно фильтровать по разделам
        section = copy(section)  # чтобы не модифицировать оригинальный объект
        if 'filter' in section:
            del section['filter']

        data = self.run_grabber(params=params, section=section, metrics=metrics, device_category=device_category,
                                filters=filters)
        return data['totals'][0]

    def get_device(self, section, metrics):
        params = {
            'dimensions': 'ym:s:deviceCategory'
        }
        return self.run_grabber(params=params, section=section, metrics=metrics)

    def get_interest(self, section, metrics, device_category):
        params = {
            'dimensions': 'ym:s:interest'
        }
        return self.run_grabber(params=params, section=section, metrics=metrics, device_category=device_category)

    def run_grabber(self, kind='', params=None, section=None, metrics=None, device_category=None, filters=None):
        params = {} if params is None else params

        if metrics:
            goal = section.get('goal', '')
            metrics_string = self._prepare_metrics_string(metrics)
            if goal:
                metrics_string = metrics_string.replace('<goal_id>', goal)
            params['metrics'] = metrics_string

        grabber = YandexMetrikaGrabber(kind)
        grabber.set_param(date1=self.start_date.strftime('%Y-%m-%d'))
        grabber.set_param(date2=self.end_date.strftime('%Y-%m-%d'))
        grabber.set_param(accuracy='medium')
        grabber.set_param(**params)

        if not filters:
            filters = []
        if device_category:
            if device_category == 'desktop':
                filters.append("ym:pv:deviceCategory=='desktop'")
            elif device_category == 'mobile':
                filters.append("ym:pv:deviceCategory=='mobile' OR ym:pv:deviceCategory=='tablet' ")
        no_section_filters = list(filters)

        if section and 'filter' in section:
            if section['filter'] == '/':
                filters.append("ym:pv:URLPath=='/'")
            else:
                filters.append("ym:pv:URLPath=~'{}'".format(section['filter']))

        if filters:
            grabber.set_param(filters=' AND '.join(filters))

        data = grabber.run()

        # !!! Костыль !!!!
        # Второй запрос для получения верной конверсии при использовании фильтра
        if section and 'filter' in section:
            # Ищем индексы метрик которые нужно пересчитать
            no_filter_idx = []
            for idx, metric in enumerate(metrics):
                if 'no_filter' in REPORT_SETTINGS['metric_names'][metric]:
                    no_filter_idx.append(idx)
            # Если есть метрики с no_filter параметром то делаем повторный запрос без фильтра
            # и подменяем данные в оригинальном ответе
            if no_filter_idx:
                grabber = YandexMetrikaGrabber(kind)
                grabber.set_param(date1=self.start_date.strftime('%Y-%m-%d'))
                grabber.set_param(date2=self.end_date.strftime('%Y-%m-%d'))
                grabber.set_param(accuracy='full')
                grabber.set_param(**params)
                if device_category:
                    grabber.set_param(filters=' AND '.join(no_section_filters))
                no_filter_data = grabber.run()
                for idx in no_filter_idx:
                    for param in ['totals', 'min', 'max']:
                        if param in data:
                            if isinstance(data[param][idx], list):
                                for total_idx, item in enumerate(data[param]):
                                    data[param][total_idx][idx] = no_filter_data[param][total_idx][idx]
                            else:
                                data[param][idx] = no_filter_data[param][idx]

                    # Найти элемент с таким же dimensions в no_filter_data
                    for data_idx, item in enumerate(data['data']):
                        for no_filter_data_idx, no_filter_item in enumerate(no_filter_data['data']):
                            if no_filter_item['dimensions'] == item['dimensions']:
                                data['data'][data_idx]['metrics'][idx] = \
                                    no_filter_data['data'][no_filter_data_idx]['metrics'][idx]
                                break
        return data
