# -*- coding: utf-8 -*-

from __future__ import absolute_import

import mock
from django_dynamic_fixture import G, N

from irk.news.helpers.grabbers import FlashVideoPreviewGrabber, FlashFromVkGrabber
from irk.news.models import Flash
from irk.tests.unit_base import UnitTestBase


class FlashVideoPreviewGrabberTest(UnitTestBase):
    """Тесты для грабера превьюшек Народных новостей"""

    def setUp(self):
        self.grabber_class = FlashVideoPreviewGrabber

    def test_download_thumbnail(self):
        """Проверка загрузки превью для Народных новостей"""

        flash = G(Flash, title='TEST http://www.youtube.com/watch?v=7-vnBKP3fe8 TEST')
        grabber = self.grabber_class(flash)

        grabber.download_thumbnail()

        actual_flash = Flash.objects.get(pk=flash.pk)
        self.assertTrue(actual_flash.video_thumbnail)

    def test_parse_video_links(self):
        """Проверка обработки ссылок на видео YouTube в полях title и content"""

        flash_without_video = G(Flash)
        grabber = self.grabber_class(flash_without_video)
        self.assertFalse(grabber._parse_video_links())

        flash_with_video_in_title = N(Flash, title='TEST http://www.youtube.com/watch?v=7-vnBKP3fe8 TEST')
        grabber = self.grabber_class(flash_with_video_in_title)
        self.assertEqual('youtube.com/watch?v=7-vnBKP3fe8', grabber._parse_video_links()[0]['url'])
        self.assertIn('7-vnBKP3fe8', grabber._parse_video_links()[0]['id'])

        flash_with_video_in_title_short = N(Flash, title='TEST http://youtu.be/s11sqV99N5c TEST')
        grabber = self.grabber_class(flash_with_video_in_title_short)
        self.assertEqual('youtu.be/s11sqV99N5c', grabber._parse_video_links()[0]['url'])
        self.assertIn('s11sqV99N5c', grabber._parse_video_links()[0]['id'])

        flash_with_video_in_content = N(Flash, content='TEST http://www.youtube.com/watch?v=2oUWamm_T00 TEST')
        grabber = self.grabber_class(flash_with_video_in_content)
        self.assertEqual('youtube.com/watch?v=2oUWamm_T00', grabber._parse_video_links()[0]['url'])
        self.assertIn('2oUWamm_T00', grabber._parse_video_links()[0]['id'])

        flash_with_video_in_content_short = N(Flash, content='TEST http://youtu.be/_WaWbsOBTMQ TEST')
        grabber = self.grabber_class(flash_with_video_in_content_short)
        self.assertEqual('youtu.be/_WaWbsOBTMQ', grabber._parse_video_links()[0]['url'])
        self.assertIn('_WaWbsOBTMQ', grabber._parse_video_links()[0]['id'])

    def test_get_embed_url(self):
        """Получение ссылки на встраиваемое видео"""

        filename = '7-vnBKP3fe8.jpeg'
        expected_url = 'http://www.youtube.com/embed/7-vnBKP3fe8'

        flash = G(
            Flash, title='TEST http://www.youtube.com/watch?v=7-vnBKP3fe8 TEST', video_thumbnail=filename
        )
        grabber = self.grabber_class(flash)
        self.assertEqual(expected_url, grabber.get_embed_url())


class FlashFromVkGrabberTest(UnitTestBase):
    """Тесты грабера народных новостей из Вконтакта"""

    def setUp(self):
        parse_patcher = mock.patch('irk.utils.embed_widgets.VkVideoEmbedWidget.parse')
        self._parse = parse_patcher.start()
        self._parse.return_value = None
        self.addCleanup(parse_patcher.stop)

    @mock.patch('irk.irk.news.helpers.grabbers.FlashFromVkGrabber._get_api')
    def test_run(self, get_api):
        """
        Тестирование работы граббера.

        Тестовые данные.
        всего записей: 7
            с тегом #dtp: 3
            с тегом #дтп: 3 (2 с вложением)
            без тегов: 2
        из них:
            с видео: 1
            с фото: 5
            с документом (не обрабатывается): 1
        """

        kwargs = {'newsfeed.get.return_value': self.load_json_data('vk.newsfeed.get.json')}
        get_api.return_value = mock.Mock(**kwargs)

        self.assertFalse(Flash.objects.filter(type=Flash.VK_DTP).exists())

        grab = FlashFromVkGrabber()
        grab.run()

        self.assertTrue(Flash.objects.filter(type=Flash.VK_DTP).exists())

    def test_has_hashtags(self):
        """Наличие хэштегов в тексте новости"""

        grab = FlashFromVkGrabber()

        self.assertTrue(grab._has_hashtags(u'#dtp В субботу в березовом!'))
        self.assertTrue(grab._has_hashtags(u'На улице Костычева сегодня ночью. #DTP'))
        self.assertTrue(grab._has_hashtags(u'#ДТП на плотине ГЭС. \nВ 22:30 всё было ровно, через пять минут мясо'))
        self.assertTrue(grab._has_hashtags(u'Суббота ДТП перед мегаполисом 3 участника #ДТП'))
        self.assertTrue(grab._has_hashtags(u'Водитель пьяный, до этого #ДТП ещё что то снёс на култукской!!!'))
        self.assertTrue(grab._has_hashtags(u'http://www.youtube.com/watch?v=KQNh0CfTUso опять 80-е #Dtp'))
        self.assertFalse(grab._has_hashtags(u'Дтп дтп dtp Dtp'))
