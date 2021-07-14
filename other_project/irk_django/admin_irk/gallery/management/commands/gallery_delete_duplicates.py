# -*- coding: utf-8 -*-

import logging
from collections import defaultdict

from django.core.management.base import BaseCommand

from irk.gallery.models import GalleryPicture


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Команда удаления дубликатов в модели GalleryPicture'

    def handle(self, **options):
        logger.debug('Start deleting duplicates from GalleryPicture')

        data = defaultdict(list)
        for gallery_id, picture_id, gp_id in GalleryPicture.objects.values_list('gallery_id', 'picture_id', 'id'):
            data[(gallery_id, picture_id)].append(gp_id)

        ids_for_remove = []
        for ids in data.itervalues():
            if len(ids) > 1:
                # Берем id кроме первого
                ids_for_remove.extend(ids[1:])

        gps = GalleryPicture.objects.filter(id__in=ids_for_remove)
        logger.debug(u'Удалено {} записей'.format(gps.count()))
        gps.delete()

        logger.debug('Finish deleting duplicates from GalleryPicture')
