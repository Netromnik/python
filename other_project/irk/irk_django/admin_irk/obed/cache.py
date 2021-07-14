# -*- coding: utf-8 -*-


from irk.utils.cache import model_cache_key, invalidate_tags


def invalidate(sender, **kwargs):
    """Протухание кэша обеда"""

    from irk.obed.models import Establishment

    instance = kwargs.get('instance')
    tags = [model_cache_key(instance), ]

    if isinstance(instance, Establishment):
        tags.append('establishment')

    invalidate_tags(tags)
