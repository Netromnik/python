# -*- coding: utf-8 -*-

import uuid
import hashlib
import datetime

from django.db import models
from django.conf import settings


def _generate_key():
    bits = [
        settings.SECRET_KEY,
        uuid.uuid4().hex,
        datetime.datetime.now().isoformat(),
    ]
    return hashlib.sha256('-'.join(bits)).hexdigest()[:40]


class Application(models.Model):
    """Приложение, имеющее доступ к API"""

    title = models.CharField(u'Название', max_length=255)
    access_token = models.CharField(u'Ключ авторизации', max_length=40, unique=True)
    created = models.DateTimeField(u'Дата создания')

    class Meta:
        verbose_name = u'приложение'
        verbose_name_plural = u'приложения'

    def __unicode__(self):
        return self.title

    def regenerate_access_token(self):
        self.access_token = _generate_key()
        self.save()
