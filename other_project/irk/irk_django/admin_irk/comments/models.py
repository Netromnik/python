# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import time
import datetime
import six

from closuretree.models import ClosureModel
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property
from django.conf import settings

from irk.comments.helpers import content_type_for_comments
from irk.comments.managers import CommentManager
from irk.utils.db.models.mixins import SerializerMixin


class CommentMixin(models.Model):
    """Примесь для комментариев"""

    hide_comments = models.BooleanField(
        'Скрывать комментарии', default=False, db_index=True, help_text='отключить комменты без сообщения про 24 часа'
    )
    disable_comments = models.BooleanField(
        'Отключить комментирование', default=False, db_index=True, help_text='сообщение выводится'
    )

    class Meta:
        abstract = True

    @cached_property
    def comments(self):
        return Comment.objects.for_object(self)

    @cached_property
    def root_comments_cnt(self):
        return Comment.objects.for_object(self).roots().count()

    def get_comments_url(self):
        ct = content_type_for_comments(self)
        return reverse('comments:list', kwargs={'ct_id': ct.id, 'target_id': self.id})

    @property
    def can_commented(self):
        return not self.disable_comments

    def get_last_comment(self):
        return Comment.objects.for_object(self).visible().order_by('-pk').first()


class CommentGenericForeignKey(GenericForeignKey):
    """GenericForeignKey который умеет правльно определять content_type целевого объекта"""

    def get_content_type(self, obj=None, id=None, using=None):
        if obj is not None:
            return content_type_for_comments(obj)
        else:
            return super(CommentGenericForeignKey, self).get_content_type(
                obj=obj, id=id, using=using
            )


@six.python_2_unicode_compatible
class Comment(SerializerMixin, ClosureModel):
    """Комментарий"""

    STATUS_VISIBLE = 1
    STATUS_AUTO_DELETE = 2
    STATUS_DIRECT_DELETE = 3
    STATUS_SPAM = 4
    STATUS_CHOICES = (
        (STATUS_VISIBLE, 'виден'),
        (STATUS_AUTO_DELETE, 'автоматическое удаление'),
        (STATUS_DIRECT_DELETE, 'прямое удаление'),
        (STATUS_SPAM, 'спам'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField('текст', blank=True)
    ip = models.BigIntegerField('IP', editable=False, null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        'статус', choices=STATUS_CHOICES, default=STATUS_VISIBLE, db_index=True
    )
    is_first = models.BooleanField('первый комментарий пользователя', default=False, db_index=True)
    is_edited = models.BooleanField('отредактирован', default=False, db_index=True)

    created = models.DateTimeField('дата добавления', db_index=True, auto_now_add=True)
    modified = models.DateTimeField('дата изменения', db_index=True, auto_now=True)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(db_index=True)
    target = CommentGenericForeignKey('content_type', 'target_id')

    # Эти поля нужны для миграции комментариев из форума
    message_id = models.IntegerField(null=True, db_index=True)
    message_parent_id = models.IntegerField(null=True, db_index=True)

    objects = CommentManager

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return self.text[:50] + ('...' if len(self.text) > 50 else '')

    def __repr__(self):
        return '<Comment {0.user.username} «{0!s}»>'.format(self).encode('utf-8')

    def save(self, *args, **kwargs):
        if not self.user.comments.exists():
            self.is_first = True

        super(Comment, self).save(*args, **kwargs)

        # Пересчет происходит всегда так как в комментарии меняют только статус
        if hasattr(self.target, 'comments_cnt'):
            comments_cnt = Comment.objects.filter(target_id=self.target_id, content_type=self.content_type,
                                                  status=Comment.STATUS_VISIBLE).count()
            self.target.comments_cnt = comments_cnt
            self.target.save()

    def is_visible(self):
        return self.status == self.STATUS_VISIBLE

    def is_parent(self):
        """Is this node has children"""
        return Comment.objects.filter(parent_id=self.pk).exists()

    def get_absolute_url(self):
        if self.is_root_node():
            ids = '{}'.format(self.pk)
        else:
            ids = '{}-{}'.format(self.get_root().pk, self.pk)
        return '{}?comments-{}#comments'.format(self.target.get_absolute_url(), ids)

    def get_visible_children(self):
        qs = self.children if hasattr(self, 'children') else self.get_descendants()
        return qs.filter(status=self.STATUS_VISIBLE)

    def get_visible_children_count(self):
        return self.get_visible_children().count()

    @property
    def created_timestamp(self):
        return int(time.mktime(self.created.timetuple()))

    @property
    def end_edit_timestamp(self):
        return int(time.mktime(self.created.timetuple())) + settings.COMMENTS_EDIT_ALLOWED_TIME

    @property
    def is_editable(self):
        return True if int(time.time()) <= self.end_edit_timestamp and self.get_visible_children_count() == 0 else False

class ActionLog(models.Model):
    """ Логирование всех действий связанных с комментами"""

    ACTION_DELETE = 1
    ACTION_RESTORE = 2

    ACTION_CHOICES = (
        (ACTION_DELETE, 'Удаление'),
        (ACTION_RESTORE, 'Восстановление'),
    )

    created = models.DateTimeField('Дата добавления', auto_now_add=True)
    user = models.ForeignKey(User, null=True, verbose_name='Изменил')
    comment = models.ForeignKey(Comment, verbose_name='Комментарий')
    action = models.SmallIntegerField('Действие', choices=ACTION_CHOICES)

    class Meta:
        verbose_name = 'действие'
        verbose_name_plural = 'действия'


class SpamIp(models.Model):
    """IP адреса спамеров"""

    ip = models.GenericIPAddressField('IP адрес', db_index=True)
    created = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Спам IP адрес'
        verbose_name_plural = 'Спам IP адреса'

    def __unicode__(self):
        return self.ip


class SpamLog(models.Model):
    """Лог автоматического бана спамеров"""

    user = models.ForeignKey(User, null=True, verbose_name='Аккаунт')
    text = models.TextField('текст', blank=True)
    ip = models.GenericIPAddressField('IP адрес')
    created = models.DateTimeField('Дата добавления', auto_now_add=True)
    reason = models.CharField('Причина бана', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Лог автоматического бана спамеров'
        verbose_name_plural = 'Лог автоматического бана спамеров'

    def __unicode__(self):
        return self.text[:100]


class SpamPattern(models.Model):
    """Ключевое слово для проверки сообщений на спам"""

    text = models.TextField('Ключевое слово')
    created = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'антиспам'
        verbose_name_plural = 'антиспам'

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        from irk.comments.tasks import clear_spam

        super(SpamPattern, self).save(*args, **kwargs)

        # Удалене всех последних сообщений со спамом за последние 48 часов
        pattern = self.text.lower()
        stamp = datetime.datetime.now() - datetime.timedelta(2)
        clear_spam.delay(pattern, stamp)
