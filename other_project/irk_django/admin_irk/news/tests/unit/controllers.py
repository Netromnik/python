# coding=utf-8
"""
Тесты для контроллера индекса новостей.
"""
import random

from django_dynamic_fixture import G

from irk.tests.unit_base import UnitTestBase
from irk.news.controllers import ArticleIndexController
from irk.news.models import ArticleIndex
from irk.news.tests.unit.material import create_material


class ArticleIndexControllerTest(UnitTestBase):
    """
    Тесты класса ArticleIndexController
    """
    def setUp(self):
        super(ArticleIndexControllerTest, self).setUp()
        self.controller = ArticleIndexController()

    def test_hello(self):
        """
        Контроллер хотя бы импортируется
        """
        controller = ArticleIndexController()
        self.assertIsNotNone(controller)

    def test_article_index_record_required(self):
        """
        Если в базе данных есть материал, но его нет в таблице ArticleIndex, то
        этот материал не появится в выдаче ленты статей
        """
        article = create_material('news', 'article', is_hidden=False, magazine=None)
        materials = list(self.controller.get_materials())
        self.assertEqual(materials, [])

    def test_article_index_record_exists(self):
        """
        Если есть запись ArticleIndex, то материал выведется
        """
        article = create_material('news', 'article', is_hidden=False, magazine=None)
        ai = G(ArticleIndex, material=article, is_super=False)

        print(ai.is_super)
        # ai = ArticleIndex.objects.create(material=article)

        materials = list(self.controller.get_materials())
        self.assertEqual(len(materials), 1)

    def test_article_index_supermaterial_doesnt_show(self):
        """
        Суперматериал не возвращаются в get_materials
        """
        article = create_material('news', 'article', is_hidden=False, magazine=None)
        G(ArticleIndex, material=article, is_super=True)

        materials = list(self.controller.get_materials())
        self.assertEqual(len(materials), 0)

    def test_hidden_materials_doesnt_show(self):
        """
        Скрытые материалы не возвращаются в get_materials
        """
        article = create_material('news', 'article', is_hidden=True, magazine=None)
        G(ArticleIndex, material=article, is_super=False)

        materials = list(self.controller.get_materials())
        self.assertEqual(len(materials), 0)

    def test_materials_sort(self):
        """
        Материалы сортируются в соответствии с position
        """
        article1 = create_material('news', 'article', is_hidden=False, magazine=None, title='1')
        article2 = create_material('news', 'article', is_hidden=False, magazine=None, title='2')

        G(ArticleIndex, material=article1, is_super=False, stick_position=None, position=190)
        G(ArticleIndex, material=article2, is_super=False, stick_position=None, position=200)

        materials = list(self.controller.get_materials())
        self.assertEqual(len(materials), 2)
        self.assertEqual(materials[0], article2)  # вторая статья выведется первой из-за большего сорта


class StickTest(UnitTestBase):
    """
    Тесты закреплений в ArticleIndexController
    """
    def setUp(self):
        super(StickTest, self).setUp()
        self.controller = ArticleIndexController()

        self.materials = []
        for i in range(5):
            a = create_material('news', 'article', is_hidden=False, magazine=None)
            G(ArticleIndex, material=a, is_super=False, stick_position=None, position=i)
            self.materials.append(a)

        self.materials.reverse()

    def test_stick(self):
        """Закрепленная статья выводится на закрепленном месте"""
        material = random.choice(self.materials)
        index = 0

        # stick
        self.controller.stick(material, index)
        lenta = self.controller.get_materials()
        self.assertEqual(lenta[index], material)
        self.assertEqual(lenta[index].article_index.stick_position, index)

        # unstick
        self.controller.stick(material, None)
        lenta = self.controller.get_materials()
        self.assertEqual(lenta[index].article_index.stick_position, None)

    def test_sticked_moves_after_new_materials_added(self):
        material = random.choice(self.materials)

        # закрепим на первом месте
        index = 0
        self.controller.stick(material, index)

        # add new material
        from datetime import datetime
        new_material = create_material('news', 'article', is_hidden=False, magazine=None, stamp=datetime.today(),
                                       published_time=None)
        self.controller.material_updated(new_material)

        lenta = self.controller.get_materials()
        self.assertEqual(len(lenta), len(self.materials)+1)
        self.assertEqual(lenta[index], material)

    def test_sticked_with_pagination(self):
        """
        Проверяет корректность пейджинации через [start:stop]
        """
        # создадим четыре материала
        items = []
        for i in xrange(4):
            a = create_material('news', 'article', is_hidden=False, magazine=None)
            ai = G(ArticleIndex, material=a, is_super=False, stick_position=None, position=10-i)
            items.append(a)

        # закрепим четвертый на месте №2
        self.controller.stick(items[3], 1)

        # в текущей реализации это поменяет местами 1 и 3
        # хотя было бы лучше 0 3 1 2
        items = [items[0], items[3], items[2], items[1]]

        # запросим и сверим все элементы
        materials = list(self.controller.get_materials(0, 4))
        self.assertEqual(materials, items)

        # и с пейджинацией - как будто вторую страницу
        materials = list(self.controller.get_materials(2, 4))
        self.assertEqual(materials, items[2:4])

        # пейджинация второй страницы, если закрепленный материал на первой
        controller = ArticleIndexController()
        materials = controller.get_materials(2, 4)
        self.assertEqual(materials[0].id, items[2:4][0].id)
        self.assertEqual(materials[1].id, items[2:4][1].id)

    def test_bug_almost_end_sticked(self):
        """
        Проверим, что если закреплено 20 материалов, а мы запрашиваем десять с
        девятнадцатого, то вернется корректно
        """
        # создадим 20 материалов
        items = []
        for i in xrange(20):
            a = create_material('news', 'article', is_hidden=False, magazine=None)
            ai = G(ArticleIndex, material=a, is_super=False, stick_position=None, position=10-i)
            items.append(ai)

        # закрепим десятый
        self.controller.stick(items[9].id, 1)

        controller = ArticleIndexController()
        materials = controller.get_materials(9, 15)
        self.assertEqual(len(materials), 6)
