# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string

from irk.externals.models import InstagramMedia, InstagramTag
from irk.utils.http import JsonResponse


def instagram_tag(request, tag_id):
    """Страница списка фотографий тега"""

    tag = get_object_or_404(InstagramTag, pk=tag_id, is_visible=True)

    queryset = InstagramMedia.objects.filter(is_visible=True, tags=tag).order_by('-id')
    limit = 10
    has_next = queryset.count() > limit
    images = queryset[:limit]

    context = {
        'tag': tag,
        'images': images,
        'has_next': has_next,
    }

    return render(request, 'newyear2014/instagram/tag.html', context)


def instagram_more(request, tag_id):
    """Ajax endpoint для страницы списка фотографий тега"""

    try:
        max_id = int(request.GET.get('max_id'))
    except (ValueError, TypeError):
        return HttpResponseBadRequest()

    tag = get_object_or_404(InstagramTag, pk=tag_id, is_visible=True)

    limit = 10

    queryset = InstagramMedia.objects.filter(is_visible=True, tags=tag, id__lt=max_id).order_by('-id')
    has_next = queryset.count() > limit
    images = queryset[:limit]

    html = u''
    for image in images:
        html += render_to_string('newyear2014/instagram/instagram-list-item.html', {'image': image, 'tag': tag})

    return JsonResponse({
        'html': html,
        'has_next': has_next,
    })
