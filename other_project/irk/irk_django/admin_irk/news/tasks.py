# -*- coding: utf-8 -*-

"""Задачи celery"""

import imghdr
import logging
import os
import re

from django.conf import settings
from django.core.files.base import ContentFile

from irk.news.controllers.socials.posting import SocialPosterError, get_poster_by_name
from irk.news.helpers import MaterialController
from irk.news.helpers.grabbers import FlashVideoPreviewGrabber
from irk.uploads.models import Upload
from irk.utils.embed_widgets import EmbedWidgetParser
from irk.utils.grabber import proxy_requests
from irk.utils.helpers import get_object_or_none
from irk.utils.tasks.helpers import make_command_task, task

logger = logging.getLogger(__name__)


news_twitter_grabber = make_command_task('news_twitter_grabber')

news_irkdtp_grabber = make_command_task('news_irkdtp_grabber')

news_send_daily_distribution = make_command_task('news_send_daily_distribution')
news_send_weekly_distribution = make_command_task('news_send_weekly_distribution')

news_articles_paid_unset = make_command_task('news_articles_paid_unset')

news_disable_comments = make_command_task('news_disable_comments')

news_coin_grabber = make_command_task('news_coin_grabber')

news_publish_scheduled = make_command_task('news_publish_scheduled')


@task(max_retries=1, ignore_result=True)
def live_entry_image_save(entry_id):
    """Сохранение картинок из записей в онлайн-репортажи новостей

    Текст парсится на наличие ссылок на картинки, которые скачиваются и потом ресайзятся

    В entry_id передается id записи
    """

    from irk.news.models import LiveEntry

    entry = LiveEntry.objects.get(pk=entry_id)
    text = entry.text

    for match in re.findall(ur'(\[image\s+(\S+)(\s+(left|center|right))?\])', text) or ():
        whole, url, _, align = match
        if url.isdigit():
            continue
        try:
            image = ContentFile(proxy_requests.get(url).content)
        except proxy_requests.HTTPError:
            image = None
        extension = imghdr.what(image)
        upload = Upload()
        upload.file.save('%s.%s' % (os.path.basename(url), extension), image)
        upload.save()

        if upload.is_image:
            result_url = upload.file.path.replace(settings.MEDIA_ROOT, '')
            text = text.replace(url, result_url)

            logger.debug('Replacing external URI %s with local %s in the live news entry' % (url, result_url))

        else:
            text = text.replace(whole, '')

    entry.text = text
    entry.save()


@task(ignore_result=True, max_retries=3, default_retry_delay=60)
def pregenerate_cache(debug_info=None):
    """Прегенерация списка новостей на главной раздела"""

    mc = MaterialController()
    mc.pregenerate_cache()


@task(ignore_result=True)
def download_video_thumbnail_for_flash(flash_id):
    """Задача для загрузки превью видео у Народной новости"""

    logger.debug('Start download video thumbnail for flash {}'.format(flash_id))

    from irk.news.models import Flash

    flash = get_object_or_none(Flash, pk=flash_id)
    if not flash:
        logger.error('Not found flash with id: {}'.format(flash_id))
        return

    # Для новостей из Вконтакта, превью заполняется через API
    if flash.is_vk_dtp:
        logger.debug('Skip flash from vk')
        return

    grabber = FlashVideoPreviewGrabber(flash)
    grabber.download_thumbnail()

    logger.debug('Finish download video thumbnail for flash {}'.format(flash_id))


@task(ignore_result=True)
def parse_embedded_widgets(content):
    """
    Обработка встраиваемых виджетов в тексте (Твиттер и другие)
    Обрабатывается поле content.

    :param str content: текст содержащий встраиваемые виджеты
    """

    parser = EmbedWidgetParser(content)
    parser.parse()


@task
def social_post_task(alias, material_id, social_post_id=None, data=None):
    """
    Задача размещения материала в социальных сетях
    """
    logger.info('Starting social_post_task, alias=%s, mid=%s, socpost_id=%s',
                alias, material_id, social_post_id)
    from irk.news.models import BaseMaterial, SocialPost

    material = BaseMaterial.objects.filter(id=material_id).first()
    if not material:
        logger.error('Not found material with id {}'.format(material_id))
        raise Exception('Not found material with id {}'.format(material_id))

    # обновим задачу для соцпульта
    try:
        post = SocialPost.objects.get(pk=social_post_id)
    except SocialPost.DoesNotExist:
        post = SocialPost()

    post.material = material
    post.network = alias

    try:
        poster = get_poster_by_name(alias)
        result = poster.post(material.cast(), data)
    except SocialPosterError as err:
        logger.error(err)
        post.status = 'error'
        post.error = str(err)
        raise  # сначала выполнится finally, а потом эта инструкция
    else:
        post.status = 'published'
        post.response = result.as_string()
        post.link = result.url()
    finally:
        post.save()

    logger.debug('Posting result: %r', result)
    logger.info('Social post task done, id=%s', post.id)


@task(ignore_result=True)
def social_refresh_cache(material_id):
    """Задача сброса кэша социальных сетей для материала"""

    from irk.news.models import BaseMaterial
    material = BaseMaterial.objects.filter(id=material_id).first()
    if not material:
        logger.error('Not found material with id {}'.format(material_id))
        raise Exception('Not found material with id {}'.format(material_id))

    for provider in ['vk', 'facebook']:
        poster = get_poster_by_name(provider)
        poster.refresh_cache(material)

    logger.info('Social caches are refreshed successful')
