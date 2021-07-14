# -*- coding: utf-8 -*-

import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.cache import cache

from irk.news.feeds.yandex import YandexLiveFeed
from irk.news.models import Live


logger = logging.getLogger(__name__)


def update(request, live_id):
    """Обновление контента онлайн-трансляции через ajax"""

    response = cache.get('news.live.%s' % live_id)
    if not response:
        live = get_object_or_404(Live, pk=live_id)
        logger.debug('Regenerating cache for news live entry #%d' % live.id)

        response = render_to_string('news/snippets/live_table_content.html',
                                    {'entries': live.entries.all().order_by('-date', '-created')})
        cache.set('news.live.%s' % live.pk, response, 60 * 10)
    else:
        logger.debug('Cache exists for live news #%s' % live_id)

    return HttpResponse(response)


def feed(request, live_id):
    """RSS для Яндекс.новостей"""

    live = get_object_or_404(Live, pk=live_id)

    key = 'news.rss.live.%s.yandex' % live.pk
    content = cache.get(key)
    if not content:
        content = YandexLiveFeed(live).writeString('utf-8')
        cache.set(key, content, 600)

    return HttpResponse(content, content_type='application/rss+xml')
