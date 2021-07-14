# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, InvalidPage, Paginator

from irk.profiles.models import Bookmark
from irk.news.models import BaseMaterial
from irk.utils.http import JsonResponse

logger = logging.getLogger(__name__)


@login_required
def index(request):
    """Список закладок"""

    limit = 10

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    bookmarks = Bookmark.objects.filter(user_id=request.user.id).order_by('-created')

    paginate = Paginator(bookmarks, limit)

    try:
        bookmarks = paginate.page(page)
    except (EmptyPage, InvalidPage):
        bookmarks = paginate.page(paginate.num_pages)

    return render(request, 'profiles/bookmarks/index.html', {'bookmarks': bookmarks})


@login_required
def add(request):
    """Добавление закладки"""

    if request.POST:
        ct_id = request.POST.get('ct_id')
        target_id = request.POST.get('target_id')

        try:
            ct = ContentType.objects.get(pk=ct_id)
            target = ct.get_object_for_this_type(pk=target_id)
        except (ObjectDoesNotExist, AttributeError):
            return HttpResponseBadRequest()

        if not isinstance(target, BaseMaterial):
            return HttpResponseBadRequest()

        bookmark, created = Bookmark.objects.get_or_create(user=request.user, content_type=ct, target_id=target.pk)
        bookmark.save()
        return JsonResponse({'result': 'ok', 'id': bookmark.pk})

    return HttpResponseBadRequest()


@login_required
def remove(request):
    """Удаление закладки"""

    if request.POST:
        bookmark_id = request.POST.get('bookmark_id')

        bookmark = get_object_or_404(Bookmark, pk=bookmark_id, user_id=request.user.id)
        bookmark.delete()

        return JsonResponse({'result': 'ok'})

    return HttpResponseBadRequest()
