# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from irk.profiles.options import options_library

register = template.Library()


class OptionNode(template.Node):
    def __init__(self, param, template=None, **kwargs):
        self.param = options_library[param]
        self.template = template or self.param.template
        self.extra_params = kwargs
        self.submit_url = reverse('profiles:set_option')

    def render(self, context):
        request = context['request']

        template_context = {
            'request': request,
            'next': request.build_absolute_uri(),
            'param': self.param(request),
            'set_option_url': self.submit_url,
        }
        template_context.update(self.extra_params)

        return render_to_string(self.template, template_context)


@register.tag
def option(parser, token):
    bits = token.split_contents()
    param_name = bits[1]
    options = {}
    for param in bits[2:]:
        if '.html' in param:
            options['template'] = param.strip('"').strip('\'')
        elif '=' in param:
            p = param.split('=')
            options[p[0]] = p[1]

    return OptionNode(param_name, **options)


class OptionValue(template.Node):

    def __init__(self, param, variable):
        self.param = param
        self.variable = variable

    def render(self, context):
        option = options_library[self.param]
        request = context.get('request')
        if not request:
            return option.default
        value = option(request).value

        if self.variable:
            context[self.variable] = value
            return ''
        else:
            return value


@register.tag
def option_value(parser, token):
    """Получить значение опции для пользователя"""

    bits = token.split_contents()

    param = bits[1].strip('"').strip("'")

    variable = None
    if bits[-2].lower() == 'as':
        variable = bits.pop(-1)
        del bits[-1]

    return OptionValue(param, variable)
