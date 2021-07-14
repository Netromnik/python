# -*- coding: UTF-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from irk.options.models import Site
from irk.utils.fields.file import FileRemovableField
from irk.utils.validators import FileSizeValidator


class Page(models.Model):
    url = models.CharField(_('URL'), max_length=100, db_index=True)
    title = models.CharField(_('title'), max_length=200, blank=True)
    content = models.TextField(_('content'), blank=True)
    sub_content = models.TextField(u'Доп. контент', blank=True)
    template_name = models.CharField(_('template name'), max_length=70, blank=True)
    site = models.ForeignKey(Site, blank=False, verbose_name=u'Раздел')
    position = models.IntegerField(u'Позиция', blank=True, default=0, db_index=True)
    editors = models.ManyToManyField(Group, verbose_name=u'Редакторы')

    objects = models.Manager()

    class Meta:
        verbose_name = u'простая страница'
        verbose_name_plural = u'простые страницы'
        ordering = ('position', 'title',)

    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        if self.site.url:
            return self.site.url + self.url.lstrip("/")
        else:
            return self.url

    def save(self, *args, **kwargs):
        return super(Page, self).save(*args, **kwargs)


class FileSortManager(models.Manager):
    def get_queryset(self):
        return super(FileSortManager, self).get_queryset()


class File(models.Model):
    flatpage = models.ForeignKey(Page)
    name = models.CharField(max_length=100, verbose_name=u'Название')
    file = FileRemovableField(verbose_name=u'Файл', upload_to="img/site/pages/",
                              validators=[FileSizeValidator(max_size=1024 * 1024 * 5)])
    href = models.CharField(max_length=100, blank=True, verbose_name=u'Ссылка')

    class Meta:
        verbose_name = u'Файлы'
        verbose_name_plural = u'Файлы'
        ordering = ('name', )

    def __unicode__(self):
        return self.name
