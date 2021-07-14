# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Обновляет поле content_type для материалов созданных до перехода на явные proxy модели'

    SELECT_SQL = '''
        SELECT nb.id, dct.app_label, dct.model, os.slugs
        FROM irk.news_basematerial nb
        JOIN django_content_type dct ON dct.id = nb.content_type_id
        JOIN options_site os ON os.id = nb.source_site_id
        WHERE dct.app_label != os.slugs AND dct.app_label != CONCAT(os.slugs, 's');
    '''

    UPDATE_SQL = 'UPDATE irk.news_basematerial SET content_type_id = %s WHERE id = %s'

    def handle(self, **options):
        logger.debug('Start update content_types')

        with connection.cursor() as cursor:
            cursor.execute(self.SELECT_SQL)

            updates = []
            for row in cursor.fetchall():
                pk, app_label, model_name, site_slug = row
                try:
                    ct = ContentType.objects.get_by_natural_key(site_slug, model_name)
                    updates.append((ct.id, pk))
                except ContentType.DoesNotExist:
                    continue

            count = cursor.executemany(self.UPDATE_SQL, updates)
            logger.debug('Successful updated {} materials'.format(count))

        logger.debug('Finish update content_types')
