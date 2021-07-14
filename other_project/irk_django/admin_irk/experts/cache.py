# -*- coding: utf-8 -*-

from irk.utils.cache import invalidate_tags


def invalidate(sender, **kwargs):
    """Протухание кэша эксперта"""

    invalidate_tags(('experts', 'expert'))
