# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from irk.gallery.fields import ManyToGallerysField
from irk.blogs.cache import invalidate
from irk.blogs.managers import UserBlogEntryManager, AdminBlogEntryManager
from irk.blogs.signals import author_recount
from irk.comments.models import CommentMixin
from irk.options.models import Site


class Author(User):
    """Автор блогов"""

    is_visible = models.BooleanField(u'Отображается', default=True)
    is_operative = models.BooleanField(u'Может писать', default=True)
    subscribers_cnt = models.PositiveIntegerField(u'Количество подписчиков', default=0)
    entries_cnt = models.PositiveIntegerField(u'Количество постов', default=0)
    comments_cnt = models.PositiveIntegerField(u'Количество комментариев к постам', default=0)
    date_started = models.DateField(u'Дата начала записей')

    class Meta:
        db_table = 'blogs_authors'
        verbose_name = u'Автор'
        verbose_name_plural = u'Авторы'

    def latest_entry(self):
        try:
            return self.entries.filter(visible=True).latest('created')
        except BlogEntry.DoesNotExist:
            return None


class BlogEntry(models.Model):
    """Запись в блоге"""

    TYPE_BLOG = 1
    TYPE_EDITORIAL = 2

    TYPES = (
        (TYPE_BLOG, u'Запись блога'),
        (TYPE_EDITORIAL, u'Колонка редактора'),
    )

    author = models.ForeignKey(Author, related_name='entries')
    type = models.PositiveIntegerField(u'Тип записи', choices=TYPES, default=TYPE_BLOG, db_index=True)
    title = models.CharField(u'Название', max_length=255)
    caption = models.TextField(u'Подводка', null=True, blank=True)
    content = models.TextField(u'Содержание')
    created = models.DateTimeField(u'Дата создания')
    updated = models.DateTimeField(u'Дата обновления')
    visible = models.BooleanField(u'Опубликовано', default=False, db_index=True)
    show_until = models.DateField(u'Показывать до', blank=True, null=True)
    view_cnt = models.IntegerField(editable=False, default=0)
    comments_cnt = models.PositiveIntegerField(u'Комментариев', default=0)
    site = models.ForeignKey(Site, null=True,
                             blank=True, verbose_name=u'Раздел')
    gallery = ManyToGallerysField()

    class Meta:
        verbose_name = u'блог'
        verbose_name_plural = u'блоги'
        db_table = u'blogs_entries'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'news:blogs:read', (self.author.username, self.pk), {}

    def can_be_moderated_by(self, user):
        """Может ли пользователь модерировать комментарии для данного объекта"""

        return self.author.pk == user.pk


post_save.connect(invalidate, sender=BlogEntry)
post_save.connect(author_recount, sender=BlogEntry)


class UserBlogEntry(BlogEntry):
    objects = UserBlogEntryManager()
    is_user = True

    class Meta:
        proxy = True
        verbose_name = u'блог'
        verbose_name_plural = u'блоги'


post_save.connect(author_recount, sender=UserBlogEntry)


class AdminBlogEntry(BlogEntry):
    objects = AdminBlogEntryManager()
    is_admin = True

    class Meta:
        proxy = True
        verbose_name = u'колонка редактора'
        verbose_name_plural = u'колонки редакторов'
