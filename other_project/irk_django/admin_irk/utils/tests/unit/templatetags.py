# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest
from datetime import datetime, timedelta

from django_dynamic_fixture import G
from freezegun import freeze_time
from lxml.html import fromstring as html_fromstring

from django.contrib.staticfiles.finders import find
from django.core.files import File as DjangoFile
from django.template import Context, Template

from irk.gallery.models import GalleryPicture, Picture
from irk.tests.unit_base import UnitTestBase
from irk.utils.templatetags.date_tags import pretty_date
from irk.utils.templatetags.str_utils import has_bb_code, truncatechars_until_sentence, truncatesentences


class DateTagsTest(UnitTestBase):

    @freeze_time('2014-01-04 00:01')
    def test_pretty_date(self):
        now = datetime.now()

        # timestamp, short format, full format
        date_results = (
            (now, u'сегодня', u'менее минуты назад'),  # 2014-01-04 00:01:00
            (now - timedelta(seconds=5), u'сегодня', u'менее минуты назад'),  # 2014-01-04 00:00:55
            (now - timedelta(minutes=1, seconds=1), u'вчера', u'минуту назад'),  # 2014-01-03 23:59:59
            (now - timedelta(minutes=5), u'вчера', u'5 минут назад'),  # 2014-01-03 23:56:00
            (now - timedelta(hours=5), u'вчера', u'5 часов назад'),  # 2014-01-03 19:01:00
            (now - timedelta(days=1), u'вчера', u'вчера'),  # 2014-01-03 00:01:00
            (now - timedelta(days=2), u'2 января', u'позавчера'),  # 2014-01-02 00:01:00
            (now - timedelta(days=3), u'1 января', u'01.01'),  # 2014-01-01 00:01:00
            (now - timedelta(days=32), u'3 декабря 2013', u'03.12.2013'),  # 2013-11-30 00:01:00
        )

        for date_result in date_results:
            self.assertEqual(pretty_date(date_result[0], 'short'), date_result[1], 'Trying {}'.format(date_result[0]))
            self.assertEqual(pretty_date(date_result[0], 'full'), date_result[2], 'Trying {}'.format(date_result[0]))


class StrUtilsTest(UnitTestBase):

    @unittest.skipIf(True, '')
    def test_truncatesentences(self):
        sentences = [u'Автором скульптуры стал И. И. Иванов и к.o.',
                     u'Иванов И. И. автором скульптуры т.е., стал по статье 20.8 КоАП.',
                     u'И.И. Иванов автором (www.irk.ru) скульптуры стал.',
                     u'Автором скульптуры Иванов И.И. стал.',
                     u'Автором скульптуры стал Иванов И.И.',
                     u'Автором скульптуры стал Иванов И.И.',
                     u'Автором скульптуры Иванов И.И. стал.']

        text = u' '.join(sentences)

        self.assertEqual(truncatesentences(text, 1), u' '.join(sentences[:1]))
        self.assertEqual(truncatesentences(text, 2), u' '.join(sentences[:2]))
        self.assertEqual(truncatesentences(text, 3), u' '.join(sentences[:3]))
        self.assertEqual(truncatesentences(text, 4), u' '.join(sentences[:4]))
        self.assertEqual(truncatesentences(text, 5), u' '.join(sentences[:5]))
        self.assertEqual(truncatesentences(text, 6), u' '.join(sentences[:6]))

    def test_truncatechars_until_sentence(self):
        """Обрезка строки по символам с учетом предложений."""

        text = u'Борода глазам не замена. Без копейки рубля нет. Прытче зайца не будешь, а и того ловят.'

        self.assertEqual(u'Борода глазам не замена.', truncatechars_until_sentence(text, 30))
        self.assertEqual(u'Борода глазам не замена. Без копейки рубля нет.', truncatechars_until_sentence(text, 60))
        self.assertEqual(u'Борода глазам не замена.', truncatechars_until_sentence(text, 24))
        self.assertEqual(u'Борода глазам не замена.', truncatechars_until_sentence(text, 20))
        self.assertEqual(u'Борода глазам не замена.', truncatechars_until_sentence(text, 46))
        self.assertEqual(u'', truncatechars_until_sentence('', 10))
    
    def test_truncatechars_until_sentence2(self):
        """Обрезка строки по символам с учетом предложений.
        Дополнительный тест с вопросительными и восклицательными придложениями"""

        text = u'Борода? Замена! Без копейки рубля нет.'

        self.assertEqual(u'Борода? Замена!', truncatechars_until_sentence(text, 20))
        self.assertEqual(u'Борода? Замена! Без копейки рубля нет.', truncatechars_until_sentence(text, 60))
        self.assertEqual(u'Борода? Замена!', truncatechars_until_sentence(text, 16))
        self.assertEqual(u'Борода? Замена!', truncatechars_until_sentence(text, 15))

        self.assertEqual(truncatechars_until_sentence(u'Привет!', 1), u'Привет!')
        self.assertEqual(truncatechars_until_sentence(u'Привет', 1), u'Привет')
        self.assertEqual(truncatechars_until_sentence(u'Привет.', 6), u'Привет.')
        self.assertEqual(truncatechars_until_sentence(u'Привет. Это Вася', 1), u'Привет.')
        self.assertEqual(truncatechars_until_sentence(u'Привет. Это Вася', 10), u'Привет.')
        self.assertEqual(truncatechars_until_sentence(u'Привет. Это Вася. Кот? ', 50), u'Привет. Это Вася. Кот? ')
        self.assertEqual(truncatechars_until_sentence(u'два  пробела', 1), u'два  пробела')


