# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import re
import unicodedata

import twitter
import vk
from vk.exceptions import VkException

from django.conf import settings
from django.db import IntegrityError
from django.utils.functional import SimpleLazyObject

from irk.utils.grabber import proxy_requests
from irk.utils.models import InstagramEmbed, TweetEmbed, VkVideoEmbed

logger = logging.getLogger(__name__)


class BaseEmbedWidget(object):
    """
    Базовый класс для встраиваемых виджетов.

    Для каждого поддерживаемого виджета, нужно унаследовать этот класс и реализовать метод _parse_link()
    """

    # регулярное выражение для BB-кода виджета
    WIDGET_REGEX = None
    # регулярное выражение для поиска идентификатора записи в ссылке.
    # Индентификатор помечается именной групой id - например (?P<id>\d+)
    ENTRY_ID_REGEX = None
    # Признаки конкретного виджета в ссылке
    SIGNS = []

    def __init__(self, content):
        self._content = content
        self._links = []

    def exist(self):
        """
        Имеется ли виджет в контенте?

        :rtype: bool
        """

        self._find_links()
        return bool(self._links)

    def parse(self):
        """Найти и обработать все ссылки"""

        logger.debug('Start parsing links for embed widget')

        if not self._links:
            self._find_links()

        for link in self._links:
            self._parse_link(link)

        logger.debug('Finish parsing links for embed widget')

    def get_entry_id(self, link):
        """
        Получить ID записи из ссылки

        :param str link: ссылка
        :return: идентификатор записи, если он найден
        :rtype: str or None
        """

        match = self.ENTRY_ID_REGEX.search(link)
        if match:
            return match.groupdict()['id']

        return None

    def _find_links(self):
        """Поиск ссылок на встроенные виджеты"""

        logger.debug('Start find links')

        links = set()
        for link in self.WIDGET_REGEX.findall(self._content):
            if self.SIGNS:
                if any(sign in link for sign in self.SIGNS):
                    links.add(link)
            else:
                links.add(link)

        self._links = list(links)

        logger.debug('Finish find links. Found {} links'.format(len(self._links)))

    def _parse_link(self, link):
        """
        Обработать ссылку.
        Реализуется в наследниках.
        """

        raise NotImplementedError

    def _escape(self, value):
        """
        Очистить значение для сохранения в БД.
        На данный момент имеются проблемы с символами новой строки и смайлами в unicode.

        :param unicode value: строка содержащая символы Unicode
        :return: очищенная строка
        """

        value = value.replace('\n', '')

        output = []
        for ch in value:
            if unicodedata.category(ch)[0] in ['C']:
                continue
            output.append(ch)
        return u''.join(output)


class TwitterEmbedWidget(BaseEmbedWidget):
    """
    Встраиваемый виджет Twitter
    Ссылка на виджет в тексте представлена BB-кодом card.
    Пример использования в тексте: [card https://twitter.com/mod_russia/status/558465674952331265]
    Загруженный виджет сохраняется в модели `utils.models.TweetEmbed`.
    """

    WIDGET_REGEX = re.compile(ur'\[card (.*)\]')
    ENTRY_ID_REGEX = re.compile(ur'/status(?:es)?/(?P<id>\d+)')
    SIGNS = ['twitter.com']

    def __init__(self, content):
        super(TwitterEmbedWidget, self).__init__(content)

        self._api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )

    def _parse_link(self, link):
        """Обработать ссылку."""

        logger.debug('Start parse link: {}'.format(link))
        entry_id = self.get_entry_id(link)
        if not entry_id:
            logger.debug('Not found entry id in link: {}'.format(link))
            return

        # Для существующих виджетов, ничего не делаем.
        if TweetEmbed.objects.filter(pk=entry_id).exists():
            return

        try:
            response = self._api.GetStatusOembed(status_id=entry_id)
            # Очищаем html-код от символов новой строки, так как при выводе они печатаются как есть.
            html = self._escape(response['html'])
            TweetEmbed.objects.create(pk=entry_id, url=link, html=html)
            logger.debug('Successful created widget for link: {}'.format(link))
        except twitter.TwitterError:
            logger.exception('Twitter API error')
            return
        except IntegrityError:
            logger.exception("Can't created widget with pk: {}".format(entry_id))
            return

        logger.debug('Finish parse link: {}'.format(link))


