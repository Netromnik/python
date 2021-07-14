# -*- coding: utf-8 -*-

from __future__ import absolute_import

import unittest

from django.test import RequestFactory
import mock
import twitter
from vk.exceptions import VkException

from irk.tests.unit_base import UnitTestBase
from irk.utils.embed_widgets import InstagramEmbedWidget, TwitterEmbedWidget, VkVideoEmbedWidget
from irk.utils.helpers import seconds_to_text, get_client_ip, parse_email_date
from irk.utils.models import InstagramEmbed, TweetEmbed, VkVideoEmbed


class HelpersTest(UnitTestBase):

    def test_seconds_to_text(self):
        # 31536000 - год
        # 2592000 - месяц
        # 86400 день
        # 3600 - час
        # 60 - минута
        # 1 - секунда

        items = (
            (31536000, u'1 год'),
            (2592000, u'1 месяц'),
            (86400, u'1 день'),
            (3600, u'1 час'),
            (60, u'1 минуту'),
            (1, u'1 секунду'),
            (2 * 31536000, u'2 года'),
            (2 * 2592000, u'2 месяца'),
            (2 * 86400, u'2 дня'),
            (2 * 3600, u'2 часа'),
            (2 * 60, u'2 минуты'),
            (2 * 1, u'2 секунды'),
            (5 * 31536000, u'5 лет'),
            (5 * 2592000, u'5 месяцев'),
            (5 * 86400, u'5 дней'),
            (5 * 3600, u'5 часов'),
            (5 * 60, u'5 минут'),
            (5 * 1, u'5 секунд'),
            (2 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1,
             u'2 года 3 месяца 15 дней 23 часа 45 минут 1 секунду'),
            (3 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1,
             u'3 года 3 месяца', {'length': 2}),
            (2 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1,
             u'27 месяцев 25 дней 23 часа 45 минут', {'start': 1, 'end': 4}),  # +10 дней потому что 2 года
            (2 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1,
             u'27 месяцев', {'start': 1, 'length': 1}),
            (2 * 31536000 + 3 * 2592000 + 15 * 86400 + 23 * 3600 + 45 * 60 + 1,
             u'835 дней 23 часа', {'start': 2, 'length': 2}),  # +10 дней потому что 2 года
        )

        for item in items:
            kwargs = item[2] if len(item) == 3 else {}
            self.assertEqual(seconds_to_text(item[0], **kwargs), item[1])


class TwitterEmbedWidgetTest(UnitTestBase):
    """Тесты встраиваемого виджета Twitter"""

    def setUp(self):
        self.widget_class = TwitterEmbedWidget

    def test_find_links(self):
        """Проверка поиска ссылок на виджет. Дубликаты ссылок игнорируются"""

        expected_links = [
            'https://twitter.com/mod_russia/status/558464698712331265',
            'https://twitter.com/mod_russia/status/558465674952331265',
            'https://twitter.com/mod_russia/status/469875413524892154',
        ]
        content = u'''
            Рождество -- это таинственный праздник, мистический, глубокий и радостный одновременно. Сегодня никому не
            [card {0}]
            [b]Отец Андрей, настоятель Входоиерусалимского храма и храма Преображения Господня:[/b]
            [card {1}]
            Рождество стоит встречать в храме. Сообразно церковному уставу, с 1 января всю предрождественскую неделю у
            [card {2}]
            благочестивая традиция поститься до первой звезды, то есть до конца вечернего богослужения.
            [card {0}]
        '''.format(*expected_links)

        widget = self.widget_class(content)
        self.assertTrue(widget.exist())

        widget._find_links()
        self.assertItemsEqual(expected_links, widget._links)

    def test_get_entry_id(self):
        """Проверка получения идентификатора по ссылке"""

        widget = self.widget_class(content='')

        self.assertIsNone(widget.get_entry_id('https://twitter.com/mod_russia/status/'))
        self.assertEqual('558465674952331265',
                         widget.get_entry_id('https://twitter.com/mod_russia/status/558465674952331265'))
        self.assertEqual('558465674952331265',
                         widget.get_entry_id('https://twitter.com/mod_russia/status/558465674952331265/photos/1'))
        self.assertEqual('558465674952331265',
                         widget.get_entry_id('https://twitter.com/mod_russia/statuses/558465674952331265/'))

    @mock.patch('twitter.Api.GetStatusOembed')
    def test_parse_link(self, api_method):
        """Проверка обработки ссылки на виджет"""

        api_method.return_value = self.load_json_data('twitter.GetStatusOembed.json')

        self.assertFalse(TweetEmbed.objects.filter(pk=558465674952331265).exists())

        widget = self.widget_class(content='')
        widget._parse_link('https://twitter.com/mod_russia/status/558465674952331265')

        self.assertTrue(TweetEmbed.objects.filter(pk=558465674952331265).exists())

    @mock.patch('twitter.Api.GetStatusOembed')
    def test_parse_link_when_api_error(self, api_method):
        """Проверка обработки ссылки на виджет, когда api выдает ошибку"""

        api_method.side_effect = twitter.TwitterError('Oops')

        widget = self.widget_class(content='')

        self.assertIsNone(widget._parse_link('https://twitter.com/mod_russia/status/558465674952331265'))
        self.assertFalse(TweetEmbed.objects.filter(pk=558465674952331265).exists())


