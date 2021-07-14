# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse_lazy
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def login_form(context):
    """Блок всплывающей авторизации на всех страницах"""

    request = context['request']

    if request.user.is_authenticated:
        return ''

    context = {
        'request': request,
    }

    return render_to_string('auth/tags/login-form.html', context, request)


@register.inclusion_tag('auth/tags/auth_tabs.html', takes_context=True)
def auth_tabs(context):
    """Рубрикатор между типами публикаций в центральной колонке"""

    request = context['request']

    auth_urls = (
        (request.user.profile.get_absolute_url(), u'Публичный профиль'),
        (reverse_lazy('authentication:profile:update'), u'Редактировать профиль'),
        (reverse_lazy('profiles:bookmark:index'), u'Мои закладки'),
    )

    urls = []

    full_path = request.get_full_path()

    for idx, (url, title) in enumerate(auth_urls):
        # Ссылка, текст, является текущей ссылкой
        is_current = full_path == url
        show_marker = full_path.startswith(str(url)) if idx != 0 else is_current
        urls.append([url, title, is_current, show_marker])

    return {
        'urls': urls,
        'user': request.user,
    }
