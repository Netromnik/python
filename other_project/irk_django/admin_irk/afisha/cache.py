# -*- coding: utf-8 -*-

from irk.utils.cache import model_cache_key, invalidate_tags


def invalidate(sender, **kwargs):
    """Протухание кэша афиши"""

    from irk.afisha.models import Event

    instance = kwargs.get('instance')
    tags = []

    # Для событий чистим кэширование по каждому событию отдельно
    if isinstance(instance, Event):
        tags.append('afisha')
        tags.append(model_cache_key(instance))

    invalidate_tags(tags)
