# -*- coding: utf-8 -*-

from django import template
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache

from irk.utils.metrics import NewrelicTimingMetric
from irk.utils import settings as app_settings


register = template.Library()


@register.tag('timing_metric')
def do_newrelic_record_timing(parser, token):
    try:
        tag_name, metric_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Не указано название метрики")

    metric_name = metric_name.strip('"').strip("'")
    nodelist = parser.parse(('end_timing_metric',))
    parser.delete_first_token()

    return NewrelicRecordTimingNode(nodelist, metric_name)


class NewrelicRecordTimingNode(template.Node):
    def __init__(self, nodelist, metric_name):
        self.nodelist = nodelist
        self.metric_name = metric_name

    def render(self, context):
        with NewrelicTimingMetric('Custom/%s' % self.metric_name):
            return self.nodelist.render(context)


@register.simple_tag(takes_context=True)
def ravenjs(context):
    """Подключение скрипта raven.js на страницу, инициализация с настройками из `utils.settings.RAVENJS_SETTINGS`"""

    if settings.DEBUG or not getattr(settings, 'SENTRY_RAVENJS_URI', None):
        return ''

    request = context['request']

    key = 'utils.ravenjs.%d' % request.user.id if request.user.is_authenticated else 0
    value = cache.get(key)
    if value is None:
        template_context = {
            'user': request.user,
            'url': settings.SENTRY_RAVENJS_URI,
            'settings': app_settings.RAVENJS_SETTINGS,
        }

        value = render_to_string('utils/ravenjs.html', template_context)

        cache.set(key, value, 60 * 60 * 24)

    return value
