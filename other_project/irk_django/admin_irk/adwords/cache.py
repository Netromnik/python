# -*- coding: utf-8 -*-

from irk.utils.cache import invalidate_tags


def invalidate(sender, **kwargs):
    """Протухание кэша рекламных новостей"""

    invalidate_tags(['news', 'adwords', ])
