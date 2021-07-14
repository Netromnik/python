# -*- coding: utf-8 -*-

import datetime

from django import template
from django.template.loader import render_to_string

from irk.contests.models import Contest
from irk.news.models import Block
from irk.utils.helpers import get_object_or_none
from irk.utils.templatetags import parse_arguments
from irk.news.permissions import is_moderator

register = template.Library()


class ContestNode(template.Node):
    def __init__(self, template):
        self.template = template

    def render(self, context):
        request = context.get('request')
        try:
            contest = Contest.objects.filter(sites=request.csite, date_start__lte=datetime.date.today(),
                                             date_end__gte=datetime.date.today()).order_by('?')[0]
        except IndexError:
            return ''

        context = {'contest': contest}

        return render_to_string(self.template, context, request)


@register.tag
def contest_latest(parser, token):
    """Последний конкурс, привязанный к разделу"""

    args, kwargs = parse_arguments(parser, token.split_contents()[1:])

    if 'template' in kwargs:
        template = str(kwargs['template']).strip('"\'')
    else:
        template = 'contests/tags/latest.html'

    return ContestNode(template)


@register.simple_tag
def participant_meta_title(participant):
    """Возвращает название для meta заголовка с учетом типа конкурса"""

    if participant.contest.type == participant.contest.TYPE_INSTAGRAM:
        title = u'@{}'.format(participant.username)
    else:
        title = participant.title
    return title


@register.inclusion_tag('contests/tags/sidebar_materials.html', takes_context=True)
def contests_sidebar_materials(context, count=3):
    """Блок материалов в правой колонке"""

    request = context.get('request')
    if not request:
        return {}

    block = get_object_or_none(Block, slug='news_index_sidebar')
    if not block:
        return {}

    materials = []
    for position in block.positions.all():
        if not position.material:
            continue
        if not is_moderator(request.user) and position.material.is_hidden:
            continue
        materials.append(position.material)

    show_banner = not bool(context.get('opened'))

    if show_banner:
        count -= 1

    return {
        'materials': materials[:count],
        'show_banner': show_banner
    }
