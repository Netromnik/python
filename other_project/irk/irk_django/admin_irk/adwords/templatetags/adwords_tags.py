# -*- coding: utf-8 -*-

import datetime

from django import template
from django.template.loader import render_to_string

from irk.adwords.models import AdWordPeriod, CompanyNewsPeriod

from irk.utils.templatetags import parse_arguments

register = template.Library()


class MultipleSiteAdWord(template.Node):
    def __init__(self, limit, template, variable):
        self.limit = int(limit)
        self.template = template
        self.variable = variable

    def render(self, context):
        request = context['request']
        today = datetime.date.today()

        periods = AdWordPeriod.objects.filter(start__lte=today, end__gte=today,
                                              adword__sites=request.csite).select_related('adword').order_by('-pk')
        adwords = list(set(x.adword for x in periods))[:self.limit]

        if len(adwords):
            data = render_to_string(self.template, {'adwords': adwords})
        else:
            data = ''

        if self.variable:
            context[self.variable] = data
            return ''
        return data


@register.tag('site_adwords')
def do_site_adwords(parser, token):
    """
    {% site_adwords 2 %}
    {% site_adwords 2 variable='adwords' %}
    {% site_adwords 2 template='adwords/tags/inline_multiple_adwords.html' %}
    """

    args, kwargs = parse_arguments(parser, token.split_contents()[1:])

    try:
        limit = int(args[0].token)
    except (IndexError, TypeError, AttributeError):
        limit = 2

    if 'template' in kwargs:
        template = str(kwargs['template']).strip('"\'')
    else:
        template = 'adwords/tags/multiple_adwords.html'

    if 'variable' in kwargs:
        variable = str(kwargs['variable']).strip('"\'')
    else:
        variable = None

    return MultipleSiteAdWord(limit, template, variable)


@register.inclusion_tag("company_news/tags/inline.html", )
def company_news(show_title=False, ):
    today = datetime.date.today()
    periods = CompanyNewsPeriod.objects.filter(
        news__is_hidden=False,
        start__lte=today,
        end__gte=today, ).select_related('news').order_by('-pk')
    news = list(set(x.news for x in periods))[:2]
    return {
        'news': news,
        'show_title': bool(show_title),
    }
