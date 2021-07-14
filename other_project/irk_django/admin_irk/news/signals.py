# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from irk.utils.cache import invalidate_tags

logger = logging.getLogger(__name__)


def live_cache(sender, instance, **kwargs):
    from irk.news.models import Live, LiveEntry

    if isinstance(instance, Live):
        key = 'news.live.%s' % instance.pk
    elif isinstance(instance, LiveEntry):
        key = 'news.live.%s' % instance.live_id

    invalidate_tags([key, ])


def download_video_thumbnail(sender, instance, **kwargs):
    """Загрузка превью видео при сохранении модели Народные новости"""

    from irk.news.tasks import download_video_thumbnail_for_flash

    download_video_thumbnail_for_flash.delay(instance.pk)


def tilda_article_post_delete(sender, instance, **kwargs):
    """Удаляет файлы Тильды"""
    if instance.archive:
        instance.delete_extracted()
        instance.archive.delete(save=False)


def tilda_article_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        old_file = old_instance.archive
    except sender.DoesNotExist:
        return False

    new_file = instance.archive
    if old_file and old_file != new_file:
        old_instance.delete_extracted()
        old_file.delete(save=False)
