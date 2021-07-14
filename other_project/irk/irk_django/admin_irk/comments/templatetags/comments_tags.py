# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging
import re

from django import template
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from irk.comments.helpers import content_type_for_comments
from irk.comments.models import ActionLog, Comment
from irk.comments.permissions import is_moderator
from irk.utils.exceptions import raven_capture
from irk.utils.templatetags import parse_arguments

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def comments(context, obj, preview=False):

    content_type = content_type_for_comments(obj)

    template_context = {
        'object': obj,
        'ct_id': content_type.pk,
        'comments_disabled': settings.COMMENTS_GLOBAL_DISABLED,
        'request': context.get('request'),
    }

    if preview:
        template_name = 'comments/tags/comments-loader-preview.html'
        txt = obj.comments.roots().visible().last()
        template_context['preview_comment'] = txt
    else:
        template_name = 'comments/tags/comments-loader.html'

    return render_to_string(template_name, template_context)


class AdminCommentMenu(template.Node):
    user = None

    def render(self, context):
        request = context['request']
        comment = context['comment']

        context = {
            'comment': get_object_or_404(Comment, pk=comment.pk),
            'has_history': ActionLog.objects.filter(comment=comment).exists(),
        }

        try:
            if is_moderator(request.user):
                return render_to_string('comments/tags/admin_comment_menu.html', context)
            else:
                raise Exception(request.path)
        except Exception as exc:
            raven_capture(exc)
            return ''


@register.tag('admin_comment_menu')
def do_admin_comment_menu(parser, token):
    return AdminCommentMenu()


class UserMenuNode(template.Node):
    def __init__(self, user, next_link=None, comment=None, ):
        self._user = user
        self._next_link = next_link
        self._comment = comment

    def render(self, context):
        request = context['request']
        user = self._resolve_param(self._user, context)
        comment = self._resolve_param(self._comment, context)
        next_link = self._resolve_param(self._next_link, context)

        if not user:
            return ''

        if not next_link:
            next_link = request.build_absolute_uri()

        data = {
            'user': user,
            'next': next_link,
            'comment': comment,
            'periods': settings.BAN_PERIODS,
        }

        if not is_moderator(request.user):
            return ''

        return render_to_string('comments/tags/user_menu.html', data)

    def _resolve_param(self, variable, context):
        """Выбрать значение параметра из контекста шаблона"""

        try:
            value = variable.resolve(context) if variable else None
            return value
        except (template.VariableDoesNotExist, AttributeError):
            return None


@register.tag('user_menu')
def do_user_menu(parser, token):
    """Меню пользователя

    Параметры:
        user - Пользователь, для которого делается меню
        next_link - url для редиректа.
        comment - комментарий пользователя.
    """

    bits = token.split_contents()

    args, kwargs = parse_arguments(parser, bits[1:])

    return UserMenuNode(*args, **kwargs)


class CommentsCountNode(template.Node):
    default_plural = u'отзыв, отзыва, отзывов'

    def __init__(self, args, kwargs):
        self._args = args
        self._kwargs = kwargs

    def render(self, context):

        if settings.COMMENTS_GLOBAL_DISABLED:
            return ''

        args = [arg.resolve(context) for arg in self._args]
        kwargs = {}
        for kwarg in self._kwargs:
            try:
                kwargs[kwarg] = kwarg.resolve(context)
            except AttributeError:
                kwargs[kwarg] = self._kwargs[kwarg].resolve(context)

        obj = args[0]

        if obj is None:
            logger.warning('`comments_cnt` template tag had received an None `obj` variable')
            return ''

        url = kwargs.get('url') or obj.get_absolute_url()
        url_params = kwargs.get('url_params')
        if url_params:
            url = u'{}?{}'.format(url, url_params)
        else:
            url = '{}#comments'.format(url)

        plural = kwargs.get('plural') or self.default_plural
        extra_class = kwargs.get('extra_class') or ''

        blank_label = None
        if kwargs.get('blank_label', '').lower().strip().strip('\'').strip('"') in ('1', 'true', 'yes'):
            blank_label = u'Написать %s' % plural.split(',')[0]

        new_card = kwargs.get('new_card')

        if 'new_layout' not in kwargs:
            template_name = 'comments/comment/comments_bubble.html'
        else:
            template_name = 'comments/comment/comments_count.html'

        return render_to_string(template_name, {
            'obj': obj,
            'plural': plural,
            'url': url,
            'blank_label': blank_label,
            'extra_class': extra_class,
            'new_card': new_card,
        })


@register.tag
def comments_cnt(parser, token):
    """Количество комментариев к записи

    Определяется по атрибуту comments_cnt объекта.
    Если привязанная тема форума удалена (считается, что комментарии отключены) - блок не выводится

    Позиционные параметры::
        obj - целевой объект

    Именованные параметры::
        plural - текст для фильтра pytils.numeral.choose_plural
        blank_label - выводить надпись «Написать отзыв», если нет отзывов
        url - ссылка на страницу объекта. Если не указана, используется get_absolute_url
        new_card - переменная для изменения отображения комментов в новых карточках

    Примеры использования::
        {% comments_cnt obj %}
        {% comments_cnt obj plural='комментарий, комментария, комментариев' %}
        {% comments_cnt obj plural='отзыв,отзыва,отзывов' blank_label=1 %}
        {% comments_cnt obj plural='отзыв,отзыва,отзывов' blank_label=false url=some_url_variable %}
        {% comments_cnt obj extra_class='class-name' %}
        {% comments_cnt obj new_layout %}
        {% comments_cnt obj new_layout url_params='#comments' %}
    """

    bits = token.split_contents()[1:]

    if not bits:
        raise template.TemplateSyntaxError(u'В тег {% comments_cnt %} должен быть передан хоть один параметр')

    args, kwargs = parse_arguments(parser, bits)

    return CommentsCountNode(args, kwargs)


@register.filter
def strip_forum_tags(text):
    """Убираем теги, которые используются в форуме, но не используются, например
    в новостях.

    TODO: Не вырезает вложенные [q]..[/q]"""

    return re.sub(ur'\[q\].*?\[\/q\]', '', text, re.M)
