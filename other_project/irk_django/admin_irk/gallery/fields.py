# -*- coding: utf-8 -*-

from irk.gallery import models

from django.contrib.contenttypes.fields import GenericRelation


def ManyToGallerysField(**kwargs):
    return GenericRelation(models.Gallery, default='', **kwargs)
