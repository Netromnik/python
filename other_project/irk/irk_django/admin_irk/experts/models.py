# -*- coding: utf-8 -*-

import datetime
import os
import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.text import Truncator

from irk.gallery.fields import ManyToGallerysField
from irk.experts.cache import invalidate
from irk.experts.managers import ExpertManager
from irk.experts.search import ExpertSearch
from irk.news.models import BaseMaterial, material_register_signals
from irk.phones.models import Firms
from irk.special.models import ProjectMixin
from irk.utils.fields.file import ImageRemovableField


def expert_image_upload_to(instance, filename):
    return 'img/site/experts/expert/%(folder)s/%(filename)s.%(ext)s' % {
        'folder': Expert.objects.count() / 1024,
        'filename': str(uuid.uuid4()),
        'ext': os.path.splitext(filename)[1].lstrip('.'),
    }


@material_register_signals
class Expert(BaseMaterial):
    """Пресс-конференция

    Если is_consultation == True, эксперт может сразу отвечать на вопросы, не
    дожидаясь окончания приема вопросов.
    """

    user = models.ForeignKey(User)
    firm = models.ForeignKey(Firms, null=True, blank=True, verbose_name=u'Организация')
    specialist = models.TextField(u'Эксперт')
    avatar = ImageRemovableField(
        upload_to='img/site/experts/avatars/', blank=True, null=True, verbose_name=u'Аватарка',
        help_text=u'Используется в ответах эксперта.<br />Фото должно быть квадратным! Максимальный размер 200x200.'
    )  #  max_size=(200, 200),
    signature = models.CharField(
        u'Подпись эксперта', max_length=100, blank=True, help_text=u'Используется в ответах эксперта.'
    )
    contacts = models.TextField(u'Контактные данные', blank=True)
    stamp_end = models.DateField(u'Конец')
    stamp_publ = models.DateField(u'Дата публикации ответов', blank=True, null=True)
    questions_count = models.PositiveIntegerField(u'Количество вопросов', editable=False, default=0)
    is_answered = models.BooleanField(u'Ответы даны', default=False)
    # NOTE: не используется. 21.04.2015 решено оставить только конференции
    is_consultation = models.BooleanField(u'Консультация', default=False)
    # NOTE: не используется. 21.04.2015 решено не использовать главные конференции
    is_main = models.BooleanField(u'Главная конференция', default=False)
    is_announce = models.BooleanField(u'Анонсировать', default=False)
    image = ImageRemovableField(
        upload_to='img/site/experts/', blank=True, null=True, verbose_name=u'Изображение',
        help_text=u'Оптимальный размер фото 705х470, минимальный 460х307. Пропорция 3:2.'
    )
    wide_image = ImageRemovableField(
        verbose_name=u'Широкоформатная фотография', upload_to=expert_image_upload_to,
        help_text=u'Размер: 940х445 пикселей', blank=True, null=True,
    ) # max_size=(940, 445), min_size=(940, 445),
    picture = ImageRemovableField(upload_to='img/site/experts/', blank=True, null=True, verbose_name=u'Картинка')
    image_title = models.CharField(u'Подпись изображения', max_length=255, blank=True)

    objects = ExpertManager()
    search = ExpertSearch()

    _questions = []

    class Meta:
        db_table = u'experts'
        verbose_name = u'конференция'
        verbose_name_plural = u'конференции'

    def __unicode__(self):
        return self.title

    @staticmethod
    def get_material_url(material):
        return reverse_lazy('news:experts:read', args=(material.category.slug, material.pk))

    @property
    def questions(self):
        if not self._questions:
            if not self.is_answered:
                self._questions = Question.objects.filter(expert=self, same_as__isnull=True).order_by('-created')
            else:
                self._questions = Question.objects.filter(expert=self, same_as__isnull=True,
                                                          answer__isnull=False).order_by('-created')
        return self._questions

    def save(self, *args, **kwargs):
        # Только одна конференция среди открытых может быть главной
        if self.is_main:
            Expert.objects.filter(stamp_end__gte=datetime.datetime.now()).update(is_main=False)
            # Только одна конференция может быть анонсирована
        if self.is_announce:
            Expert.objects.filter(stamp__gte=datetime.datetime.now()).update(is_announce=False)
        super(Expert, self).save(*args, **kwargs)

    def show_rating(self):
        """Рейтинг показывается при таких условиях"""

        if self.is_consultation and self.stamp <= datetime.date.today():
            return True
        if not self.is_consultation and self.is_answered:
            return True
        return False

    def is_active(self):
        """Конференция активна, вопросы принимаются"""

        return self.stamp <= datetime.date.today() <= self.stamp_end

    def is_finish(self):
        """Конференция завершена, но вопросы еще не опубликованы"""

        return datetime.date.today() > self.stamp_end and not self.is_answered

    def is_published(self):
        """Конференция закрыта и вопросы опубликованы"""

        return datetime.date.today() > self.stamp_end and self.is_answered

    @property
    def standard_image(self):

        return self.image

    def get_social_label(self):
        return super(Expert, self).get_social_label() or u'Эксперт'


class Question(models.Model):
    """Вопрос/ответ пресс-конференции

    TODO: При удалении вопроса удалять дочерние вопросы?
    """

    user = models.ForeignKey(User)
    expert = models.ForeignKey(Expert)
    question = models.TextField(u'Вопрос')
    answer = models.TextField(u'Ответ')
    created = models.DateTimeField()
    same_as = models.ForeignKey('self', blank=True, null=True, related_name='identical', verbose_name=u'Одинаков с')
    gallery = ManyToGallerysField()  # Галерея изображений в ответах

    _same = []

    class Meta:
        db_table = u'expert_questions'

    def get_absolute_url(self):
        return '%s#quest_%s' % (self.expert.get_absolute_url(), self.pk)

    def save(self, *args, **kwargs):
        super(Question, self).save(*args, **kwargs)
        Expert.objects.filter(pk=self.expert.pk).update(
            questions_count=Question.objects.filter(expert=self.expert).count())

    def delete(self, *args, **kwargs):
        super(Question, self).delete(*args, **kwargs)
        Expert.objects.filter(pk=self.expert.pk).update(
            questions_count=Question.objects.filter(expert=self.expert).count())

    def __unicode__(self):
        return Truncator(self.question).words(15)

    @property
    def same(self):
        if not self._same:
            self._same = Question.objects.filter(same_as=self)
        return self._same


post_save.connect(invalidate, sender=Question)
post_delete.connect(invalidate, sender=Question)


class Subscriber(models.Model):
    """Подписчик ответов экспетра"""

    email = models.EmailField(u'E-mail')
    user = models.ForeignKey(User, null=True, blank=True, verbose_name=u'Пользователь',
                             related_name='expert_subscriber')
    expert = models.ForeignKey(Expert, verbose_name=u'Эксперт')
    created = models.DateTimeField(u'Дата создания', auto_now_add=True, editable=False)

    class Meta:
        verbose_name = u'подписчик эксперта'
        verbose_name_plural = u'подписчики эксперта'

    def __unicode__(self):
        return self.email
