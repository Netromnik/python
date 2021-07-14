# -*- coding: utf-8 -*-

import types

from django.template import Library
from django.template.loader import render_to_string
from django import template
from django.conf import settings

from irk.utils import settings as app_settings
from irk.comments.helpers import content_type_for_comments
from irk.profiles.models import Bookmark

register = Library()


class ShareNode(template.Node):
    def __init__(self, obj, template='buttons/share.html'):
        self._obj = obj
        self._template = template

    def render(self, context):
        if not app_settings.SHARE_BUTTONS_SHOW:
            return ''

        request = context.get('request')
        obj = self._obj

        if isinstance(obj, types.StringTypes):
            obj = template.Variable(obj).resolve(context)

        url = request.build_absolute_uri(str(obj.get_absolute_url()))

        template_context = {
            'obj': obj,
            'url': url,
            # TODO: заменить на `request.scheme` после обновления django
            'request_scheme': 'https' if settings.FORCE_HTTPS else 'http'
        }

        return render_to_string(self._template, template_context, request=request)


@register.tag
def share(parser, token):
    """Кнопки для расшаривания контента в сервисах:
      - Twitter
      - Вконтакте
      - Facebook
    {% share news_object %}
    {% share news_object 'buttons/share_vertical.html' %}"""

    parts = token.split_contents()
    if len(parts) == 2:
        return ShareNode(parts[1])
    elif len(parts) == 3:
        return ShareNode(parts[1], parts[2].strip('"').strip("'"))

    raise template.TemplateSyntaxError(u'Два или три аттрибута у тега {% share %}')


@register.inclusion_tag('buttons/share_custom.html', takes_context=True)
def share_custom(context, **kwargs):
    """Кастомный шаблон для социальных кнопок"""

    request = context.get('request')
    kwargs['request'] = request

    obj = kwargs.get('object')

    if obj:
        ct = content_type_for_comments(obj)

        bookmark_obj = Bookmark.objects.filter(user_id=request.user.pk, content_type_id=ct.pk, target_id=obj.pk).first()

        kwargs['target_id'] = obj.pk
        kwargs['ct_id'] = ct.pk
        kwargs['bookmark'] = bookmark_obj

    return kwargs


@register.inclusion_tag('buttons/bookmark.html', takes_context=True)
def bookmark(context, obj):
    """Кнопка добавления закладки"""

    request = context.get('request')

    ct = content_type_for_comments(obj)

    bookmark_obj = Bookmark.objects.filter(user_id=request.user.pk, content_type_id=ct.pk, target_id=obj.pk).first()

    return {'object': obj, 'ct': ct, 'bookmark': bookmark_obj, 'request': request}