class TypografTemplateTagTest(UnitTestBase):
    """Тесты для шаблонного тега typograf"""

    def test_default(self):
        """Использование типографа без параметров"""
        template = Template('''{% load str_utils %}{{ object|typograf }}''')

        self.assertEqual('Test Text', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('Test &lt;b&gt;Text&lt;/b&gt;', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_title(self):
        """Использование типографа с параметром title"""
        template = Template('''{% load str_utils %}{{ object|typograf:"title" }}''')

        self.assertEqual('Test Text', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('Test &lt;b&gt;Text&lt;/b&gt;', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_title_with_safe(self):
        """Использование типографа с параметром title и фильтром safe"""
        template = Template('''{% load str_utils %}{{ object|typograf:"title"|safe }}''')

        self.assertEqual('Test Text', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('Test &lt;b&gt;Text&lt;/b&gt;', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_title_with_double_safe(self):
        """Использование типографа с параметром title и применением фильтра safe дважды"""
        template = Template('''{% load str_utils %}{{ object|typograf:"title"|safe|safe }}''')

        self.assertEqual('Test Text', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('Test &lt;b&gt;Text&lt;/b&gt;', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_admin(self):
        """Использование типографа с параметром admin"""
        template = Template('''{% load str_utils %}{{ object|typograf:"admin" }}''')

        self.assertEqual('<p>Test Text</p>', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('<p>Test <b>Text</b></p>', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_admin_with_safe(self):
        """Использование типографа с параметром admin и фильтром safe"""
        template = Template('''{% load str_utils %}{{ object|typograf:"admin"|safe }}''')

        self.assertEqual('<p>Test Text</p>', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('<p>Test <b>Text</b></p>', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_user(self):
        """Использование типографа с параметром user"""
        template = Template('''{% load str_utils %}{{ object|typograf:"user" }}''')

        self.assertEqual('<p>Test Text</p>', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('<p>Test &lt;b&gt;Text&lt;/b&gt;</p>', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_user_with_safe(self):
        """Использование типографа с параметром user и фильтром safe"""
        template = Template('''{% load str_utils %}{{ object|typograf:"user"|safe }}''')

        self.assertEqual('<p>Test Text</p>', self._render(template, {'object': 'Test Text'}))
        self.assertEqual('<p>Test &lt;b&gt;Text&lt;/b&gt;</p>', self._render(template, {'object': 'Test <b>Text</b>'}))

    def test_image_crop(self):
        gp = self.create_picture()
        template = Template('{% load str_utils %}{{ content|typograf:"admin,image=100x100" }}')

        result = self._render(template, {'content': '[image {0.id}]'.format(gp)})
        html = html_fromstring(result)
        elem = html.find('img')
        # self.assertEqual('100px', elem.get('width'))
        # self.assertEqual('100px', elem.get('height'))

    def test_image_stretch(self):
        gp = self.create_picture()
        template = Template('{% load str_utils %}{{ content|typograf:"admin,image=500x500xstretch" }}')

        result = self._render(template, {'content': '[image {0.id}]'.format(gp)})
        html = html_fromstring(result)
        elem = html.find('img')
        # self.assertEqual('500px', elem.get('width'))
        # self.assertEqual('500px', elem.get('height'))

    def test_image_scalable(self):
        gp = self.create_picture()
        template = Template('{% load str_utils %}{{ content|typograf:"admin,image=100x100xscalable" }}')

        result = self._render(template, {'content': '[image {0.id}]'.format(gp)})
        html = html_fromstring(result)
        elem = html.find('img')
        # self.assertEqual('100px', elem.get('width'))
        # self.assertEqual('100px', elem.get('height'))
        # self.assertEqual('150', elem.get('data-single-layer-width'))
        # self.assertEqual('150', elem.get('data-single-layer-height'))

    def _render(self, template, context):
        return template.render(Context(context))

    def create_picture(self):
        image = DjangoFile(open(find('img/irkru.png')))
        picture = G(Picture, image=image)

        return G(GalleryPicture, picture=picture)


class HasBBCodeFilterTest(UnitTestBase):
    """Тесты шаблонного фильтра has_bb_code"""

    def test_default(self):
        self.assertTrue(has_bb_code('No matter [diff 123,321]', 'diff'))
        self.assertFalse(has_bb_code('No matter [diff 123,321]', 'video'))
        self.assertFalse(has_bb_code('No matter [video http://ya.ru] pass', 'video diff'))
        self.assertTrue(has_bb_code('No matter [video http://ya.ru] pass [diff 123,321]', 'video diff'))
        self.assertTrue(has_bb_code('No matter [video http://ya.ru] pass [diff 123,321]', 'video,diff'))
        self.assertTrue(has_bb_code('No matter [video http://ya.ru] pass [diff 123,321]', 'video, diff'))
        self.assertTrue(has_bb_code('No matter [video http://ya.ru] pass [diff 123,321]', 'video,  ,  diff'))
