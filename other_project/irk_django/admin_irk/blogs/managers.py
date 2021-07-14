# -*- coding: utf-8 -*-

from django.db import models


class UserBlogEntryManager(models.Manager):
    def get_queryset(self):
        return super(UserBlogEntryManager, self).get_queryset().filter(type=1)


class AdminBlogEntryManager(models.Manager):
    def get_queryset(self):
        return super(AdminBlogEntryManager, self).get_queryset().filter(type=2)
