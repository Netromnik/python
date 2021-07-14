# -*- coding: utf-8 -*-

import datetime
import os
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from irk.gallery.fields import ManyToGallerysField
from irk.news.models import BaseMaterial, material_register_signals, wide_image_upload_to
from irk.options.models import Site
from irk.ratings.models import RatingObject
from irk.special.models import ProjectMixin


def textblock_upload_to(obj, filename):
    return 'img/site/contests/%s%s' % (uuid.uuid4().hex, os.path.splitext(filename)[1])


@material_register_signals
class Contest(BaseMaterial):
    """Конкурс"""

    TYPE_PHOTO = 'photo'
    TYPE_QUIZ = 'quiz'
    TYPE_INSTAGRAM = 'ig'
    TYPE_TEXT = 'text'

    TYPE = (
        (TYPE_PHOTO, u'Показуха'),
        (TYPE_QUIZ, u'Викторина'),
        # (TYPE_INSTAGRAM, u'Instagram'),
        # (TYPE_TEXT, u'Текстовый')
    )

    SMS_VOTE = 1
    SITE_VOTE = 2

    VOTE_TYPE_CHOICES = (
        (SMS_VOTE, u'через смс'),
        (SITE_VOTE, u'на сайте'),
    )

    image = models.ImageField(verbose_name=u'Изображение', upload_to=textblock_upload_to, blank=True)
    image_caption = models.CharField(u'Подводка изображения', max_length=255, blank=True)
    w_image = models.ImageField(
        verbose_name=u'Широкоформатная фотография', upload_to=wide_image_upload_to,
        help_text=u'Размер: 940х445 пикселей', blank=True
    )
    date_start = models.DateField(u'Дата начала', db_index=True)
    date_end = models.DateField(u'Дата конца', db_index=True)
    is_blocked = models.BooleanField(default=False, verbose_name=u'Закрыть голосование',
                                     help_text=u'Голосование отображается, но возможность проголосовать отключена')
    type = models.CharField(max_length=10, choices=TYPE, verbose_name=u'Тип', default=TYPE_PHOTO, db_index=True)
    vote_type = models.SmallIntegerField(choices=VOTE_TYPE_CHOICES, verbose_name=u'Голосование', default=SITE_VOTE)
    user_can_add = models.BooleanField(verbose_name=u'Пользователи могут добавляться', default=True)
    instagram_tag = models.CharField(u'Хэштег Instagram', max_length=50, blank=True)

    class Meta:
        db_table = 'contests_contests'
        verbose_name = u'конкурс'
        verbose_name_plural = u'конкурсы'

    def __unicode__(self):
        return self.title

    @staticmethod
    def get_material_url(material):
        return reverse('contests:contests:read', args=(material.slug,))

    def is_closed(self):
        return self.date_end < datetime.date.today()

    @property
    def wide_image(self):
        """Широкоформатное изображение материала"""

        if hasattr(self, 'w_image'):
            return self.w_image
        else:
            return None

    @property
    def standard_image(self):
        """Стандартное изображение материала"""

        if hasattr(self, 'image'):
            return self.image
        else:
            return None

    def get_social_label(self):
        return super(Contest, self).get_social_label() or u'Конкурсы'


class Participant(models.Model):
    """Участник конкурса"""

    contest = models.ForeignKey(Contest, related_name='participants', verbose_name=u'Конкурс')
    title = models.CharField(u'Название', max_length=255, blank=True)
    description = models.TextField(u'Описание', blank=True, default='')
    comments_cnt = models.PositiveIntegerField(editable=False, default=0)
    sms_value = models.IntegerField(null=True, blank=True, verbose_name=u'Значение смс голосования')
    sms_code = models.CharField(max_length=255, verbose_name=u'Код для смс', blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Пользователь', )
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'Имя')
    instagram_id = models.CharField(u'Instagram ID', max_length=40, editable=False, blank=True, null=True)
    is_active = models.BooleanField(u'Выводить на сайте', default=False)
    reject_reason = models.CharField(u'Причина отказа', max_length=255, default='', blank=True)

    full_name = models.CharField(u'имя и фамилия', max_length=100, blank=True)
    phone = models.CharField(u'телефон', max_length=20, blank=True)

    gallery = ManyToGallerysField()

    class Meta:
        db_table = 'contests_competitors'
        verbose_name = u'участник'
        verbose_name_plural = u'участники'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('contests:contests:participant_read', args=(self.contest.slug, self.pk))

    def can_rate(self):
        if not self.contest.is_closed() and not self.contest.is_blocked:
            return True
        else:
            return False

    @property
    def rating_object(self):
        """Инстанс класса RatingObject для этого участника"""
        if not self.pk:
            return None

        ct = ContentType.objects.get_for_model(Participant)
        # если никто не голосовал за этот объект, то RatingObject'a нет
        try:
            return RatingObject.objects.get(content_type=ct.pk, object_pk=self.pk)
        except RatingObject.DoesNotExist as identifier:
            return None
