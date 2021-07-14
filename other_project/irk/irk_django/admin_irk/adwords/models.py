# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.db.models.signals import post_save

from irk.adwords.cache import invalidate

from irk.gallery.fields import ManyToGallerysField
from irk.options.models import Site
from irk.comments.models import CommentMixin


class AdWord(models.Model):
    """Рекламная новость"""

    sites = models.ManyToManyField(Site, verbose_name=u'Разделы')
    title = models.CharField(u'Заголовок', max_length=255)
    caption = models.TextField(u'Подводка', blank=True)
    content = models.TextField(u'Содержание', blank=True)
    content_html = models.BooleanField(u'В содержании используется HTML', default=False)
    url = models.URLField(u'Ссылка новости', blank=True)
    gallery = ManyToGallerysField()

    class Meta:
        db_table = u'adwords_main'
        verbose_name = u'рекламная новость'
        verbose_name_plural = u'рекламные новости'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'adwords:read', (), {'adword_id': self.pk}

    def get_url(self):
        """Если у новости задан URL, переадресуем на него"""

        if self.url:
            return self.url
        return self.get_absolute_url()

post_save.connect(invalidate, sender=AdWord)


class AdWordPeriod(models.Model):
    """День показа новости"""

    start = models.DateField(u'Начало показа', db_index=True)
    end = models.DateField(u'Конец показа', db_index=True)
    adword = models.ForeignKey(AdWord, related_name='periods')

    class Meta:
        db_table = u'adwords_dates'
        verbose_name = u'период'
        verbose_name_plural = u'периоды'

    def __unicode__(self):
        if self.start and self.end:
            return '%s - %s ' % (self.start.isoformat(), self.end.isoformat())
        else:
            return ''

post_save.connect(invalidate, sender=AdWord)


class CompanyNews(CommentMixin, models.Model):
    """Новости компаний"""

    title = models.CharField(u'Заголовок', max_length=255)
    caption = models.TextField(u'Подводка', blank=True)
    content = models.TextField(u'Содержание', blank=True)
    stamp = models.DateField(u'Дата', db_index=True,
                             default=datetime.date.today)
    is_hidden = models.BooleanField(u'Скрытая', default=True, db_index=True)
    comments_cnt = models.PositiveIntegerField(
        u'Комментариев', default=0, editable=False)
    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'новость'
        verbose_name_plural = u'новости компаний'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'news:company_news_read', (), {'news_id': self.pk}


class CompanyNewsPeriod(models.Model):
    """День показа новости"""

    start = models.DateField(u'Начало показа', db_index=True)
    end = models.DateField(u'Конец показа', db_index=True)
    news = models.ForeignKey(CompanyNews, related_name='period',)

    class Meta:
        verbose_name = u'период'
        verbose_name_plural = u'периоды'

    def __unicode__(self):
        if self.start and self.end:
            return '%s - %s ' % (self.start.isoformat(), self.end.isoformat())
        else:
            return ''
