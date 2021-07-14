# -*- coding: utf-8 -*-

import datetime
import imghdr
import logging
import re
import vk

from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from irk.gallery.models import Picture, GalleryPicture
from irk.news.helpers import logger
from irk.news.models import Flash
from irk.news.permissions import get_flash_moderators
from irk.news.signals import download_video_thumbnail
from irk.utils.embed_widgets import VkVideoEmbedWidget
from irk.utils.files import generate_file_name
from irk.utils.notifications import tpl_notify
from irk.utils.grabber import proxy_requests


class FlashVideoPreviewGrabber(object):
    """Грабер превью видео для народных новостей"""

    # регулярки для поиска ссылок на видео
    REGEX_PATTERNS = [
        # Standard YouTube
        re.compile(r'youtube\.com/watch\?v=(?P<id>[\w-]+)'),
        # Short YouTube
        re.compile(r'youtu\.be/(?P<id>[\w-]+)')
    ]

    # url с которого закачивается превью
    THUMBNAIL_URL = 'http://img.youtube.com/vi/{}/mqdefault.jpg'
    # url для встраиваемого видео
    EMBED_URL = 'http://www.youtube.com/embed/{}'

    def __init__(self, flash):
        self._flash = flash

    def download_thumbnail(self):
        """Загрузить превью видео"""

        self._disconnect_signals()

        video_links = self._parse_video_links()
        if not video_links:
            return None

        # Пока работаем только с первым видео
        link = video_links[0]
        thumbnail_url = self.THUMBNAIL_URL.format(link['id'])

        try:
            image = ContentFile(proxy_requests.get(thumbnail_url).content)
        except proxy_requests.HTTPError:
            logger.exception('Error download image for flash: {}'.format(self._flash.id))
            return

        extension = imghdr.what(image)
        self._flash.video_thumbnail.save('{}.{}'.format(link['id'], extension), image)

        self._reconnect_signals()

    def get_embed_url(self):
        """
        Вернуть url для встраиваемого видео

        url формируется на основе video_id содержащегося в имени файла.
        """

        if not self._flash.video_thumbnail:
            return ''

        try:
            video_link = self._parse_video_links()[0]
            return self.EMBED_URL.format(video_link['id'])
        except IndexError:
            return ''

    @staticmethod
    def _disconnect_signals():
        """Отключение сигналов"""

        # Отключаем сигнал, чтобы не войти в бесконечную рекурсию
        post_save.disconnect(download_video_thumbnail, sender=Flash)

    @staticmethod
    def _reconnect_signals():
        """Переподлкючение сигналов"""

        # Возвращаем обработчик сигнала
        post_save.connect(download_video_thumbnail, sender=Flash)

    def _parse_video_links(self, fields=('title', 'content')):
        """Определение ссылок на видео в полях народной новости"""

        video_links = []

        for pattern in self.REGEX_PATTERNS:
            for field_name in fields:
                field_value = getattr(self._flash, field_name, '')
                match = pattern.search(field_value)
                if match:
                    video_links.append({
                        'url': match.group(0),
                        'id': match.groupdict()['id']
                    })

        return video_links


