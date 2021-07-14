# -*- coding: utf-8 -*-

import os
import uuid

import django
from django.conf import settings
from django.db import models


# GeoDjango introspection rules
# для Cities.center
# TODO: Перенести в более подходящее место
has_gis = "django.contrib.gis" in settings.INSTALLED_APPS

from django.contrib.gis.db.models.fields import GeometryField

if django.VERSION[0] == 1 and django.VERSION[1] >= 1:
    rules = [((GeometryField,), [], {
        "srid": ["srid", {"default": 4326}],
        "spatial_index": ["spatial_index", {"default": True}],
        "dim": ["dim", {"default": 2}]})]
else:
    rules = [((GeometryField, ), [], {
        "srid": ["_srid", {"default": 4326}],
        "spatial_index": ["_index", {"default": True}],
        "dim": ["_dim", {"default": 2}]})]


def image_upload_to(instance, filename):
    """Вернуть путь для сохранения изображения"""

    opts = instance._meta

    return 'img/site/{app_label}/{model_name}/{folder}/{filename}{ext}'.format(
        app_label=opts.app_label,
        model_name=opts.model_name,
        folder=opts.model.objects.count() / 1024,
        filename=str(uuid.uuid4()),
        ext=os.path.splitext(filename)[1],
    )


class TweetEmbed(models.Model):
    """Встраиваемый блок твиттера"""

    id = models.BigIntegerField(u'Tweet ID', primary_key=True)
    url = models.URLField(u'Tweet URL')
    html = models.TextField(u'HTML-код', blank=True)


class InstagramEmbed(models.Model):
    """Встраиваемый виджет Инстаграма"""

    id = models.CharField(u'Slug', primary_key=True, max_length=191)
    url = models.URLField()
    html = models.TextField(u'HTML-код', blank=True)


class VkVideoEmbed(models.Model):
    """Встраиваемое видео из Вконтакта"""

    id = models.CharField(u'Vk video ID', max_length=20, primary_key=True)
    url = models.URLField(u'Video URL')
    html = models.TextField(u'HTML-код', blank=True)
