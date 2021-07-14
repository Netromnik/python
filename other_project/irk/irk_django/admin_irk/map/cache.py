# -*- coding: utf-8 -*-

from irk.utils.cache import model_cache_key, invalidate_tags
from irk.afisha.cache import invalidate as afisha_invalidate


def invalidate(sender, **kwargs):
    """Протухание кэша карты"""

    from irk.map.models import Cities

    instance = kwargs.get('instance')

    tags = []

    # Для событий чистим кэширование по каждому событию отдельно
    if isinstance(instance, Cities):
        tags.append(model_cache_key(instance))
        afisha_invalidate(Cities, instance=instance)

    invalidate_tags(tags)
