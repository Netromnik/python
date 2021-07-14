# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.utils.safestring import mark_safe

from models import Page

DEFAULT_TEMPLATE = 'pages/default.html'

logger = logging.getLogger(__name__)


def flatpage(request, url):
    # Если запрос не обрабатывался по нормальному,
    # то и простых страниц для него нет
    if not hasattr(request, 'csite'):
        raise Http404

    if not url.endswith('/') and settings.APPEND_SLASH:
        return HttpResponseRedirect("%s/" % request.path)

    if not url.startswith('/'):
        url = "/" + url

    if request.csite.url != url:
        url = '/%s' % (url.replace(request.csite.url, '').lstrip("/"))

    try:
        f = Page.objects.get(url__exact=url, site=request.csite.site)
    except Page.DoesNotExist:
        logger.debug(u'Page not exist: URL `{}`, search URL: {}, site {}, request type {}'.
                     format(request.build_absolute_uri(), url, request.csite.site.pk, request.csite.request_type))
        raise Http404()

    if f.template_name:
        t = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    f.title = mark_safe(f.title)

    f.content = mark_safe(f.content)

    # Слаг для посадочной таблицы
    try:
        f.slug = f.url.strip('/').split('/')[-1]
    except IndexError:
        f.slug = ''

    c = {
        'flatpage': f,
    }
    response = HttpResponse(t.render(c, request))
    return response
