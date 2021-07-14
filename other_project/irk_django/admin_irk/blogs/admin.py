# -*- coding: utf-8 -*-

import datetime

from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import connection, transaction
from django.contrib import messages

from irk.blogs.models import BlogEntry, UserBlogEntry, Author
from irk.blogs.forms import BlogEntryAdminForm, AuthorAdminForm, AuthorCreateAdminForm

from irk.gallery.admin import GalleryBBCodeInline
from irk.utils.files.admin import admin_media_static


class UserBlogEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'visible', 'created')
    list_select_related = True
    form = BlogEntryAdminForm
    inlines = (GalleryBBCodeInline,)
    ordering = ('-created',)

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
            'js/lib/select2.min.js',
            'js/lib/heavy_data.js',
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
            obj.type = BlogEntry.TYPE_BLOG
            obj.created = datetime.datetime.now()
        obj.updated = datetime.datetime.now()
        obj.save()


admin.site.register(UserBlogEntry, UserBlogEntryAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_visible', 'is_operative', 'entries_cnt', 'comments_cnt', 'date_started')
    form = AuthorAdminForm
    ordering = ('-date_started',)

    @admin_media_static
    class Media(object):
        js = (
            'js/apps-js/admin.js',
            'js/lib/select2.min.js',
            'js/lib/heavy_data.js',
        )

    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):

        if request.POST:
            form = AuthorCreateAdminForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                cursor = connection.cursor()

                cursor.execute('SELECT COUNT(*) AS cnt FROM blogs_authors WHERE user_ptr_id = %s', (user.pk,))
                is_exists = cursor.fetchone()[0] > 0
                if is_exists:
                    return HttpResponseRedirect('..')

                cursor.execute('''INSERT INTO blogs_authors (
                    user_ptr_id, date_started, is_visible, entries_cnt, subscribers_cnt, comments_cnt, is_operative
                ) VALUES (%s, %s, 1, 0, 0, 0, 1)''', (user.pk, datetime.date.today()))

                messages.add_message(request, messages.SUCCESS,
                                     u'Пользователь %s добавлен в авторы блогов' % user.username)

                return HttpResponseRedirect('..')

        else:
            form = AuthorCreateAdminForm()

        context = {
            'form': form,
            'opts': Author._meta,
            'change': False,
            'is_popup': False,
            'save_as': False,
            'has_delete_permission': False,  # TODO: возможно, понадобится
            'has_add_permission': True,  # TODO: возможно, понадобится
            'has_change_permission': True,  # TODO: возможно, понадобится
            'add': True,
            'media': self.media + form.media,
        }

        context.update(extra_context or {})

        return render(request, 'admin/blogs/author/add.html', context)

    @transaction.atomic
    def delete_model(self, request, obj):
        cursor = connection.cursor()
        cursor.execute('UPDATE blogs_authors SET is_visible = 0 WHERE user_ptr_id = %s', (obj.pk,))

        messages.add_message(request, messages.SUCCESS, u'Пользователь %s перестал быть автором блогов' % obj.username)


admin.site.register(Author, AuthorAdmin)
