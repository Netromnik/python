# -*- coding: utf-8 -*-

import urllib

from django.db import models
from utils.fields.file import ImageRemovableField, FileRemovableField
from .managers import SitesManager
from utils.db.models.fields import ColorField


class Site(models.Model):
    """Раздел сайта"""

    name = models.CharField(u'Название', max_length=100, blank=True)
    title = models.CharField(u'Заголовок', max_length=255)
    url = models.CharField(u'URL', max_length=255, blank=True)
    slugs = models.CharField(u'Алиасы', max_length=50, unique=True,
                             help_text=u'Должен быть уникальным и не содержать в себе другие алиасы. Например news-some не подойдет')
    position = models.IntegerField(u'Позиция', db_index=True)
    menu_class = models.CharField(u'Класс', max_length=15, blank=True)
    in_menu = models.BooleanField(u'В меню', default=False, help_text=u'Если галочка стоит, то будет отображаться в основном меню, если нет то в списке "ещё"')
    is_hidden = models.BooleanField(u'Спрятан', default=False, db_index=True, help_text=u'Не отображается в меню вообще')
    booking_visible = models.BooleanField(u'Выводить в бронировании', default=False)
    mark_in_menu = models.BooleanField(u'В верхней строке', default=False)
    highlight = models.BooleanField(u'Подсвечивать', default=False)
    small = models.BooleanField(u'Уменьшенная шапка', default=False)
    blogs_through_perms = models.BooleanField(u'Добавление/ред. блогов только через права.', default=False)
    show_in_bar = models.BooleanField(u'Показывать в полосе навигации', default=False, help_text=u'Для внешних сайтов')
    track_transition = models.BooleanField(u'Подсчитывать переходы', default=False, help_text=u'Статистика хранится в Google.Analytics')
    icon = ImageRemovableField(verbose_name=u'Иконка', upload_to='img/site/option/icon/', blank=True, null=True)  #  max_size=(15,15)
    show_icon = models.BooleanField(u'Показывать иконку', default=False)
    branding_image = ImageRemovableField(verbose_name=u'Брендирование', upload_to='img/site/adv/branding', blank=True, null=True,
         help_text=u'Размеры изображения: 1920×250 пикселей')  # min_size=(1920, 250), max_size=(1920, 250)

    branding_color = ColorField(u'Цвет фона брендирования', blank=True, null=True)
    widget_image = ImageRemovableField(verbose_name=u'Изображение виджета', upload_to='img/site/adv/widgets', blank=True,
        null=True, help_text=u'Выводится справа от меню')  # min_size=(54, 54), max_size=(54, 54),
    widget_link = models.URLField(u'Ссылка виджета', blank=True, null=True)
    widget_text = models.CharField(u'Текст виджета', max_length=255, blank=True, null=True)

    image = FileRemovableField(verbose_name=u'Картинка вместо текста', upload_to='img/site/option/image/', blank=True, null=True,
                               help_text=u'Размер по высоте 20px. Можно SVG. Заменяет текст в меню картинкой')

    objects = SitesManager()

    _url = None

    class Meta:
        db_table = 'options_site'
        verbose_name = u'раздел'
        verbose_name_plural = u'разделы'
        ordering = ['position']

    def __unicode__(self):
        if len(self.name.strip()):
            return self.name
        else:
            return self.title

    def save(self):
        if hasattr(Site, '_cache'):
            Site._cache.clear()
            Site.objects._cache.clear()
        return super(Site, self).save()

    def get_url(self):
        if not self._url:
            if self.url:
                return self.url.rstrip('/')
            else:
                return self.site.domain

        return self._url

    def get_domain(self):
        domain = self.site.domain
        domain = domain.split('.')
        return domain[0]

    def get_path(self):
        """Если сайт имеет path"""

        if self.url:
            site_url = self.url
            return urllib.splithost('//'+site_url)[1]
        else:
            return ''

    def get_host(self):
        if self.url:
            site_url = self.url
            return urllib.splithost('//'+site_url)[0]
        else:
            return ''

