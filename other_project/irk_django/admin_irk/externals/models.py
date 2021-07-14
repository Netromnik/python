# -*- coding: utf-8 -*-

from jsonfield import JSONField

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse_lazy
from django.db import models

from irk.options.models import Site


class InstagramTag(models.Model):
    """Хэштег инстаграма"""

    # Источники новостей
    ALL = 0
    IMAGE = 1
    VIDEO = 2
    TYPES = (
        (ALL, u'любой'),
        (IMAGE, u'только фото'),
        (VIDEO, u'только видео'),
    )

    title = models.CharField(u'Название', max_length=191)
    name = models.CharField(u'Тег', unique=True, max_length=191, help_text=u"без #")
    type = models.PositiveIntegerField(u'Тип контента', choices=TYPES, default=ALL)
    site = models.ForeignKey(Site, verbose_name=u'Раздел', null=True, blank=True)
    is_visible = models.BooleanField(u'Отображается', default=True, db_index=True)
    description = models.TextField(u'Описание', null=True, blank=True)
    latest_media_id = models.CharField(u'Последний провереный id', max_length=30, blank=True)

    class Meta:
        verbose_name = u'хэштег Instagram'
        verbose_name_plural = u'хэштеги Instagram'
        db_table = 'externals_instagram_tags'

    def __unicode__(self):
        return self.title


class InstagramMedia(models.Model):
    """Медиа-контент инстаграма"""

    instagram_id = models.CharField(max_length=30, unique=True)
    is_visible = models.BooleanField(u'Отображается', default=True, db_index=True)
    data = JSONField()
    tags = models.ManyToManyField(InstagramTag, related_name='media', verbose_name=u'хэштег Instagram')
    is_marked = models.BooleanField(u'Выделено', default=False, db_index=True)
    created = models.DateTimeField(editable=False, auto_now_add=True, null=True)

    class Meta:
        db_table = 'externals_instagram_media'
        verbose_name = u'Instagram'
        verbose_name_plural = u'Instagram'

    def __unicode__(self):
        return u'Фото {}'.format(self.instagram_id)

    def get_admin_url(self):
        """Получить ссылку для редактирования объекта в админке"""

        return reverse_lazy(admin_urlname(self._meta, 'change'), args=[self.pk])


class InstagramUserBlacklist(models.Model):
    """Заблокированный пользователь инстаграма"""

    username = models.CharField(u'Пользователь', max_length=100, db_index=True)

    class Meta:
        verbose_name = u'Заблокированный пользователь instagram'
        verbose_name_plural = u'Заблокированные пользователи instagram'
