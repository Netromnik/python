# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django_dynamic_fixture import G

from irk.blogs.models import BlogEntry
from irk.blogs.templatetags.blogs_tags import blog_sidebar_block
from irk.tests.unit_base import UnitTestBase


class BlogSidebarBlockTest(UnitTestBase):
    """ Теги блогов """

    def test_default(self):
        """
        По умолчанию отображается одна из трех последних записей в блогах. (Выбирается случайно)
        Запись блога должна быть видима и автор записи должен отображаться.
        """

        entry = G(BlogEntry, type=BlogEntry.TYPE_BLOG, visible=True)
        hidden_entries = G(BlogEntry, type=BlogEntry.TYPE_BLOG, visible=False, n=5)
        entries_with_hidden_author = G(BlogEntry, type=BlogEntry.TYPE_BLOG, visible=True, author__is_visible=False, n=5)

        result = blog_sidebar_block()['entries'][0]

        self.assertEqual(entry.id, result.id)

        # Невидимые не должны отображатся
        for e in hidden_entries:
            self.assertNotEqual(e.id, result.id)

        # Записи скрытого автора не должны отображатся
        for e in entries_with_hidden_author:
            self.assertNotEqual(e.id, result.id)

    def test_limit(self):
        """Параметр limit задает количество возвращаемых записей"""
        G(BlogEntry, type=BlogEntry.TYPE_BLOG, visible=True, n=4)

        result = blog_sidebar_block(limit=3)

        self.assertEqual(3, len(result['entries']))

    def test_when_not_entries(self):
        """Нет записей в блогах"""

        result = blog_sidebar_block(limit=1)

        self.assertEqual(0, len(result['entries']))

        result = blog_sidebar_block(limit=3)

        self.assertEqual(0, len(result['entries']))

    def test_when_entries_less_and_limit_1(self):
        """Случай когда записей мало и limit равен 1"""

        entries = G(BlogEntry, type=BlogEntry.TYPE_BLOG, visible=True, n=2)

        result = blog_sidebar_block(limit=1)['entries'][0]

        self.assertIn(result.id, [e.id for e in entries])