class InstagramEmbedWidget(BaseEmbedWidget):
    """
    Встраиваемый виджет Instagram
    Ссылка на виджет в тексте представлена BB-кодом card.
    Примеры использования в тексте:
        [card https://www.instagram.com/p/BcBup4nl2tM/]
        [card https://www.instagram.com/tv/B4FElY1l7Hy/]
    Загруженный виджет сохраняется в модели `utils.models.InstagramEmbed`.
    """

    WIDGET_REGEX = re.compile(ur'\[card (.*)\]')
    ENTRY_ID_REGEX = re.compile(ur'/(?:p|tv)/(?P<id>[-\w]+)')
    SIGNS = ['instagram.com', 'instagr.am']
    EMBED_URL = 'https://graph.facebook.com/v9.0/instagram_oembed'

    def _parse_link(self, link):
        """Обработать ссылку."""

        logger.debug('Start parse link: {}'.format(link))

        entry_id = self.get_entry_id(link)
        if not entry_id:
            logger.debug('Not found entry id in link: %s', link)
            return

        # Для существующих виджетов, ничего не делаем.
        if InstagramEmbed.objects.filter(pk=entry_id).exists():
            return

        params = {
            'url': link,
            'access_token': settings.FACEBOOK_PAGE_ACCESS_TOKEN,
        }

        try:
            response = proxy_requests.get(self.EMBED_URL, params=params)
            response.raise_for_status()
            data = response.json()
            InstagramEmbed.objects.create(
                id=entry_id,
                url=link,
                html=self._escape(data.get('html', '')),
            )
            logger.debug('Successful created widget for link: %s', link)
        except proxy_requests.RequestException:
            logger.exception('Instagram API error')
            return
        except IntegrityError:
            logger.exception("Can't create widget with pk: %d", entry_id)
            return

        logger.debug('Finish parse link: {}'.format(link))


class VkVideoEmbedWidget(BaseEmbedWidget):
    """
    Встраиваемый виджет Vkontakte для видео
    Ссылка на виджет в тексте представлена BB-кодом video.
    Пример использования в тексте: [video https://vk.com/irkdtp?z=video9685316_171125042%2F825d1d1e72c2d97770]
    Загруженный виджет сохраняется в модели `utils.models.VkVideoEmbed`.
    """

    WIDGET_REGEX = re.compile(ur'\[video (.*)\]')
    ENTRY_ID_REGEX = re.compile(ur'video(?P<id>-?\d+_\d+)')
    SIGNS = ['vk.com', 'vkontakte.ru']

    def __init__(self, content):
        super(VkVideoEmbedWidget, self).__init__(content)

        # При создании объекта доступа к API происходит запрос к vk.com (Особенность библиотеки vk).
        # Оборачиваем объект доступа к API в LazyObject, чтобы избежать задержек при создании объекта виджета.
        self._api = SimpleLazyObject(lambda: self._get_api())

    @staticmethod
    def _get_api():
        """Получить объект для связи с api"""

        if hasattr(settings, 'VK_ACCESS_TOKEN'):
            session = vk.Session(access_token=settings.VK_ACCESS_TOKEN)
        else:
            session = vk.AuthSession(
                app_id=settings.VK_APP_ID,
                user_login=settings.VK_USER,
                user_password=settings.VK_PASSWORD,
                scope='video',
            )

        return vk.API(session, v='5.50')

    def _parse_link(self, link):
        """
        Обработать ссылку.

        Код виджета сохраняется в модели VkVideoEmbed
        """

        logger.debug('Start parse link: {}'.format(link))

        entry_id = self.get_entry_id(link)
        if not entry_id:
            logger.debug('Not found entry id in link: {}'.format(link))
            return

        # Для существующих виджетов, ничего не делаем.
        if VkVideoEmbed.objects.filter(pk=entry_id).exists():
            return

        try:
            response = self._api.video.get(videos=entry_id)
            html = response['items'][0]['player']
            VkVideoEmbed.objects.create(pk=entry_id, url=link, html=html)
            logger.debug('Successful created widget for link: {}'.format(link))
        except (VkException, KeyError):
            logger.exception('Vkontakte API error')
            return
        except IntegrityError:
            logger.exception("Can't created widget with pk: {}".format(entry_id))
            return
        except IndexError:
            # Видео не найдено
            logger.debug('Not found video for link'.format(link))
            return

        logger.debug('Finish parse link: {}'.format(link))


class EmbedWidgetParser(object):
    """Хелпер для обработки встроенных виджетов в тексте"""

    # Поддерживаемые виджеты
    EMBED_WIDGETS = [
        TwitterEmbedWidget,
        InstagramEmbedWidget,
        VkVideoEmbedWidget,
    ]

    def __init__(self, content):
        self._content = content
        self._widgets = []

    def parse(self):
        """Найти и обработать все встроенные виджеты"""

        logger.debug('Start parse embedded widgets')

        self._find_widgets()

        for widget in self._widgets:
            widget.parse()

        logger.debug('Finish parse embedded widgets')

    def _find_widgets(self):
        """Поиск встроенных виджетов"""

        logger.debug('Start find widgets')

        for widget_class in self.EMBED_WIDGETS:
            widget = widget_class(self._content)
            if widget.exist():
                self._widgets.append(widget)

        logger.debug('Finish find widgets. Found {} widgets'.format(len(self._widgets)))
