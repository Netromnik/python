# -*- coding: utf-8 -*-

import os
import logging

from django import template
from django.conf import settings
from django.contrib.staticfiles.finders import find

from irk.utils import settings as app_settings
from irk.utils.files.helpers import static_link


logger = logging.getLogger(__name__)

register = template.Library()
cache = {}


class LessNode(template.Node):
    _less_pattern = '<link rel="stylesheet/less" type="text/css" media="%s" href="%s">'
    _css_pattern = '<link rel="stylesheet" type="text/css" media="%s" href="%s">'

    def __init__(self, path, media):
        self._path = template.Variable(path)
        self._media = media

    def render(self, context):
        path = self._path.resolve(context)
        path = path.strip('\'').strip('"').lstrip('/')

        # кеш
        if not settings.DEBUG_LESS and path in cache:
            return cache[path]

        self._less_path = find(path)

        if not self._less_path:
            if settings.DEBUG_LESS:
                raise ValueError(u'Can not find less file: {}'.format(path))
            else:
                return ''

        if os.path.exists(self._less_path):
            self._less_url = os.path.join(settings.STATIC_URL, path)

        for directory in settings.STATICFILES_DIRS:
            self._less_path = self._less_path.replace(directory, '')

        if settings.DEBUG_LESS:
            return self._less_pattern % (self._media, self._less_url)

        filename = os.path.splitext(self._less_path.replace('less/', '').lstrip('/'))[0]
        self._css_path = os.path.join(app_settings.LESS_OUTPUT_DIR, '%s.css' % filename)
        self._css_url = static_link(os.path.join(app_settings.LESS_OUTPUT_URL, '%s.css' % (filename,)))

        result = self._css_pattern % (self._media, self._css_url)

        cache[path] = result
        return result


@register.tag
def less(parser, token):
    """Less файл

    Примеры использования::
        {% less '/less/compile/style.less' %}
        {% less '/forum/less/forum.less' media='print' %}
    """

    bits = token.split_contents()[1:]

    try:
        path = bits[0]
    except IndexError:
        raise template.TemplateSyntaxError(u'В тег {% less %} должен передаваться параметр с именем файла')

    media = 'all'
    if len(bits) > 1:
        media = bits[1].replace('media=', '').strip().strip('\'').strip('"')

    return LessNode(path, media)
