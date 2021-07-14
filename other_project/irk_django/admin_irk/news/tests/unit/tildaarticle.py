# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import StringIO
import zipfile
from django_dynamic_fixture import G, N

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from irk.options.models import Site
from irk.tests.unit_base import UnitTestBase

from irk.news.forms import TildaArticleAdminForm
from irk.news.models import Article, Category, TildaArticle
from irk.news.tests.unit.material import create_material


class TildaArticleTest(UnitTestBase):
    """Тесты Тильдовских статей"""

    def setUp(self):
        super(TildaArticleTest, self).setUp()
        self.date = datetime.date.today()
        self.admin = self.create_user('admin', '123', is_admin=True)
        self.site = Site.objects.get(slugs='news')

    def test_get_material_url(self):
        """Обратный юрл работает"""

        # article = create_material('news', 'tildaarticle', slug='test', stamp=datetime.date(2019, 8, 7))
        # print(article)
        # self.assertEqual('/news/article/20190807/testd/', str(article.get_absolute_url()))

    def test_tilda_extract_root(self):
        """
        Функции extract_root и extract_url работают правильно
        """
        article = TildaArticle()
        self.assertIsNone(article.tilda_extract_root)
        self.assertIsNone(article.tilda_extract_url)

        class FakeFile(object):
            path = '/any/path/0x0x'
        article.archive = FakeFile()

        with self.settings(MEDIA_ROOT='/mediaroot/'):
            self.assertRegexpMatches(article.tilda_extract_root, '/mediaroot/img/site/news/tilda/\d+/0x0x/')

        with self.settings(MEDIA_URL='/media/'):
            self.assertRegexpMatches(article.tilda_extract_url, '/media/img/site/news/tilda/\d+/0x0x/')


class TildaArticleAdminFormTest(UnitTestBase):
    def setUp(self):
        self.form = TildaArticleAdminForm()
        self.valid_archive = self._valid_zip()
        self.text_file = StringIO.StringIO(b'content')

    def _valid_zip(self):
        return StringIO.StringIO('PK\x05\x06' + '\x00'*18)

    def test_archive_false_pass(self):
        # значение false (очистить поле) проходит без проблем
        self.form.cleaned_data = {'archive': False}
        self.assertEqual(self.form.clean_archive(), False)

    def test_valid_archive(self):
        self.form.cleaned_data = {'archive': self.valid_archive}
        self.assertEqual(self.form.clean_archive(), self.valid_archive)

    def test_invalid_file(self):
        self.form.cleaned_data = {'archive': self.text_file}

        with self.assertRaises(ValidationError):
            self.form.clean_archive()

