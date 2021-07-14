# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from irk.options.models import Site

from irk.news.models import BaseMaterial

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Создать/обновить права для работы с новостными материалами'

    def handle(self, **options):
        logger.debug('Start create material permissions')

        for model in apps.get_models():
            if not issubclass(model, BaseMaterial):
                continue

            if not model._meta.proxy:
                continue

            try:
                ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
            except ContentType.DoesNotExist:
                continue

            for perm_name in ('can_change',):
                perm, created = Permission.objects.update_or_create(
                    content_type=ct, codename=perm_name, defaults={'name': self.description(model)}
                )

                if created:
                    logger.info('Create permission {} for {}'.format(perm_name, model))

        logger.debug('Finish create material permissions')

    def description(self, model):
        """Описание permission"""

        opts = model._meta

        chunks = [u'{}'.format(opts.verbose_name_plural).capitalize()]
        site = Site.objects.filter(slugs=opts.app_label).first()
        if site:
            if not opts.proxy:
                chunks.append(u'раздела')
            chunks.append(site.name)

        return u' '.join(chunks)
