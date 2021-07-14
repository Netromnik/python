# -*- coding: utf-8 -*-

import datetime
import locale
import logging
import re
import time
import twitter

from django.conf import settings as global_settings
from django.core.management.base import BaseCommand

from irk.utils.notifications import tpl_notify

from irk.news import settings
from irk.news.models import Flash, FlashBlock
from irk.news.permissions import get_flash_moderators


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Граббер последних твитов"""

    def handle(self, *args, **options):

        logging.basicConfig(level=global_settings.LOGGING_LEVEL)
        logger.info('Twitter grabber started')
        locale.setlocale(locale.LC_ALL, 'C')

        if global_settings.PROXY_ENABLED and global_settings.PROXY:
            proxies = global_settings.PROXY
        else:
            proxies = None

        logger.debug('Proxies {}'.format(proxies))

        api = twitter.Api(
            consumer_key=global_settings.TWITTER_CONSUMER_KEY,
            consumer_secret=global_settings.TWITTER_CONSUMER_SECRET,
            access_token_key=global_settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=global_settings.TWITTER_ACCESS_TOKEN_SECRET,
            proxies=proxies,
        )
        try:
            since_id = Flash.objects.filter(type=Flash.TWITTER).order_by('-created')[0].instance_id
        except IndexError:
            since_id = None

        tweets = api.GetSearch(term=' OR '.join(settings.TWITTER_SEARCH_KEYWORDS),
                               count=100,
                               result_type='recent',
                               since_id=since_id)

        if not tweets:
            logger.info('Results are not available')

        for tweet in tweets:
            try:
                Flash.objects.get(instance_id=tweet.id)
            except Flash.DoesNotExist:
                # Убираем ретвиты
                # TODO: может есть более логичные варианты проверки на ретвит?
                if tweet.text.startswith('RT '):
                    continue

                block_cnt = FlashBlock.objects.filter(pattern=tweet.user.screen_name).count()
                if block_cnt > 0:
                    # Автор твита заблокирован
                    continue

                date = time.strptime(tweet.created_at, '%a %b %d %H:%M:%S +0000 %Y')[0:6]

                # На случай проблем с часовым поясом, чтобы не оказаться в будущем
                created = min(datetime.datetime(*date[0:6]) + datetime.timedelta(hours=8), datetime.datetime.now())

                # Вырезаем "плохие" юникодные символы из текста
                # http://stackoverflow.com/questions/3220031/how-to-filter-or-replace-unicode-characters-that-would-take-more-than-3-bytes
                pattern = re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)
                text = pattern.sub(u'', tweet.text)

                flash = Flash(instance_id=tweet.id, username=tweet.user.screen_name, type=Flash.TWITTER,
                              content=text, created=created)
                flash.save()

                logger.debug('New twitter flash message with instance id %s created' % tweet.id)

                tpl_notify(u'Добавлена народная новость', 'news/notif/flash/add.html', {'instance': flash},
                           emails=get_flash_moderators().values_list('email', flat=True))
            else:
                logger.debug('Message with instance id %s already exists in database' % tweet.id)
                continue

        logger.info('Twitter grabber ended')
