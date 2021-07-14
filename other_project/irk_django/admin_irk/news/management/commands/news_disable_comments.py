# -*- coding: utf-8 -*-

import datetime
import logging

from django.core.management.base import BaseCommand

from irk.news.models import News

logger = logging.getLogger(__name__)


def need_disable_comments(material):
    """Проверка необходимости отключения комментариев в новости"""

    day_start_hour = 9  # Час с которого начинаются дневные новости
    day_end_hour = 17  # Час в который кончаются дневные новости
    disable_time = 24  # Количество часов неактивности через которое комменты закроются
    night_disable_hour = day_start_hour + 1  # Час с которого разрешено закрывать комменты к ночным новостям

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    yesterday = today - datetime.timedelta(1)
    now = datetime.datetime.now()

    if not material.published_time:
        material.published_time = now.time()
    material_published_time = datetime.datetime.combine(material.stamp, material.published_time)

    # Если новость была добавлена с 17:00 до 09:00, то закрываем комменты не раньше 10 утра
    allow_disable_time = material_published_time  # Ближайшее время в которое возможно закрыть новость
    # Сегодня до 9:00
    if material.published_time < datetime.time(day_start_hour) and material.stamp == today:
        allow_disable_time = datetime.datetime.combine(today, datetime.time(night_disable_hour))
    # Вчера после 17:00
    elif material.published_time > datetime.time(day_end_hour) and material.stamp == yesterday:
        allow_disable_time = datetime.datetime.combine(today, datetime.time(night_disable_hour))
    # Сегодня после 17:00
    elif material.published_time > datetime.time(day_end_hour) and material.stamp == today:
        allow_disable_time = datetime.datetime.combine(tomorrow, datetime.time(night_disable_hour))

    # Время последней активности в новости
    last_active_time = material_published_time

    last_message = material.get_last_comment()
    if last_message:
        last_active_time = last_message.created

    return now >= last_active_time + datetime.timedelta(hours=disable_time) and now >= allow_disable_time


class Command(BaseCommand):
    help = u'Отключение комментариев к устаревшим новостям'

    def handle(self, *args, **options):
        news = News.objects.filter(disable_comments=False, is_hidden=False,
                                   is_auto_disable_comments=True).order_by('id')
        for material in news:
            if need_disable_comments(material):
                material.disable_comments = True
                material.save(update_fields=['disable_comments'])
                logger.debug('Disable comments for news {}'.format(material.pk))
