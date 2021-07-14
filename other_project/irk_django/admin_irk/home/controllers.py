# -*- coding: utf-8 -*-

import datetime
import logging

from django.db.models import Q

from irk.home import settings as app_settings
from irk.news.models import BaseMaterial, Metamaterial
from irk.options.models import Site
from irk.special.models import Project

log = logging.getLogger(__name__)


class MaterialController(object):
    """Контроллер материалов для Главной страницы"""

    # Не показывать редактору материалы, запланированные к публикации
    # после этого момента в будущем
    FUTURE_WINDOW = {'minutes': 30}

    def __init__(self, stamp=None, show_hidden=False):
        """
        :param datetime.datetime stamp: метка времени, относительно которой выбираются закрепленные материалы.
            Default: now
        :param bool show_hidden: определяет показывать ли скрытые материалы. Default: False
        """
        # Временная метка, относительно которой выбираются закрепленные материалы
        self._stamp = stamp or datetime.datetime.now()

        self._site_home = Site.objects.get(slugs='home')
        self._ordering = ('-home_position', '-pk')
        # Общие фильтры для выборки материалов
        self._filters = {}
        if not show_hidden:
            self._filters['is_hidden'] = False

    def get_materials(self):
        """Получить итоговый список материалов"""

        qs = BaseMaterial.longread_objects \
            .for_site(self._site_home) \
            .exclude_future_drafts(**self.FUTURE_WINDOW) \
            .filter(stick_position__isnull=True, **self._filters) \
            .order_by(*self._ordering) \
            .values('pk', 'home_position')

        limit = app_settings.HOME_POSITIONS_COUNT
        material_list = list(qs[:limit])
        self._insert_sticked(material_list)

        materials_ids = [x['pk'] for x in material_list[:limit]]
        result_list = list(BaseMaterial.longread_objects
            .filter(pk__in=materials_ids)
            .prefetch_related('source_site', 'content_type')
            .select_subclasses()
        )
        result_list.sort(key=lambda m: materials_ids.index(m.pk))

        return result_list

    def _insert_sticked(self, material_list):
        """Вставить закрепленные материалы"""

        sticked_materials = self._get_sticked()

        for material in sticked_materials:
            material_list.insert(material['stick_position'] - 1, material)

    def _get_sticked(self):
        """Получить закрепленные материалы"""

        sticked_materials = BaseMaterial.longread_objects \
            .for_site(self._site_home) \
            .filter(stick_position__isnull=False, **self._filters) \
            .order_by('stick_position') \
            .values('pk', 'stick_position', 'home_position')

        return sticked_materials


class ProjectController(object):
    """
    Контроллер спецпроектов на Главной

    В блоке выводятся спецпроекты и метаматериалы-спецпроекты.
    В каждом спецпроекте выводится 3 последних материала.
    Сортировка спекпроектов по времени публикации последнего материала в них.
    """

    def get_items(self):
        """
        Получить итоговый список элементов

        item - можем быть спецпроектом или метаматериалом
        """

        projects = self._get_projects()
        metamaterials = self._get_metamaterials()
        items = projects + metamaterials

        items = self._sort(items)
        views = self._get_views(len(items))
        for item, view in zip(items, views):
            item.view = view

        return items

    def _get_projects(self):
        """Получить список спецпроектов"""

        projects = list(Project.objects.filter(show_on_home=True))
        for project in projects:
            # ~Q оптимизирует sql-запрос, избавляет от merge_index
            materials = project.news_materials.filter(~Q(is_hidden=True)).select_subclasses().order_by('-stamp')[:5]
            if not materials:
                projects.remove(project)
                continue

            project.materials = [m.cast() for m in materials]
            project.stamp = materials[0].stamp

        return projects

    def _get_metamaterials(self):
        """Получить список метаматериалов"""

        return list(Metamaterial.objects.filter(is_special=True, show_on_home=True, is_hidden=False))

    def _sort(self, items):
        """Сортировать по убыванию даты публикации"""

        return sorted(items, key=lambda x: x.stamp, reverse=True)

    def _get_views(self, length):
        """
        Получить список меток для определения как рендерить элемент.

        Правила:
            если элемент 1, широкая карточка
            на последней строке не должно быть одиночного элемента в виде квадратной карточки
            а так каждый 3й элемент в виде широкой карточки
        """

        if length < 1:
            return []

        if length == 1:
            return ['double']

        result = ['single'] * length
        for i in range(2, len(result), 3):
            result[i] = 'double'

        if length % 3 == 1:
            result[-2] = 'single'

        return result
