# -*- coding: utf-8 -*-

import urllib2

from django import template
from django.core.urlresolvers import reverse

register = template.Library()


def base_search_form(context, action, placeholder):
    # TODO: docstring
    request = context['request']
    if not action:
        raise ValueError(u'Нужно указать action формы')
    else:
        action = action.strip('"').strip('\'')

    try:
        action = reverse(action)
    except Exception:
        # TODO: Какие исключения вызывает?
        pass

    return {
        'q': urllib2.unquote(request.GET.get('q', '').encode('utf-8')),
        'url': action,
        'placeholder': placeholder.strip('"').strip('\'')
    }


def search_form(context, action=None, placeholder=''):
    # TODO: docstring
    return base_search_form(context, action, placeholder)


register.inclusion_tag('snippets/search_form.html', takes_context=True, name='search_form')(search_form)
