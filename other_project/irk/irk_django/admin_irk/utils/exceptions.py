# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def raven_capture(einfo=None):
    """Перехват исключений"""

    if settings.DEBUG or not 'raven.contrib.django.raven_compat' in settings.INSTALLED_APPS:
        logger.debug('Skipping `raven_capture` routine')
        return

    from raven.contrib.django.raven_compat.models import client
    client.captureException(einfo)
    logger.debug('Exception was sent to raven')
