# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models.signals import post_save

from irk.news.managers import BaseMaterialManager, LongreadMaterialManager, MaterialManager, MagazineMaterialManager
from irk.news.models import BaseMaterial, material_register_signals, wide_image_upload_to
from irk.options.models import Site
from irk.special.models import ProjectMixin
from irk.utils.helpers import iptoint, inttoip, get_client_ip
from irk.utils.fields.file import ImageRemovableField

from irk.polls.cache import invalidate
from irk.polls.managers import PollChoiceManager


class Quiz(models.Model):
    """Опрос"""

    name = models.CharField(u'Название', max_length=255)
    slug = models.SlugField(u'Алиас')
    comments_cnt = models.PositiveIntegerField(u'Комментариев', default=0, editable=False)
    title = models.CharField(u'Заголовок', max_length=255)
    content = models.TextField(u'Содержание', blank=True)

    class Meta:
        verbose_name = u'опрос'
        verbose_name_plural = u'опросы'

    def __unicode__(self):
        return self.name

    def voted(self, request):
        """Проверка на участие в опросе по первому привязанному голосованию"""

        ct = ContentType.objects.get_for_model(self)
        today = datetime.date.today()

        try:
            poll = Poll.objects.filter(target_ct=ct, target_id=self.pk, start__lte=today).order_by('-end')[0]
            if poll.end is not None and poll.end < today:
                voted = True
            else:
                voted = poll.voted(request)
        except IndexError:
            voted = True

        return voted

    @property
    def votes_cnt(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            poll = Poll.objects.filter(target_ct=ct, target_id=self.pk).order_by('-end')[0]
            return poll.votes_cnt
        except IndexError:
            return 0

    def get_absolute_url(self):
        return reverse(self.slug)


@material_register_signals
class Poll(BaseMaterial):
    """Голосование"""

    start = models.DateField(u'Дата начала', db_index=True, blank=True, null=True)
    end = models.DateField(u'Дата конца', db_index=True, blank=True, null=True)
    votes_cnt = models.PositiveIntegerField(u'Количество голосов', default=0, editable=False)
    multiple = models.BooleanField(u'Несколько ответов', default=False)

    image = ImageRemovableField(
        verbose_name=u'Стандартное изображение', upload_to=wide_image_upload_to, blank=True, null=True,
        help_text=u'Оптимальный размер фото 805х536. Пропорция 3:2.')  #  min_size=(805, 536)
    show_image_on_read = models.BooleanField(u'Отображать фото на странице голосования', default=False)
    image_label = models.CharField(u'Подпись стандартного изображения', max_length=255, blank=True)
    w_image = ImageRemovableField(
        verbose_name=u'Широкоформатное изображение', upload_to=wide_image_upload_to, blank=True, null=True,
        help_text=u'Размер: 940х405 пикселей.') # max_size=(940, 445), min_size=(940, 445)

    target_ct = models.ForeignKey(
        ContentType, null=True, blank=True, verbose_name=u'Тип объекта', help_text=u'К чему привязывать голосование'
    )
    target_id = models.PositiveIntegerField(default=0)

    _choices = []

    objects = BaseMaterialManager()
    material_objects = MaterialManager()
    longread_objects = LongreadMaterialManager()
    magazine_objects = MagazineMaterialManager()

    class Meta:
        db_table = u'polls_main'
        verbose_name = u'голосование'
        verbose_name_plural = u'голосования'

    def __unicode__(self):
        return self.title

    @staticmethod
    def get_material_url(material):
        name = '{0}:poll_read'.format(material.source_site.slugs)
        return reverse_lazy(name, kwargs={'poll_id': material.pk})

    @property
    def choices(self):
        if not self._choices:
            self._choices = self.pollchoice_set.all().order_by('position', 'id')
        return self._choices

    def voted(self, request):
        """Проверяем, голосовал ли пользователь за этот вариант"""

        available_choices = self.choices.values_list('pk', flat=True)
        if request.user.is_authenticated:
            vote = PollVote.objects.filter(user=request.user)
        else:
            ip = iptoint(get_client_ip(request))
            vote = PollVote.objects.filter(user__isnull=True, ip=ip)
            cookie = request.COOKIES.get('pl', '').split(':')
            for poll in cookie:
                try:
                    if self.pk == int(poll):
                        return True
                except (TypeError, ValueError):
                    continue

        return vote.filter(choice__in=available_choices).count() > 0

    @property
    def standard_image(self):
        if hasattr(self, 'image'):
            return self.image
        else:
            return None

    @property
    def wide_image(self):
        """Широкоформатное изображение материала"""

        if hasattr(self, 'w_image'):
            return self.w_image
        else:
            return None

    def is_active(self):
        """Проходит ли еще голосование?"""

        today = datetime.date.today()

        if self.end and self.end < today:
            return False

        return True

    def get_social_label(self):
        return super(Poll, self).get_social_label() or u'Опросы'


class PollChoice(models.Model):
    """Вариант ответа на голосование"""

    poll = models.ForeignKey(Poll)
    text = models.CharField(u'Вариант ответа', max_length=255)
    position = models.PositiveIntegerField(verbose_name=u'Позиция', default=0)
    votes_cnt = models.PositiveIntegerField(default=0)

    image = ImageRemovableField(verbose_name=u'изображение', upload_to='img/site/polls/choice/', help_text=u'Размер: 60x60 пикселей',
                  null=True, blank=True)  # max_size=(60, 60), min_size=(60, 60),

    objects = PollChoiceManager()

    class Meta:
        db_table = u'polls_choices'
        verbose_name = u'ответ'
        verbose_name_plural = u'ответы'

    def __unicode__(self):
        return self.text


post_save.connect(invalidate, sender=PollChoice)


class PollVote(models.Model):
    """Голос за определенный вариант"""

    choice = models.ForeignKey(PollChoice)
    user = models.ForeignKey(User, blank=True, null=True)
    ip = models.PositiveIntegerField(default=0, db_index=True)  # default=0 для старых записей
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'polls_votes'
        verbose_name = u'голос'
        verbose_name_plural = u'голоса'

    def __unicode__(self):
        if self.user:
            return self.user.username
        return inttoip(self.ip)

    def save(self, *args, **kwargs):
        """Обновляем количество голосов у Poll и PollChoice"""

        super(PollVote, self).save(args, kwargs)

        self.choice.votes_cnt = PollVote.objects.filter(choice=self.choice).count()
        self.choice.save()

        self.choice.poll.votes_cnt = (
            PollChoice.objects.filter(poll=self.choice.poll).aggregate(votes=models.Sum('votes_cnt'))['votes']
        )
        self.choice.poll.save()


post_save.connect(invalidate, sender=PollVote)
