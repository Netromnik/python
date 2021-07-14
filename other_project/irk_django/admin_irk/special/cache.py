# -*- coding: utf-8 -*-

import logging

from irk.utils.cache import invalidate_tags

logger = logging.getLogger(__name__)


def invalidate(sender, **kwargs):
    """Протухание кэша для моделей приложения Special"""

    from irk.special.models import Project

    instance = kwargs.get('instance')
    tags = []

    if isinstance(instance, Project):
        tags.append('project')

    invalidate_tags(tags)