class InstagramEmbedWidgetTest(UnitTestBase):
    """Тесты встраиваемого виджета Instagram"""

    def setUp(self):
        self.widget_class = InstagramEmbedWidget

    def test_find_links(self):
        """Проверка поиска ссылок на виджет. Дубликаты ссылок игнорируются"""

        expected_links = [
            'https://www.instagram.com/p/Bb8e6uylkzp/',
            'https://www.instagram.com/p/Bb3x0U5Fzua',
            'https://www.instagram.com/p/Bby-dalFzSv/',
        ]
        content = u'''
            Рождество -- это таинственный праздник, мистический, глубокий и радостный одновременно. Сегодня никому не
            [card {0}]
            [b]Отец Андрей, настоятель Входоиерусалимского храма и храма Преображения Господня:[/b]
            [card {1}]
            Рождество стоит встречать в храме. Сообразно церковному уставу, с 1 января всю предрождественскую неделю у
            [card {2}]
            благочестивая традиция поститься до первой звезды, то есть до конца вечернего богослужения.
            [card {0}]
        '''.format(*expected_links)

        widget = self.widget_class(content)
        self.assertTrue(widget.exist())

        widget._find_links()
        self.assertItemsEqual(expected_links, widget._links)

    def test_get_entry_id(self):
        """Проверка получения идентификатора по ссылке"""

        widget = self.widget_class(content='')

        self.assertIsNone(widget.get_entry_id('https://www.instagram.com/developer/embedding/'))
        self.assertEqual(
            'Bb8e6uylkzp',
            widget.get_entry_id('https://www.instagram.com/p/Bb8e6uylkzp/')
        )
        self.assertEqual(
            'Bb3x0U5Fzua',
            widget.get_entry_id('https://www.instagram.com/p/Bb3x0U5Fzua/?taken-by=history_of_bouquets')
        )
        self.assertEqual(
            'fA9uwTtkSN',
            widget.get_entry_id('http://instagr.am/p/fA9uwTtkSN/')
        )

    @mock.patch('irk.utils.grabber.proxy_requests.get')
    def test_parse_link(self, request_get):
        """Проверка обработки ссылки на виджет"""

        request_get.json.return_value = self.load_json_data('instagram.oembed.json')

        self.assertFalse(InstagramEmbed.objects.filter(pk='BcBup4nl2tM').exists())

        widget = self.widget_class(content='')
        widget._parse_link('https://www.instagram.com/p/BcBup4nl2tM/')

        self.assertTrue(InstagramEmbed.objects.filter(pk='BcBup4nl2tM').exists())

    @unittest.skip('Broken. Trouble with mock object')
    @mock.patch('irk.utils.grabber.proxy_requests.get')
    def test_parse_link_when_api_error(self, request_get):
        """Проверка обработки ссылки на виджет, когда api выдает ошибку"""

        from requests.exceptions import RequestException

        request_get.side_effect = RequestException('Oops')

        widget = InstagramEmbedWidget(content='')

        self.assertFalse(InstagramEmbed.objects.filter(pk='BcBup4nl2tM').exists())
        self.assertIsNone(widget._parse_link('https://www.instagram.com/p/BcBup4nl2tM/'))
        self.assertFalse(InstagramEmbed.objects.filter(pk='BcBup4nl2tM').exists())


