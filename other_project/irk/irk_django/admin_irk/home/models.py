# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save

from irk.utils.db.models.fields import ColorField
from irk.utils.fields.file import ImageRemovableField

from irk.home.cache import invalidate


class Logo(models.Model):
    """Логотипы на главной странице"""

    image = ImageRemovableField(verbose_name=u'Логотип', upload_to='img/site/logo',
                             help_text=u'Максимальный размер: 200x74 пикселей')  # max_size=(200, 74)
    color = ColorField(u'Цвет', null=True, blank=True)
    title = models.CharField(u'Название', max_length=255)
    start_month = models.IntegerField(u'Месяц начала показа', db_index=True, default=0)
    start_day = models.IntegerField(u'День начала показа', db_index=True, default=0)
    end_month = models.IntegerField(u'Месяц окончания показа', db_index=True, default=0)
    end_day = models.IntegerField(u'Дата окончания показа', db_index=True, default=0)
    create_stamp = models.DateField(u'Дата добавления', auto_now_add=True)
    visible = models.BooleanField(u'Выводить на сайте', default=True, db_index=True)

    class Meta:
        verbose_name = u'логотип'
        verbose_name_plural = u'логотипы'

    def __unicode__(self):
        return self.title


post_save.connect(invalidate, sender=Logo)
