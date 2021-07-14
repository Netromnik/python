# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.core.cache import cache

from irk.polls.cache import invalidate as poll_invalidate
from irk.utils.cache import invalidate_tags, model_cache_key

logger = logging.getLogger(__name__)


def invalidate(sender, **kwargs):
    """Протухание кэша для моделей раздела «Новости»"""

    from irk.news.models import (
        BaseMaterial, News, Article, Photo, Video, Subject, Flash, Live, LiveEntry, Infographic, Metamaterial, Podcast,
        Block, Position
    )
    from irk.contests.models import Contest
    from irk.experts.models import Expert
    from irk.polls.models import Poll
    from irk.testing.models import Test

    instance = kwargs.get('instance')

    tags_map = {
        Article: ['article', 'longread'],
        BaseMaterial: ['material', model_cache_key(instance)],
        Block: ['block'],
        Contest: ['contest', 'longread'],
        Expert: ['expert', 'experts', 'longread'],
        Flash: ['news-flash'],
        Infographic: ['infographic', 'longread'],
        Metamaterial: ['metamaterial', 'longread'],
        News: ['news'],
        Photo: ['photo', 'longread'],
        Podcast: ['podcast', 'longread'],
        Poll: ['poll', 'longread'],
        Position: ['position', 'block'],
        Subject: ['subjects'],
        Test: ['test'],
        Video: ['video', 'longread'],
    }

    tags = []

    for model in tags_map:
        if isinstance(instance, model):
            tags.extend(tags_map[model])

    if isinstance(instance, Poll):
        poll_invalidate(sender, **kwargs)

    if isinstance(instance, Live):
        logger.debug('Invalidating cache for live news #%d' % instance.id)
        tags.append(model_cache_key(instance.news))
        tags.append('news.rss.live.%s.yandex' % instance.id)
        cache.delete(model_cache_key(instance))

    if isinstance(instance, LiveEntry):
        logger.debug('Invalidating cache for live news #%d' % instance.live_id)
        tags.append(model_cache_key(instance.live.news))
        tags.append('news.rss.live.%s.yandex' % instance.live_id)
        cache.delete(model_cache_key(instance.live))

    invalidate_tags(tags)
