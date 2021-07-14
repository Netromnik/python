# -*- coding: utf-8 -*-

from utils.cache import  invalidate_tags


def invalidate(sender, **kwargs):
    """Протухание кэша разделов"""

    invalidate_tags(('options',))
