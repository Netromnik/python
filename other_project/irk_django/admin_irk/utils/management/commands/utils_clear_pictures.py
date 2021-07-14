# -*- coding: utf-8 -*-

import glob
import os

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from irk.gallery.models import Gallery


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help=u'Физическое удаление файлов')

    def handle(self, *args, **options):
        deleted_apps = ['auto', 'bandy2014', 'billing', 'blackouts', 'board', 'books', 'bwcair', 'coupons', 'discounts',
                        'drugs', 'forum', 'house', 'jobs', 'journals', 'mobile', 'newyear', 'orphans', 'realty', 'shop',
                        'shopping', 'sms', 'transport', 'tv', 'yellow_pages']

        cts = ContentType.objects.filter(app_label__in=deleted_apps).values_list('pk', flat=True)

        pictures_cnt = 0
        pictures_size = 0

        galleries = Gallery.objects.filter(content_type_id__in=cts)
        for gallery in galleries:
            pictures_cnt += gallery.pictures.count()

            for picture in gallery.pictures.all():

                file_full_name, ext = os.path.splitext(picture.image.path)
                pattern = '{}*_q*{}'.format(file_full_name, ext)
                thumbs = glob.glob(pattern)

                for thumb in thumbs:
                    pictures_size += os.path.getsize(thumb)
                    print thumb
                    if options['delete']:
                        os.remove(thumb)

        print 'count: ', pictures_cnt
        print 'size: ', pictures_size
