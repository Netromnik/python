# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404
from django.core.urlresolvers import reverse

from irk.news.models import Infographic
from irk.news.permissions import is_moderator
from irk.news.helpers import get_image_parts
from irk.hitcounters.actions import hitcounter


def index(request):
    """Главная инфографики"""

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    infographics = Infographic.material_objects.order_by('-stamp')
    moderator = is_moderator(request.user)
    if not moderator:
        infographics = infographics.filter(is_hidden=False)

    paginate = Paginator(infographics, 10)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(paginate.num_pages)

    context = {
        'objects': objects,
    }

    if request.is_ajax():
        template = 'news-less/infographic/snippets/entries.html'
    else:
        template = 'news-less/infographic/index.html'

    return render(request, template, context)


def read(request, infographic_id):
    """Страница инфографики"""

    infographic = get_object_or_404(Infographic, pk=infographic_id)
    moderator = is_moderator(request.user)
    if not moderator and infographic.is_hidden:
        raise Http404()

    hitcounter(request, infographic)

    images = []
    if request.user_agent.device.family in ('iPad', 'iPhone', 'iPod'):
        images = get_image_parts(infographic.image.path)

    latest_qs = Infographic.material_objects.filter(is_hidden=False).exclude(id=infographic.id).order_by('-stamp')
    paginator = Paginator(latest_qs, 3)
    try:
        latest = paginator.page(1)
    except EmptyPage:
        latest = ()

    context = {
        'object': infographic,
        'images': images,
        'latest': latest,
        'exclude_pk': infographic.id,
    }

    return render(request, 'news-less/infographic/read.html', context)


def paginator(request):

    limit = 3

    try:
        exclude_pk = int(request.GET.get('exclude_pk', 0))
    except ValueError:
        exclude_pk = 0

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        infographic_pks = list(Infographic.material_objects.filter(is_hidden=False).\
            order_by('-stamp').values_list('pk', flat=True))
        page = int(infographic_pks.index(exclude_pk) / limit)

    infographics = Infographic.material_objects.filter(is_hidden=False).exclude(pk=exclude_pk).order_by('-stamp')

    paginate = Paginator(infographics, limit)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(1)

    context = {
        'objects': objects,
        'exclude_pk': exclude_pk
    }

    return render(request, 'news-less/infographic/entries.html', context)
