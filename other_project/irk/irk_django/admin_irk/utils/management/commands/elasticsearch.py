# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging

from django.apps import apps
from django.core.management.base import BaseCommand

from irk.utils.search import ElasticSearchManager
from irk.utils.search.controllers import ElasticSearchController

log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Пересоздание всех индексов поиска ElasticSearch

    Примеры использования::
        manage.py elasticsearch all
            переиндексация всех моделей
        manage.py elasticsearch news.news afisha.event
            переиндексация новостей и событий афиши
        manage.py elasticsearch --remap news.news
            перед индексацией удаляет mappings
        manage.py elasticsearch --reload_settings
            обновить настройки индекса
    """

    help = 'Управление ElasticSearch'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.elastic_ctrl = ElasticSearchController()

    def add_arguments(self, parser):
        parser.add_argument(
            'models', nargs='*', type=str,
            help='List models for indexing (Ex.: app_name.model, app_name, all)',

        )
        parser.add_argument(
            '--remap', action='store_true', dest='remap', default=False,
            help='Delete mappings before indexing'
        )
        parser.add_argument(
            '--reload_settings', action='store_true', dest='reload_settings', default=False,
            help='Reload settings for index'
        )

    def handle(self, *args, **options):
        if options['reload_settings']:
            log.debug('Reloading settings')
            self.elastic_ctrl.reload_settings()

        for model in self._get_models(options):
            if not hasattr(model, 'search') or not isinstance(model.search, ElasticSearchManager):
                continue

            search = model.search.model_search

            if options['remap']:
                log.debug('Recreate type {0.index_name}_{0.type}'.format(search))
                self.elastic_ctrl.recreate_type(search)

            log.debug('Indexing {0._meta.app_label}_{0._meta.model_name}'.format(model))
            self.elastic_ctrl.bulk_create(search, chunk_size=5000)

    def _get_models(self, options):
        if not options['models']:
            return []

        if options['models'] == ['all']:
            return apps.get_models()

        models = []
        for arg in options['models']:
            # app.model
            try:
                app_label, model_name = arg.split('.')
                model = apps.get_model(app_label, model_name)
                models.append(model)
                continue
            except (ValueError, LookupError):
                pass

            # app
            try:
                app = apps.get_app_config(arg)
                models.extend(app.get_models())
                continue
            except LookupError:
                pass

        return models
