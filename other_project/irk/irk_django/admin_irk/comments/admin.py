# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.safestring import mark_safe

from irk.comments.models import Comment, SpamPattern, SpamIp, SpamLog


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('created', 'status', 'is_edited', 'display_user', 'display_title', 'text', 'get_url')
    ordering = ('-created',)
    actions = None
    list_display_links = None

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return Comment.objects.all().only('text', 'status', 'created', 'target_id', 'user_id')

    def display_title(self, obj):
        cache_key = 'comments.comment.{}.title'.format(obj.target_id)
        title = cache.get(cache_key)
        if title is None:
            try:
                title = obj.target
            except IndexError:
                title = ''
            cache.set(cache_key, title, 60 * 60 * 24)
        return title

    display_title.short_description = 'Материал'

    def display_user(self, obj):
        cache_key = 'auth.user.{}.username'.format(obj.user_id)
        username = cache.get(cache_key)
        if username is None:
            try:
                user = User.objects.get(pk=obj.user_id)
                username = str(user)
            except User.DoesNotExist:
                username = ''
            cache.set(cache_key, username, 60 * 60 * 24)
        return username

    display_user.short_description = 'Пользователь'

    def get_url(self, obj):
        return mark_safe('<a href="{}">Ссылка</a>'.format(obj.get_absolute_url()))

    get_url.short_description = 'Ссылка на комментарий'


@admin.register(SpamPattern)
class SpamPatternAdmin(admin.ModelAdmin):
    pass


@admin.register(SpamIp)
class SpamIpAdmin(admin.ModelAdmin):
    list_display = ('created', 'ip')


@admin.register(SpamLog)
class SpamLogAdmin(admin.ModelAdmin):
    list_display = ('created', 'user', 'ip', 'reason', 'text')
    readonly_fields = ('created', 'user', 'ip', 'reason', 'text')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
