# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand

from irk.comments.permissions import get_moderators
from irk.utils.notifications import tpl_notify

from irk.externals.management.grabbers.instagram import load_media_by_hashtag
from irk.externals.models import InstagramTag, InstagramMedia, InstagramUserBlacklist

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''\
        Грабинг фоток из инстаграмма.

        Собираются фотки с тегами привязанными к разделу Погода.
    '''

    def handle(self, **options):
        logger.debug('Start grabbing instagram')

        blocked_users = set(InstagramUserBlacklist.objects.values_list('username', flat=True))

        new_posts = set()
        for tag in InstagramTag.objects.filter(is_visible=True):
            logger.debug('Downloading pictures by #{}'.format(tag.name))
            last_id = None
            for post in load_media_by_hashtag(tag.name, tag.latest_media_id):
                logger.debug('Processing post {}'.format(post['id']))
                # Список постов идет от самых новых к более старым, поэтому последним (новейшим) постом
                # будет 1й элемент в списке.
                if not last_id:
                    last_id = post['id']

                if post['user']['username'] in blocked_users:
                    continue

                is_new = False
                try:
                    media = InstagramMedia.objects.get(instagram_id=post['id'])
                except InstagramMedia.DoesNotExist:
                    media = InstagramMedia(instagram_id=post['id'])
                    is_new = True
                    # В погоде действует премодерация
                    if tag.site and tag.site.slugs == 'weather':
                        media.is_visible = False

                media.data = post
                media.save()
                logger.debug('Saved media {}'.format(media.id))
                media.tags.add(tag)

                if is_new:
                    new_posts.add(media)

            if last_id:
                tag.latest_media_id = last_id
            tag.save()
            logger.debug('Finish download pictures by #{}'.format(tag.name))

        if new_posts:
            logger.debug('Sending notification for moderators')
            tpl_notify(
                u'Новые фотки в ленте инстаграмма в погоде',
                'externals/notif/new_instagram_post.html',
                {'posts': new_posts},
                emails=get_moderators().values_list('email', flat=True)
            )

        logger.debug('Finish grabbing instagram')
