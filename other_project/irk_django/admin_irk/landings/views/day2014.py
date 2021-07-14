# -*- coding: utf-8 -*-

import StringIO

from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string

from irk.externals.models import InstagramTag, InstagramMedia


HASHTAG_NAME = u'мойиркутск'


def index(request):
    try:
        tag = InstagramTag.objects.get(name=HASHTAG_NAME)
    except InstagramTag.DoesNotExist:
        images = ()
    else:
        images = InstagramMedia.objects.filter(is_visible=True, tags=tag).order_by('-id')[:5]

    context = {
        'images': list(images),
    }

    return render(request, 'landings/day2014/index.html', context)


def instagram(request):
    try:
        tag = InstagramTag.objects.get(name=HASHTAG_NAME)
    except InstagramTag.DoesNotExist:
        images = ()
    else:
        images = InstagramMedia.objects.filter(is_visible=True, tags=tag).order_by('-id')[:5]

    context = {
        'images': images,
    }

    return render(request, 'landings/day2014/instagram.html', context)


def instagram_more(request):
    try:
        max_id = int(request.GET.get('max_id'))
    except (ValueError, TypeError):
        return HttpResponseBadRequest()

    try:
        tag = InstagramTag.objects.get(name=HASHTAG_NAME)
    except InstagramTag.DoesNotExist:
        images = ()
    else:
        images = InstagramMedia.objects.filter(is_visible=True, tags=tag, id__lt=max_id).order_by('-id')[:5]

    output = StringIO.StringIO()

    for image in images:
        output.write(render_to_string('landings/day2014/instagram-list-item.html', {
            'image': image,
        }))

    return HttpResponse(output.getvalue())
