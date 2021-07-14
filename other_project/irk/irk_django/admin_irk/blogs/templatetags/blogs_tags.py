# -*- coding: utf-8 -*-

import datetime
import random

from django import template
from django.template.loader import render_to_string

from irk.blogs.models import Author
from irk.blogs.models import BlogEntry


register = template.Library()


class LatestEntryNode(template.Node):
    def __init__(self, type_, amount, newmakeup):
        self.type = type_
        self.amount = amount
        self.newmakeup = newmakeup

    def render(self, context):

        request = context.get('request')

        entries = BlogEntry.objects.filter(type=self.type, visible=True, author__is_visible=True,
                                           site=request.csite).select_related('author')
        if self.type == BlogEntry.TYPE_EDITORIAL:
            entries = entries.filter(show_until__gte=datetime.date.today())

        #Показывать будем только один блок, поэтому чтобы на заморачиваться на сортировку
        #случайным образом просто слайсом отрежем
        offset = random.randint(1, 3)
        entries = entries.order_by('-id')[offset - 1:offset]

        template_suffix = '_newmakeup' if self.newmakeup else ''

        if self.type == BlogEntry.TYPE_BLOG:
            return render_to_string('blogs/snippets/blog_entry%s.html' % template_suffix, {'entries': entries})
        return render_to_string('blogs/snippets/editorial_entry%s.html' % template_suffix, {'entries': entries})


@register.tag
def latest_blog_entries(parser, token):
    """Последние записи блога/колонки редактора

    {% latest_blog_entries 'blog' 1 %}
    {% latest_blog_entries 'editorial' 5 %}
    {% latest_blog_entries 'editorial' 5 newmakeup %}
    """

    newmakeup = False
    try:
        tag, type_, amount, newmakeup = token.split_contents()
        newmakeup = bool(newmakeup)
    except(TypeError, ValueError):
        tag, type_, amount = token.split_contents()

    type_ = type_.strip('\'').strip('"')
    if type_ not in ('blog', 'editorial'):
        raise template.TemplateSyntaxError(u'Неправильный тип для записей блога')
    type_ = BlogEntry.TYPE_BLOG if type_ == 'blog' else BlogEntry.TYPE_EDITORIAL

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        raise template.TemplateSyntaxError(u'Некорректное количество записей блога')

    return LatestEntryNode(type_, amount, newmakeup)


@register.inclusion_tag('blogs/tags/sidebar-block.html')
def blog_sidebar_block(limit=1, **kwargs):
    """
    Вывод блока с блогом в сайдбаре

    :param int limit: количество записей
    """

    entries = BlogEntry.objects \
        .filter(type=BlogEntry.TYPE_BLOG, author__is_visible=True, visible=True) \
        .order_by('-id') \
        .select_related('author') \
        .defer('content')[:limit]

    kwargs['entries'] = entries
    return kwargs


@register.inclusion_tag('blogs/tags/author-new.html')
def blog_new_author():
    """Блок нового автора"""

    period = datetime.datetime.now() - datetime.timedelta(days=14)

    try:
        author = Author.objects.filter(date_started__gte=period, entries_cnt__gt=0, is_visible=True).order_by('?')[0]
    except IndexError:
        return {}

    entry = BlogEntry.objects.filter(author=author).order_by('?')[0]

    return {
        'author': author,
        'entry': entry,
    }
