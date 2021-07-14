# -*- coding: utf-8 -*-

import datetime
from django_dynamic_fixture import G

from irk.news.tests.unit.material import create_material
from irk.special.models import Project
from irk.tests.unit_base import UnitTestBase

from irk.home.controllers import ProjectController


class ProjectControllerTest(UnitTestBase):
    """Тесты контроллера спецпроектов"""

    def setUp(self):
        self.ctrl = ProjectController()

    def test_default(self):
        """Поведение по умолчанию"""

        # Должен отображаться
        create_material('news', 'metamaterial', is_special=True, show_on_home=True, is_hidden=False)
        # Не должен отображаться т.к. не является спецпроектом
        create_material('news', 'metamaterial', is_special=False, show_on_home=True, is_hidden=False)
        # Не должен отображаться т.к. не установлена галочка "отображать на главной"
        create_material('news', 'metamaterial', is_special=True, show_on_home=False, is_hidden=False)

        project1 = G(Project, show_on_home=True)
        create_material('news', 'article', project=project1, is_hidden=False, n=3)

        project2 = G(Project, show_on_home=True)
        create_material('news', 'article', project=project2, is_hidden=False, n=3)

        # Не отображается т.к. не установлена галочка "отображать на главной"
        project3 = G(Project, show_on_home=False)
        create_material('news', 'article', project=project3, is_hidden=False, n=4)

        items = self.ctrl.get_items()

        # 1 метаматериал и 2 проекта
        self.assertEqual(3, len(items))

    def test_sort(self):
        """
        Элементы сортируются по убыванию даты публикации

        У проектов за дату публикации берется дата самого свежего материала
        """

        meta1 = create_material(
            'news', 'metamaterial', is_special=True, show_on_home=True, is_hidden=False,
            stamp=datetime.date(2016, 1, 10)
        )
        meta2 = create_material(
            'news', 'metamaterial', is_special=True, show_on_home=True, is_hidden=False,
            stamp=datetime.date(2016, 1, 5)
        )

        project1 = G(Project, show_on_home=True)
        create_material('news', 'article', project=project1, is_hidden=False, stamp=datetime.date(2016, 1, 7))
        create_material('news', 'article', project=project1, is_hidden=False, stamp=datetime.date(2016, 1, 3))

        items = self.ctrl.get_items()

        self.assertListEqual([meta1, project1, meta2], items)

    def test_hidden(self):
        """Не отображать скрытые"""

        create_material('news', 'metamaterial', is_special=True, show_on_home=True, is_hidden=True)

        project1 = G(Project, show_on_home=True)
        create_material('news', 'article', project=project1, is_hidden=False, n=3)

        # Проекты в которых только скрытые материалы не отображаются
        project2 = G(Project, show_on_home=True)
        create_material('news', 'article', project=project2, is_hidden=True, n=3)

        items = self.ctrl.get_items()

        # 1 проект
        self.assertEqual(1, len(items))

    def test_get_views(self):
        """Генерация меток для предстваления элемента"""

        self.assertListEqual([], self.ctrl._get_views(-1))
        self.assertListEqual([], self.ctrl._get_views(0))
        self.assertListEqual(['double'], self.ctrl._get_views(1))
        self.assertListEqual(['single', 'single'], self.ctrl._get_views(2))
        self.assertListEqual(['single', 'single', 'double'], self.ctrl._get_views(3))
        self.assertListEqual(['single', 'single', 'single', 'single'], self.ctrl._get_views(4))
        self.assertListEqual(['single', 'single', 'double', 'single', 'single'], self.ctrl._get_views(5))
        self.assertListEqual(
            ['single', 'single', 'double', 'single', 'single', 'single', 'single'], self.ctrl._get_views(7)
        )
