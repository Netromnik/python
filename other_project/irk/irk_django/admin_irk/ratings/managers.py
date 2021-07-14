# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType


class RatingObjectManager(models.Manager):

    def get_for_object(self, instance):

        ct = ContentType.objects.get_for_model(instance)
        obj, created = self.get_or_create(
            content_type=ct,
            object_pk=instance.pk,
        )

        return obj
