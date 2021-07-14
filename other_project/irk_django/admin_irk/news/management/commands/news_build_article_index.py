# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.models import Q

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Заполнить таблицу индекса статей данными

    Можно запускать несколько раз, команда не перезаписывает существующие данные.

    Если нужно добавить в индекс статей новый тип материалов, просто допишите его
    в content_types и вызовите эту команду - все материалы  этого типа появятся
    в ленте статей.
    """

    help = 'Заполнить таблицу индекса статей данными'

    def handle(self, *args, **options):
        logger.info('Starting news_build_article_index command')

        content_types = self.content_types()

        sql = (
            """
            INSERT IGNORE INTO news_articleindex(material_id, position, is_super)
            SELECT id, unix_timestamp(timestamp(stamp, published_time))*1000000, false
            FROM news_basematerial
            WHERE stamp IS NOT NULL
                AND published_time IS NOT NULL
                AND content_type_id IN %s
            """,
            """
            INSERT IGNORE INTO news_articleindex(material_id, position, is_super)
            SELECT id, unix_timestamp(timestamp(stamp))*1000000, false
            FROM news_basematerial
            WHERE stamp IS NOT NULL
                AND published_time IS NULL
                AND content_type_id IN %s
            """,
        )
        with transaction.atomic():
            with connection.cursor() as c:
                for query in sql:
                    result = c.execute(query, [content_types])
                    logger.debug('%d rows inserted', result)

        logger.info('Finished')

    def content_types(self):
        # типы материалов, которые попадут в индекс статей
        query = ContentType.objects.filter(
            Q(model='article') |
            Q(app_label='news', model='tildaarticle') |
            Q(app_label='obed', model='review') |
            Q(app_label='afisha', model='review')
        )

        return list(query.values_list('id', flat=True))
