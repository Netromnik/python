# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import random

from django.db.models import Manager, Q
from django.db.models.aggregates import Count
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property
from model_utils.managers import InheritanceManager, InheritanceQuerySet
from irk.options.models import Site


class BaseMaterialQuerySet(InheritanceQuerySet):
    """QuerySet для бейсматириала"""

    def exclude_future_drafts(self, **kwargs):
        """
        Исключает из выборки скрытые материалы, у которых дата публикации в будущем.

        Редактору мешает вывод далеко запланированных публикаций в ленте новостей
        и на главной. Не скрытые материалы выводятся всегда.

        > BaseMaterial.objects.exclude_future_drafts(hours=1, minutes=30)
        """

        future = datetime.now() + timedelta(**kwargs)
        before_future = Q(stamp__lte=future.date()) & Q(published_time__lte=future.time())

        # не скрытые материалы с любой датой публикации
        # или
        # скрытые, но в пределах временного окна
        q = Q(is_hidden=False) | (Q(is_hidden=True) & before_future)

        return self.filter(q)


class BaseMaterialManager(InheritanceManager):
    """Менеджер материалов"""

    def get_queryset(self):
        return BaseMaterialQuerySet(self.model, using=self._db).prefetch_related('content_type')

    def for_site(self, site_id, search_source_site=False):
        """Выборка материалов, привязанных к разделу"""

        if isinstance(site_id, Site):
            site_id = site_id.id

        queryset = self.get_queryset()

        if search_source_site:
            # используйте .distinct(), чтобы избавиться от дублей
            return queryset.filter(Q(sites=site_id) | Q(source_site=site_id))

        return queryset.filter(sites=site_id)

    def filter_models(self, *args):
        """
        Отфильтровать материалы указанных моделей

        :param args: список моделей материалов, наследников BaseMaterial
        """

        ct_ids = set()
        for model in args:
            ct_ids.add(ContentType.objects.get_for_model(model, for_concrete_model=False))

        return self.get_queryset().filter(content_type_id__in=ct_ids)


class MaterialManager(BaseMaterialManager):
    """Менеджер материалов не относящихся к журналам"""

    def get_queryset(self):
        return super(MaterialManager, self).get_queryset().filter(magazine__isnull=True)


class LongreadMaterialManager(MaterialManager):
    """
    Менеджер материалов лонгридов

    Исключаем из BaseMaterial новости и статьи 9 мая
    """

    @cached_property
    def _excluded_cts(self):
        return list(ContentType.objects.filter(model__in=['news', 'article9may']).values_list('id', flat=True))

    def get_queryset(self):
        qs = super(LongreadMaterialManager, self).get_queryset()
        return qs.exclude(content_type_id__in=self._excluded_cts)


class MagazineMaterialManager(BaseMaterialManager):
    """Менеджер материалов журналов"""

    def get_queryset(self):
        qs = super(MagazineMaterialManager, self).get_queryset()
        return qs.filter(magazine__isnull=False)


class BaseNewsletterManager(InheritanceManager):
    pass
