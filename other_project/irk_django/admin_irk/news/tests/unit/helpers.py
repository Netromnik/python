# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime
import random

from django_dynamic_fixture import G
from django.contrib.contenttypes.models import ContentType

from irk.news.models import Article, News, Infographic, Photo, Video, Subject, Category
from irk.tests.unit_base import UnitTestBase
from irk.news.helpers import SimilarMaterialHelper
from irk.options.models import Site
from irk.special.models import Project


class SimilarMaterialHelperTest(UnitTestBase):
    """Тесты для хелпера похожих материалов"""

    def setUp(self):
        self.news_site = Site.objects.get(slugs='news')

    def test_subject(self):
        """
        Возвращаются материалы с таким же сюжетом
        """

        subject = G(Subject)
        material = G(News, subject=subject, is_hidden=False)

        similar_longreads = self._create_longreads(subject=subject, is_hidden=False, n=2)
        self._create_longreads(subject=None, is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal(similar_longreads, result_longreads)

    def test_tags(self):
        """Материалов по сюжету нет, возращаются материалы по тегам"""

        material = G(Video, is_hidden=False)
        material.tags.add('test')

        similar_longreads = self._create_longreads(is_hidden=False, n=2)
        for similar in similar_longreads:
            similar.tags.add('test')

        self._create_longreads(is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal(similar_longreads, result_longreads)

    def test_category(self):
        """
        Материалов по сюжету и по тегам нет, возвращаются материалы по рубрике (категории).

        Ипользуется для материалов из раздела Новости
        """

        category = G(Category)
        material = G(News, category=category, is_hidden=False, source_site=self.news_site)

        similar_longreads = self._create_longreads(category=category, is_hidden=False, n=2)
        self._create_longreads(category=None, is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal(similar_longreads, result_longreads)

    def test_subject_and_tags(self):
        """Материалов по сюжету не хватает, добавляются материалы по тегам"""

        subject = G(Subject)
        material = G(Photo, subject=subject, is_hidden=False)
        material.tags.add('test')

        similar_longread_by_subject = self._create_longreads(subject=subject, is_hidden=False)
        similar_longread_by_tags = self._create_longreads(is_hidden=False)
        similar_longread_by_tags.tags.add('test')

        self._create_longreads(subject=None, is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal([similar_longread_by_subject, similar_longread_by_tags], result_longreads)

    def test_subject_and_category(self):
        """Материалов по сюжету не хватает, материалов по тегам нет, добавляются материалы по рубрике"""

        subject = G(Subject)
        category = G(Category)
        material = G(News, subject=subject, category=category, is_hidden=False, source_site=self.news_site)

        similar_longread_by_subject = self._create_longreads(subject=subject, is_hidden=False)
        similar_longread_by_rubric = self._create_longreads(category=category, is_hidden=False)
        self._create_longreads(subject=None, is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal([similar_longread_by_subject, similar_longread_by_rubric], result_longreads)

    def test_tags_and_category(self):
        """Материалов по сюжету нет, материалов по тегам не хватает, добавляются материалы по рубрике"""

        category = G(Category)
        material = G(Video, subject=None, category=category, is_hidden=False, source_site=self.news_site)
        material.tags.add('test')

        similar_longread_by_rubric = self._create_longreads(category=category, is_hidden=False)
        similar_longread_tags = self._create_longreads(is_hidden=False)
        similar_longread_tags.tags.add('test')
        self._create_longreads(subject=None, is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal([similar_longread_by_rubric, similar_longread_tags], result_longreads)

    def test_special_project(self):
        """Если материал из спецпроекта, то после сюжета и тегов проверяются похожие из спецпроекта"""

        project = G(Project)
        category = G(Category)
        material = G(Article, project=project, category=category, subject=None, is_hidden=False)
        similar_longreads = self._create_longreads(
            models=[Article, Photo, Infographic], project=project, is_hidden=False, n=3
        )
        self._create_longreads(category=category, is_hidden=False, n=2)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal(similar_longreads, result_longreads)

    def test_source_site(self):
        """Материалов по сюжету, тегам, рубрике нет, возвращаются материалы по основному разделу."""

        news_site = Site.objects.get(slugs='news')
        afisha_site = Site.objects.get(slugs='afisha')
        obed_site = Site.objects.get(slugs='obed')
        material = G(Article, source_site=afisha_site, sites=[news_site, afisha_site], subject=None, is_hidden=False)

        similar_longreads = self._create_longreads(
            source_site=afisha_site, sites=[news_site, afisha_site], is_hidden=False, n=2
        )
        self._create_longreads(source_site=obed_site, sites=[news_site, obed_site], is_hidden=False, n=2)

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal(similar_longreads, result_longreads)

    def test_hidden(self):
        """По умолчанию скрытые материалы не отображается"""

        subject = G(Subject)
        project = G(Project)
        category = G(Category)
        news_site = Site.objects.get(slugs='news')
        material = G(
            Photo, subject=subject, project=project, category=category, source_site=news_site, sites=[news_site],
            is_hidden=False
        )
        material.tags.add('test')

        similar_by_subject_hidden = self._create_longreads(subject=subject, is_hidden=True)
        similar_by_tags_hidden = self._create_longreads(is_hidden=True)
        similar_by_tags_hidden.tags.add('test')
        similar_by_project_hidden = self._create_longreads(
            models=[Article, Photo, Infographic], project=project, is_hidden=True
        )
        similar_by_rubric_hidden = self._create_longreads(category=category, is_hidden=True)
        similars_by_site = self._create_longreads(source_site=news_site, sites=[news_site], is_hidden=False, n=3)
        self._create_longreads(subject=None, is_hidden=False, n=3)

        smh = SimilarMaterialHelper(material, longreads_limit=4)
        result_longreads = smh.get_similar_longreads()

        # Похожие по сюжету, тегам, спецпроекту и рубрике пропущены т.к. они скрыты
        self._assert_materials_equal(similars_by_site, result_longreads)

        smh = SimilarMaterialHelper(material, show_hidden=True, longreads_limit=4)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal(
            [similar_by_subject_hidden, similar_by_tags_hidden, similar_by_project_hidden, similar_by_rubric_hidden],
            result_longreads
        )

    def test_duplicates(self):
        """В блоке не должно быть дубликатов материалов"""

        category = G(Category)
        material = G(Article, subject=None, category=category, is_hidden=False)
        material.tags.add('test')
        # Похожий материал и по сюжету и по категории
        similar_longread = self._create_longreads(category=category, is_hidden=False)
        similar_longread.tags.add('test')

        smh = SimilarMaterialHelper(material)
        result_longreads = smh.get_similar_longreads()

        self._assert_materials_equal([similar_longread], result_longreads)
        # Похожие материалы присутствует в блоке только один раз
        self.assertEqual(1, len(result_longreads))

    def _create_longreads(self, models=None, **kwargs):
        """
        Создание связанных лонгридов

        :param list models: список моделей для определия класса создаваемых лонгридов
        """

        if not models:
            models = [Article, Video, Photo, Infographic]

        model = random.choice(models)
        ct = ContentType.objects.get_for_model(model)

        stamp = datetime.datetime.now()
        kwargs.setdefault('stamp', stamp)

        return G(model, content_type=ct, **kwargs)

    def _assert_materials_equal(self, expected, actual):
        """
        Проверить, что элементы списков материалов совпадают.
        Проверка происходит по id и ContentType, так как в целях оптимизации, actual содержит Deferred Model

        :param list expected: ожидаемый список материалов
        :param list actual: актуальный список материалов
        """

        expected_ids = [(m.id, ContentType.objects.get_for_model(m)) for m in expected]
        actual_ids = [(m.id, ContentType.objects.get_for_model(m)) for m in actual]

        self.assertItemsEqual(expected_ids, actual_ids)

    def _assert_list_contains(self, sequence, subsequence):
        """
        Проверить, что все элементы subsequence присутствуют в sequence.
        Проверка происходит по id и ContentType, так как в целях оптимизации, объекты могут быть Deferred Model
        """

        sequence_ids = [(m.id, ContentType.objects.get_for_model(m)) for m in sequence]
        subsequence_ids = [(m.id, ContentType.objects.get_for_model(m)) for m in subsequence]

        self.assertListContains(sequence_ids, subsequence_ids)

    def _assert_list_not_contains(self, sequence, subsequence):
        """
        Проверить, что все элементы subsequence отсутствуют в sequence.
        Проверка происходит по id и ContentType, так как в целях оптимизации, объекты могут быть Deferred Model
        """

        sequence_ids = [(m.id, ContentType.objects.get_for_model(m)) for m in sequence]
        subsequence_ids = [(m.id, ContentType.objects.get_for_model(m)) for m in subsequence]

        self.assertListNotContains(sequence_ids, subsequence_ids)
