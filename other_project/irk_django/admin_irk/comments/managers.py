# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models

from irk.comments.helpers import content_type_for_comments


class CommentQuerySet(models.QuerySet):
    """QuerySet for comments"""

    def visible(self):
        return self.filter(status=self.model.STATUS_VISIBLE)

    def for_object(self, obj):
        """Comment for obj"""
        ct = content_type_for_comments(obj)

        return self.filter(content_type=ct, target_id=obj.pk)

    def roots(self):
        """Return root elements without parents"""

        return self.filter(parent__isnull=True)


CommentManager = CommentQuerySet.as_manager()
