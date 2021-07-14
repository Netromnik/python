# -*- coding: utf-8 -*-

"""Блоги"""

import datetime

from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from irk.blogs.forms import BlogEntryForm
from irk.blogs.models import Author, UserBlogEntry
from irk.blogs.permissions import is_blog_author, can_edit_blog
from irk.gallery.forms.helpers import gallery_formset
from irk.hitcounters.actions import hitcounter
from irk.utils.decorators import deprecated


def index(request):
    """Последние записи"""

    try:
        page = int(request.GET.get('page'))
    except (TypeError, ValueError):
        page = 1

    queryset = UserBlogEntry.objects.filter(visible=True,
                                            author__is_visible=True).order_by('-created').select_related('author')

    paginator = Paginator(queryset, 20)

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(1)

    context = {
        'objects': objects,
        'user_is_author': is_blog_author(request.user),
    }

    if request.is_ajax():
        template = 'news-less/blogs/snippets/index-entries.html'
    else:
        template = 'news-less/blogs/index.html'

    return render(request, template, context)


def authors(request):
    """Список всех авторов"""

    try:
        page = request.GET.get('page')
    except (TypeError, ValueError):
        page = 1

    queryset = Author.objects.filter(is_visible=True, is_active=True, entries_cnt__gt=0).extra(
        select={
            'post_date': '''SELECT created FROM blogs_entries
                            WHERE author_id = blogs_authors.user_ptr_id
                            ORDER BY created DESC LIMIT 1'''
        },
        order_by=['-post_date'],
    ).select_related('user_ptr')
    paginator = Paginator(queryset, 20)

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(1)

    context = {
        'objects': objects,
    }

    if request.is_ajax():
        template = 'news-less/blogs/snippets/authors-entries.html'
    else:
        template = 'news-less/blogs/authors.html'

    return render(request, template, context)


def author(request, username):
    """Список записей автора"""

    author_ = get_object_or_404(Author, username=username, is_visible=True)

    try:
        page = int(request.GET.get('page'))
    except (TypeError, ValueError):
        page = 1

    queryset = UserBlogEntry.objects.filter(author=author_, visible=True).order_by('-created').select_related('author')

    paginator = Paginator(queryset, 20)

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(1)

    context = {
        'author': author_,
        'objects': objects,
        'user_is_author': can_edit_blog(request.user, author_),
    }

    if request.is_ajax():
        template = 'news-less/blogs/snippets/author-entries.html'
    else:
        template = 'news-less/blogs/author.html'

    return render(request, template, context)


def read(request, username, entry_id):
    """Просмотр записи блога"""

    author_ = get_object_or_404(Author, username=username, is_visible=True)
    entry = get_object_or_404(UserBlogEntry, author=author_, pk=entry_id)
    if not entry.visible and getattr(request.user, 'pk', None) != entry.author_id:
        return HttpResponseForbidden()

    # Считаем счетчик просмотров
    # Для всех, кроме автора
    if getattr(request.user, 'pk', None) != entry.author_id:
        hitcounter(request, entry)

    context = {
        'author': author_,
        'entry': entry,
        'user_is_author': can_edit_blog(request.user, entry),
    }

    return render(request, 'news-less/blogs/read.html', context)


def create(request, username):
    """Создание новой записи в блоге"""

    author_ = get_object_or_404(Author, username=username, is_active=True, is_visible=True, is_operative=True)
    if not getattr(request.user, 'pk', None) == author_.pk:
        return HttpResponseForbidden()

    if request.POST:
        form = BlogEntryForm(request.POST)
        gallery_form = gallery_formset(request.POST, request.FILES, instance=UserBlogEntry(), user=request.user)
        if form.is_valid() and gallery_form.is_valid():
            instance = form.save(commit=False)
            instance.author = author_
            instance.type = UserBlogEntry.TYPE_BLOG
            instance.created = datetime.datetime.now()
            instance.updated = datetime.datetime.now()
            instance.visible = True
            instance.save()

            gallery_form.original_instance = instance
            gallery_form.save()

            return redirect(reverse('news:blogs:read', args=[username, instance.pk]))

    else:
        form = BlogEntryForm()
        gallery_form = gallery_formset(instance=UserBlogEntry(), user=request.user)

    context = {
        'author': author_,
        'form': form,
        'gallery_form': gallery_form,
    }

    return render(request, 'news-less/blogs/create.html', context)


def update(request, username, entry_id):
    """Редактирование записи"""

    author_ = get_object_or_404(Author, username=username, is_active=True, is_visible=True, is_operative=True)
    entry = get_object_or_404(UserBlogEntry, author=author_, pk=entry_id)
    if not getattr(request.user, 'pk', None) == author_.pk:
        return HttpResponseForbidden()

    if request.POST:
        form = BlogEntryForm(request.POST, instance=entry)
        gallery_form = gallery_formset(request.POST, request.FILES, instance=entry)
        if form.is_valid() and gallery_form.is_valid():
            instance = form.save(commit=False)
            instance.author = author_
            instance.type = UserBlogEntry.TYPE_BLOG
            instance.updated = datetime.datetime.now()
            instance.visible = True
            instance.save()

            gallery_form.save()

            return redirect(reverse('news:blogs:read', args=[username, instance.pk]))

    else:
        form = BlogEntryForm(instance=entry)
        gallery_form = gallery_formset(instance=entry)

    context = {
        'author': author_,
        'object': object,
        'form': form,
        'gallery_form': gallery_form,
    }

    return render(request, 'news-less/blogs/update.html', context)


@deprecated
def publish(request, username, entry_id):
    """Публикация скрытой записи"""

    author_ = get_object_or_404(Author, username=username, is_active=True, is_visible=True, is_operative=True)
    entry = get_object_or_404(UserBlogEntry, author=author_, pk=entry_id)
    if not request.user.pk == author_.pk:
        return HttpResponseForbidden()

    entry.visible = True
    entry.save()

    return HttpResponseRedirect(entry.get_absolute_url())