class FlashFromVkGrabber(object):
    """Граббер постов из Вконтакта для Народных новостей"""

    # Идентификатор группы irkdtp
    GROUP_ID = -37432351
    # Количество загружаемых новостей
    POST_COUNT = 50
    # Будут сохранены только новости содержащие следующие хэштэги (через запятую)
    HASH_TAGS = [u'dtp', u'дтп']

    def __init__(self):
        self._api = None
        self._post_ids = set()
        self.FLASH_CT = ContentType.objects.get_for_model(Flash)

    def init(self):
        """Подготовка граббера к работе"""

        self._api = self._get_api()
        self._post_ids = set(Flash.objects.filter(type=Flash.VK_DTP).values_list('instance_id', flat=True))

    def run(self):
        """Запуск граббера"""

        logger.debug('Vkontakte grabber started')

        self.init()

        try:
            response = self._api.newsfeed.get(filters='post', source_ids=self.GROUP_ID, count=self.POST_COUNT)
        except proxy_requests.SSLError:
            logger.error('Vkontakte grabber failed')
            return

        posts = response.get('items', [])
        for post in posts:
            post_id = str(post['post_id'])
            if post_id not in self._post_ids and self._has_hashtags(post['text']):
                self._save(post)
                self._post_ids.add(post_id)

        logger.debug('Vkontakte grabber finished')

    def _get_api(self):
        """Получить объект для связи с api"""

        if hasattr(settings, 'VK_ACCESS_TOKEN'):
            session = vk.Session(access_token=settings.VK_ACCESS_TOKEN)
        else:
            session = vk.AuthSession(
                app_id=settings.VK_APP_ID,
                user_login=settings.VK_USER,
                user_password=settings.VK_PASSWORD,
                scope='wall,friends,video',
            )

        return vk.API(session, v='5.50')

    def _has_hashtags(self, text):
        """
        Проверить наличие в новости необходимых хэштегов

        :param str text: текст новости
        :rtype: bool
        """

        for tag in self.HASH_TAGS:
            if re.search(ur'#{}'.format(tag), text, flags=re.I | re.U):
                return True

        return False

    def _save(self, post):
        """
        Сохранить запись из Вконтакта в качестве народной новости.

        :param dict post: запись из Вконтакта
        """

        flash = Flash(
            type=Flash.VK_DTP,
            instance_id=post['post_id'],
            username='irkdtp',
            content=self._escape_text(post['text']),
            created=self._to_date(post['date']),
        )

        flash.save()

        if 'attachments' in post:
            self._save_attachments(post, flash)

        logging.debug('New vkontakte flash message with instance id {} created'.format(flash.instance_id))

        self._notify(flash)

    def _save_attachments(self, post, flash):
        """
        Сохранить вложения для записи.
        Сейчас поддерживаются видео и фотографии.

        :param dict post: запись из Вконтакта
        :param Flash flash: народная новость
        """

        gallery = flash.gallery.create(content_type=self.FLASH_CT, object_id=flash.pk)

        for attachment in post['attachments']:
            type_ = attachment['type']
            if type_ == 'photo':
                self._save_photo(attachment['photo'], gallery)
            elif type_ == 'video':
                self._save_video(attachment['video'], flash)
            else:
                logger.error(u'Unknown attachment type: {}'.format(type_))

    def _save_photo(self, photo, gallery):
        """
        Сохранить фото.

        :param dict photo: информация о фотографии
        :param Gallery gallery: галерея
        """

        picture = Picture.objects.create(
            title=photo['text'],
            date=self._to_date(photo['date']),
        )
        self._save_image(picture.image, photo)

        GalleryPicture.objects.create(gallery=gallery, picture=picture)
        logger.debug(u'Saved picture {} for flash {}'.format(picture.pk, gallery.parent_object.pk))

    def _save_video(self, video, flash):
        """
        Сохранить видео.
        Создается объект VkVideoEmbed для хранения html кода плеера с видео.
        В текст народной новости добавляется bb-код для вывода видео.

        :param dict video: информация о видео
        :param Flash flash: народная новость
        """

        video_url = u'http://vk.com/video{}_{}'.format(video['owner_id'], video['id'])

        # Добавляем ссылку на видео в текст новости
        flash.content += u'\n[video {}]'.format(video_url)
        flash.save()
        logger.debug(u'Add bb-code video for flash {}'.format(flash.pk))

        # Сохраняем превью видео для новости
        if not flash.video_thumbnail:
            self._save_image(flash.video_thumbnail, video)

        widget = VkVideoEmbedWidget(content=flash.content)
        widget.parse()

    def _save_image(self, field, attachment):
        """
        Скачать и сохранить изображение в поле типа Image.
        Выбирает изображение максимального размера.

        :param Image field: поле модели для хранения изображения
        :param dict attachment: информация о вложении
        """

        image = self._download(self._find_image_url(attachment))
        field.save(image.name, image)

    def _escape_text(self, text):
        """Обезопасить текст"""

        # Вырезаем "плохие" юникодные символы из текста
        # http://stackoverflow.com/questions/3220031/how-to-filter-or-replace-unicode-characters-that-would-take-more-than-3-bytes
        pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
        return pattern.sub(u'', text)

    def _to_date(self, timestamp):
        """Преобразовать unixtime в datetime"""

        return datetime.datetime.fromtimestamp(timestamp)

    def _notify(self, flash):
        """Отправить уведомление модераторам"""

        tpl_notify(
            u'Добавлена народная новость', 'news/notif/flash/add.html', {'instance': flash},
            emails=get_flash_moderators().values_list('email', flat=True)
        )

    def _find_image_url(self, attachment):
        """
        Найти url максимального изображения во вложении.

        Изображения представлены ключами вида photo_75, photo_130, photo_604, ..., где числом представлен размер
        картинки. Метод находит ключ представляющий изображение наибольшего размера.

        :param dict attachment: информация о вложении
        :return: url
        """

        keys = set()

        for key in attachment:
            if 'photo_' in key:
                keys.add(key)

        max_key = max(keys, key=lambda x: int(x.split('_')[1]))

        return attachment[max_key]

    def _download(self, url):
        """Загрузить ресурс"""

        try:
            response = proxy_requests.get(url)
        except proxy_requests.RequestException:
            logger.exception(u'Fail download resource from url {}'.format(url))
            return

        filename = generate_file_name(None, url)

        return ContentFile(response.content, name=filename)
