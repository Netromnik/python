# -*- coding: utf-8 -*-

import collections

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.db import connection

from irk.newyear2014.permissions import is_moderator
from irk.news.models import Photo, Article


def photo(request):
    return HttpResponseRedirect(reverse('newyear2014.views.articles.index'))


def articles_and_photos_chain(site, show_hidden=False, start_idx=0, limit=20, photo_queryset=None, article_queryset=None):
    """Копипаста из `news.helpers.news_and_infographics_chain`.
    Нужен для того, чтобы выводить в одной ленте и фоторепортажи и статьи"""

    query = ['''
        (
            SELECT "photo" AS `model`, `news_photo`.`id`, `news_photo`.`stamp`
            FROM `news_photo`
            WHERE
                FIND_IN_SET(%(site_id)s, `news_photo`.`serialized_sites`) > 0
    ''']

    if not show_hidden:
        query.append(' AND is_hidden = 0 ')

    query.append('''
            ORDER BY stamp DESC, id DESC
        ) UNION (
            SELECT "article" AS `model`, `news_article`.`id`, `news_article`.`stamp`
            FROM `news_article`
            WHERE
                FIND_IN_SET(%(site_id)s, `news_article`.`serialized_sites`) > 0

    ''')

    if not show_hidden:
        query.append(' AND is_hidden = 0 ')

    query.append('''
            ORDER BY stamp DESC, id DESC
        )
        ORDER BY stamp DESC, id DESC
        LIMIT %(start_idx)s, %(limit)s;
    ''')

    cursor = connection.cursor()
    cursor.execute(' '.join(query), {
        'site_id': site.id,
        'start_idx': start_idx,
        'limit': limit,
    })

    model_ids = collections.defaultdict(list)
    object_ids = []
    for obj in cursor.fetchall():
        model, object_id = obj[:2]
        model_ids[model].append(object_id)
        # Внимание, здесь может быть коллизия идентификаторов
        object_ids.append((model, object_id))

    last_objects = []

    if photo_queryset is None:
        photo_queryset = Photo.material_objects.all()
    last_objects += photo_queryset.filter(id__in=model_ids['photo']).extra(select={'model': '"photo"'})

    if article_queryset is None:
        article_queryset = Article.material_objects.all()
    last_objects += article_queryset.filter(id__in=model_ids['article']).extra(select={'model': '"article"'})

    def compare(obj):
        model_name = obj._meta.object_name.lower()
        return object_ids.index((model_name, obj.id))

    return sorted(last_objects, key=compare)


def index(request):

    articles_qs = Article.material_objects.filter(sites=request.csite)
    photos_qs = Photo.material_objects.filter(sites=request.csite)
    articles_cnt = articles_qs.count()
    photos_cnt = photos_qs.count()

    try:
        limit = int(request.GET.get('limit'))
    except (TypeError, ValueError):
        limit = 20

    iterator = range(articles_cnt + photos_cnt)
    paginator = Paginator(iterator, limit)

    try:
        objects = paginator.page(request.GET.get('page'))
    except (EmptyPage, PageNotAnInteger):
        objects = paginator.page(1)

    try:
        start_idx = min(objects.object_list)
    except ValueError:
        raise Http404()

    moderator = is_moderator(request.user)

    queryset = articles_and_photos_chain(request.csite, moderator, start_idx, limit, photo_queryset=photos_qs,
        article_queryset=articles_qs)

    objects.object_list = queryset

    context = {
        'objects': objects,
    }

    return render(request, 'newyear2014/article/index.html', context)
