# -*- coding: utf-8 -*-

import datetime
import random

from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse

from irk.authentication.helpers import get_hexdigest
from irk.magazine.managers import MagazineQuerySet
from irk.news.models import SocialCardMixin
from irk.utils.fields.file import ImageRemovableField
from irk.adv.models import Place


class MagazineAuthor(models.Model):
    """Автор журнала"""

    name = models.CharField(u'Имя', max_length=255)
    image = ImageRemovableField(upload_to='img/site/magazine/author', blank=True, null=True, verbose_name=u'фотография')
    position = models.CharField(u'Должность', max_length=255, default=u'', blank=True)

    class Meta:
        verbose_name = u'автор журнала'
        verbose_name_plural = u'авторы журналов'

    def __unicode__(self):
        return self.name


class Magazine(SocialCardMixin, models.Model):
    """Журнал"""

    title = models.CharField(u'Заголовок', max_length=255)
    caption = models.TextField(u'Подводка', blank=True)
    slug = models.SlugField(u'Алиас')

    visible = models.BooleanField(u'Выводить на сайте', default=True)
    show_on_home = models.BooleanField(u'Показывать на главной', default=False, db_index=True)
    created = models.DateTimeField(u'Дата создания', auto_now_add=True, editable=False)

    home_image = models.ImageField(
        upload_to='img/site/magazine/', blank=True, null=True, verbose_name=u'изображение для главной'
    )
    caption_author = models.ForeignKey(MagazineAuthor, verbose_name=u'Автор подводки', null=True, blank=True)

    branding_bottom = models.ForeignKey(Place, verbose_name=u'Позиция брендирования внизу страницы', null=True,
                                        related_name='magazine_branding_bottom', blank=True)
    banner_right = models.ForeignKey(Place, verbose_name=u'Позиция баннера в правой колонке', null=True,
                                     related_name='magazine_banner_right', blank=True)
    banner_comment = models.ForeignKey(Place, verbose_name=u'Позиция между текстом и комментами', null=True,
                                     related_name='magazinet_banner_comment', blank=True)

    objects = MagazineQuerySet.as_manager()

    class Meta:
        verbose_name = u'журнал'
        verbose_name_plural = u'журналы'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Журнал на главной может быть только один
        if self.show_on_home:
            Magazine.objects.filter(show_on_home=True).update(show_on_home=False)
        return super(Magazine, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('magazine:read', args=(self.slug, ))


class MagazineSubscriber(models.Model):
    """Подписчик на рассылку журнала"""

    email = models.EmailField(u'E-mail', max_length=40, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    hash = models.CharField(max_length=40, editable=False, db_index=True)
    is_active = models.BooleanField(u'Активирован', default=True, db_index=True)
    hash_stamp = models.DateTimeField(null=True, blank=True, default=datetime.datetime.now, editable=False)

    class Meta:
        verbose_name = u'подписчик журнала'
        verbose_name_plural = u'подписчики журнала'

    def __unicode__(self):
        return self.email

    def generate_hash(self):
        """Создает временный хеш для подтверждения регистрации, либо для восстановления пароля."""

        if not self.hash:
            self.hash = get_hexdigest('sha1', str(random.random()), str(random.random()))
        self.hash_stamp = datetime.datetime.now()
        self.save()
