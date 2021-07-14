# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.db import transaction
from django.db.models.functions import Now

from irk.afisha.models import Review as AfishaReview
from irk.news.models import (Article, ArticleIndex, BaseMaterial, Photo,
                             TildaArticle)
from irk.news.settings import ARTICLE_INDEX_PHOTOS_COUNT
from irk.obed.models import Review as ObedReview
from irk.obed.models import TildaArticle as ObedTildaArticle
from irk.options.models import Site
from irk.utils.helpers import big_int_from_time

logger = logging.getLogger(__name__)


class ArticleIndexController(object):
    """
    Отвечает за выдачу материалов на индексе статей в нужном порядке
    с постраничным выводом и закрепленными материалами
    """

    # материалы этих классов будут выбираться и сохраняться в индексе
    SUPPORTED = Article, TildaArticle, ObedReview, AfishaReview, ObedTildaArticle

    def __init__(self):
        pass

    def layout_groups(self, page, start, limit):
        """
        Возвращает ленту материалов, сгруппированную для фронтенда, c пейджинацией
        TODO: красивее сделал Андрей: grouper(materials) - см. irk.utils.helpers.grouper
        """

        # на первой странице вставляем фотореп
        if page == 1:
            photos = self._photo()
            stop = start + limit -1  # вместо одного материала у нас блок фоторепа
        else:
            photos = []
            stop = start + limit

        materials = self.get_materials(start, stop)
        next_index = stop

        return next_index, self.group_articles(materials, photos)

    def get_supermaterial(self):
        supermaterial = BaseMaterial.objects \
            .filter(is_hidden=False) \
            .filter(article_index__is_super=True) \
            .first()

        return supermaterial.cast() if supermaterial else None

    def get_queryset(self):
        """
        Базовый запрос для ленты статей, возвращает отсортированные материалы
        """
        # обязательно isnull=False - тогда запрос делает inner join
        # без него работает в ~100 раз дольше (3940 vs 39 ms)
        query = BaseMaterial.objects \
            .filter(is_hidden=False) \
            .filter(article_index__isnull=False) \
            .filter(article_index__is_super=False) \
            .order_by('-article_index__position', '-article_index__admin_position') \
            .defer('content')  # долго передается

        return query

    def get_materials(self, start=0, stop=20):
        """
        Получить список материалов
        """
        return self.get_queryset().select_subclasses(*self.SUPPORTED)[start:stop]

    def get_other_materials(self):
        """
        Возвращает queryset для правой колонки в админке индекса статей
        """
        return self.get_queryset()

    def get_base_position(self):
        return big_int_from_time()

    @transaction.atomic
    def admin_sort(self, items, base_position=None):
        """
        Массовый реордер материалов из админки

        Параметр base_position используется вот для чего. Если в момент редактирования
        админом индекса выйдет новый материал, который админ не видит, то этот материал
        должен встать выше редактируемых. Поэтому с фронтенда приходит base_position -
        это время, когда админ открыл список. Это время сохраняется в position всех
        отредактированных материалов. У нового материала будет больший position, потому
        что он вышел позже, соответственно, он встанет выше.
        """
        if not base_position:
            base_position = big_int_from_time()

        self.reset_sticked()

        for index, item in enumerate(items):
            # на фронте stick_position 1-based, поправим
            if item.get('stick_position') is not None:
                if index+1 == item['stick_position']:
                    item['stick_position'] -= 1

            update = {
                'position': base_position,
                'admin_position': -index,  # должен быть desc для быстрого селекта
                'stick_position': item.get('stick_position'),
                'stick_date': Now() if item.get('stick_position') is not None else None,
            }

            ArticleIndex.objects.filter(material_id=item['id']).update(**update)

        self.move_sticked()

    @transaction.atomic
    def set_supermaterial(self, material_id=None):
        self.reset_supermaterial()
        return ArticleIndex.objects \
                .filter(material_id=material_id) \
                .update(is_super=True, stick_position=None, stick_date=None)

    def reset_supermaterial(self):
        return ArticleIndex.objects \
                .filter(is_super=True).update(is_super=False)

    def reset_sticked(self):
        return ArticleIndex.objects \
                .filter(stick_position__isnull=False).update(stick_position=None)

    @transaction.atomic
    def stick(self, material_id, position=None):
        """Закрепить или открепить материал"""
        if position is not None:
            # очистим тех, кто уже стоит на этой позиции
            ArticleIndex.objects.filter(stick_position=position).update(stick_position=None)
        ArticleIndex.objects.filter(material_id=material_id).update(stick_position=position)
        self.move_sticked()

        return position is not None

    @transaction.atomic
    def move_sticked(self):
        """
        Переместить закрепленные материалы в нужные позиции

        Эта функция вызывается после каждого изменения таблицы материалов и расставляет
        строки ArticleIndex в соответствии с их stick_position.
        Перестановка материалов местами работает, если материалы добавляются в индекс по одному.
        У нас так и есть.
        """
        # получим все закрепленные
        items = ArticleIndex.objects.filter(stick_position__isnull=False)
        updated = 0

        for item in items:
            # смотрим материал, который сейчас в ленте на этой позиции
            fact = ArticleIndex.objects.filter(is_super=False, material__is_hidden=False) \
                .order_by('-position', '-admin_position')[item.stick_position]
            if fact.id != item.id:
                # на этом месте стоит другой материал, поменям их местами
                self.swap(fact, item)
                updated += 1

        return updated

    @staticmethod
    @transaction.atomic
    def swap(m1, m2):
        """
        Поменять местами материалы (строки индекса) m1 и m2
        """
        m1.position, m2.position = m2.position, m1.position
        m1.admin_position, m2.admin_position = m2.admin_position, m1.admin_position
        m1.save(update_fields=['position', 'admin_position'])
        m2.save(update_fields=['position', 'admin_position'])

    def material_updated(self, material):
        """
        Хук, который вызывается при сохранении каждого материала
        """
        if not self.is_material_supported(material):
            logger.debug('material %d is not supported for ArticleIndex', material.id)
            return

        record = ArticleIndex.objects.filter(material_id=material.id).first()
        is_public = not material.is_hidden
        changed = False

        if record and not is_public:
            # снят с публикации
            logger.debug('material %d goes private, removing AI record...', material.id)
            ArticleIndex.objects.filter(material_id=material.id).delete()
            changed = True
        elif not record and is_public:
            # публикуется впервые
            logger.debug('material %d goes public, creating AI record...', material.id)

            record = ArticleIndex()
            record.material_id = material.id
            record.position = ArticleIndex.position_for_material(material)
            record.save()
            changed = True

        if changed:
            self.move_sticked()

    @classmethod
    def is_material_supported(cls, material):
        """
        Публиковать ли этот материал на индексе статей
        """
        if material.__class__ is BaseMaterial:
            logger.error('material %d saved as basematerial', material.id)

        return isinstance(material, cls.SUPPORTED)

    def _photo(self):
        """
        Блок фоторепортажей
        Из последних 30 фоторепов выбираем те, у которых есть лучшие фотки.
        """

        photos = Photo.material_objects.filter(is_hidden=False).select_subclasses().order_by('-stamp', '-pk')[:30]
        photos_best = []
        for item in photos:
            if item.gallery.has_best_image():
                photos_best.append(item)
                if len(photos_best) >= ARTICLE_INDEX_PHOTOS_COUNT:
                    break

        return photos_best

    def group_articles(self, articles, photos=None):
        """
        Группировка статей для вывода блоками в лейауте
        """
        groups = []
        it = iter(articles)
        try:
            # сначала блок "золотая спираль" из четырех элементов
            block = {'type': 'gold4', 'materials': [it.next() for _ in range(4)]}
            groups.append(block)

            # потом большая статья на всю ширину
            block = {'type': 'fullwidth', 'materials': [it.next()]}
            groups.append(block)

            # четыре маленьких квадрата
            block = {'type': 'row4', 'materials': [it.next() for _ in range(4)]}
            groups.append(block)

            # снова спираль
            block = {'type': 'gold4', 'materials': [it.next() for _ in range(4)]}
            groups.append(block)

            if photos:
                # блок фоторепортажей
                block = {'type': 'photo', 'materials': photos}
                groups.append(block)
            else:
                # статья на всю ширину
                block = {'type': 'fullwidth', 'materials': [it.next()]}
                groups.append(block)

            # четыре маленьких квадрата
            block = {'type': 'row4', 'materials': [it.next() for _ in range(4)]}
            groups.append(block)

            # два материала по полэкрана
            block = {'type': 'row2', 'materials': [it.next() for _ in range(2)]}
            groups.append(block)

        except StopIteration:
            pass

        return groups