class VkVideoEmbedWidgetTest(UnitTestBase):
    """Тесты встраиваемого виджета видео из Вконтакта"""

    def setUp(self):
        self.widget_class = VkVideoEmbedWidget

    def test_find_links(self):
        """Проверка поиска ссылок на виджет. Дубликаты ссылок игнорируются"""

        expected_links = [
            'https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770',
            'https://vk.com/irkdtp?z=video-37432351_170996959%2Fvideos-37432351',

            # Видео из YouTube
            'https://vk.com/irkdtp?z=video42532654_171027491%2F5ba259f48c0b659557',
        ]
        content = u'''
            Рождество -- это таинственный праздник, мистический, глубокий и радостный одновременно. Сегодня никому не
            [video {0}]
            [b]Отец Андрей, настоятель Входоиерусалимского храма и храма Преображения Господня:[/b]
            [video {1}]
            Рождество стоит встречать в храме. Сообразно церковному уставу, с 1 января всю предрождественскую неделю у
            [video {2}]
            благочестивая традиция поститься до первой звезды, то есть до конца вечернего богослужения.
            [video {0}]
        '''.format(*expected_links)

        widget = self.widget_class(content)
        self.assertTrue(widget.exist())

        widget._find_links()
        self.assertItemsEqual(expected_links, widget._links)

    def test_get_entry_id(self):
        """Проверка получения идентификатора по ссылке"""

        widget = self.widget_class(content='')

        self.assertIsNone(widget.get_entry_id('https://vk.com/irkdtp?z=%2F825d1d1e72c2d97770'))
        self.assertEqual('-37432351_170996959',
                         widget.get_entry_id('https://vk.com/irkdtp?z=video-37432351_170996959%2Fvideos-37432351'))
        self.assertEqual('42532654_171027491',
                         widget.get_entry_id('https://vk.com/irkdtp?z=video42532654_171027491%2F5ba259f48c0b659557'))
        self.assertEqual('9685316_171125042',
                         widget.get_entry_id('https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770'))

    @mock.patch('irk.utils.embed_widgets.VkVideoEmbedWidget._get_api')
    def test_parse_link(self, get_api):
        """Проверка обработки ссылки на виджет"""

        kwargs = {'video.get.return_value': self.load_json_data('vk.video.get.user.json')}
        get_api.return_value = mock.Mock(**kwargs)

        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

        widget = self.widget_class(content='')
        widget._parse_link('https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770')

        self.assertTrue(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

    @mock.patch('irk.utils.embed_widgets.VkVideoEmbedWidget._get_api')
    def test_parse_link_when_video_not_found(self, get_api):
        """Проверка обработки ссылки на виджет, когда видео не найдено"""

        kwargs = {'video.get.return_value': self.load_json_data('vk.video.get.empty.json')}
        get_api.return_value = mock.Mock(**kwargs)

        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

        widget = self.widget_class(content='')

        self.assertIsNone(widget._parse_link('https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770'))
        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

    @mock.patch('irk.utils.embed_widgets.VkVideoEmbedWidget._get_api')
    def test_parse_link_when_api_error(self, get_api):
        """Проверка обработки ссылки на виджет, когда api выдает ошибку"""

        kwargs = {'video.get.side_effect': VkException('Oops')}
        get_api.return_value = mock.Mock(**kwargs)

        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

        widget = self.widget_class(content='')

        self.assertIsNone(widget._parse_link('https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770'))
        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

    @mock.patch('irk.utils.embed_widgets.VkVideoEmbedWidget._get_api')
    def test_parse_link_when_api_returned_invalid_json(self, get_api):
        """Проверка обработки ссылки на виджет, когда api возвращает недействительный json"""

        kwargs = {'video.get.return_value': self.load_json_data('vk.video.get.invalid.json')}
        get_api.return_value = mock.Mock(**kwargs)

        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())

        widget = self.widget_class(content='')

        self.assertIsNone(widget._parse_link('https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770'))
        self.assertFalse(VkVideoEmbed.objects.filter(pk='9685316_171125042').exists())


class GetClientIpTest(UnitTestBase):
    """Тесты функции get_client_ip"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_maiformed_input(self):
        # хакерский инпут в заголовке
        request = self.factory.get('/', HTTP_X_FORWARDED_FOR='\xf0\'\'\xf0""')
        self.assertEqual(get_client_ip(request), '127.0.0.1')


# pytest irk/utils/tests/unit/helpers.py -k parse_email
def test_parse_email_date():

    date = parse_email_date('Sat, 01 Feb 2020 09:06:22 +0800')
    assert date.timetuple()[:6] == (2020, 2, 1, 9, 6, 22)

    # работает корректировка зоны на Иркутск
    date = parse_email_date('Sat, 01 Feb 2020 08:06:22 +0700')
    assert date.timetuple()[:6] == (2020, 2, 1, 9, 6, 22)

    date = parse_email_date('Sat, 01 Feb 2020 09:06:22 +0800 (+08)')
    assert date.timetuple()[:6] == (2020, 2, 1, 9, 6, 22)

    date = parse_email_date('Sat, 01 Feb 2020 04:06:22 +0300 (MSK)')
    assert date.timetuple()[:6] == (2020, 2, 1, 9, 6, 22)
