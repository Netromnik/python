# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.shortcuts import render

from irk.comments.models import Comment
from irk.obed.models import Establishment
from irk.phones.models import Firms
from irk.utils.helpers import int_or_none


def recent_messages(request):
    page_number = int_or_none(request.GET.get('page')) or 1
    page_limit = int_or_none(request.GET.get('limit')) or 3

    firms_ids = list(Establishment.objects.filter(is_active=True, visible=True,
                                                  disable_comments=False).values_list('pk', flat=True))
    firms_ct = ContentType.objects.get_for_model(Firms)

    comments = Comment.objects.filter(target_id__in=firms_ids, content_type=firms_ct,
                                      status=Comment.STATUS_VISIBLE, parent_id__isnull=True).order_by('-created')

    paginator = Paginator(comments, page_limit)
    try:
        page_obj = paginator.page(page_number)
    except InvalidPage:
        raise Http404()

    context = {
        'page_obj': page_obj,
        'object_list': page_obj.object_list,
    }

    return render(request, 'obed/comments/list.html', context)
