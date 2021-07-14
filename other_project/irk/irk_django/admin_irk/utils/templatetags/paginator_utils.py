# -*- coding: utf-8 -*-

from django import template
from django.core.paginator import Page
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.http import QueryDict

from irk.utils.templatetags import parse_arguments

PAGES_WITH_CURRENT = 5
DEFAULT_PAGINATOR_TEMPLATE = 'paginator/layout.html'

register = template.Library()


def _get_page_range(self):
    """Функция возаращает массив страниц относительно текущей в рамках заданного количества PAGES_WITH_CURRENT"""
    start = 1
    dp = self.number - self.pages_with_current
    if dp > 0:
        start = dp
        dp = 0

    end = self.number + self.pages_with_current - dp
    if end > self.paginator.num_pages:
        dm = end - self.paginator.num_pages - 1
        end = self.paginator.num_pages
    else:
        dm = 0
    start -= dm
    if start < 1:
        start = 1
    return range(start, end + 1)


Page.page_range = property(_get_page_range)


class PaginatorNode(template.Node):
    def __init__(self, page, *args, **kwargs):
        self._page = page
        self._url_params = args
        self._template_name = kwargs.get('template')
        self._plural_name = kwargs.get('name')
        self._params = kwargs.get('params')
        self._pages = kwargs.get('pages')
        self._url_hash = kwargs.get('hash')
        self._legacy = 'legacy' in kwargs

    def render(self, context):
        page = self._page.resolve(context)
        if page is None or page == '':
            return ''

        url_params = QueryDict('', mutable=True)
        for url_param in self._url_params:
            try:
                # Здесь token выведется вместе с фильтрами и прочим.
                # TODO: выбор имени как-то сделать?
                value = url_param.resolve(context)
                if value is None:
                    value = ''
                url_params[url_param.token] = value
            except UnicodeEncodeError:
                raise template.TemplateSyntaxError(
                    u'Устаревший формат тега `paginator`. Параметр «%s» должен быть записан как name=\'%s\'' % (
                    url_param.token, url_param.token))

        pass_params = self._params.resolve(context) if self._params else None
        if pass_params:
            url_params.update(pass_params)

        template_name = self._template_name.resolve(context) if self._template_name else 'paginator/layout.html'
        plural_name = self._plural_name.resolve(context) if self._plural_name else None
        pages = self._pages.resolve(context) if self._pages else PAGES_WITH_CURRENT
        url_hash = '#%s' % self._url_hash.resolve(context).strip('#') if self._url_hash else None

        page.pages_with_current = pages
        first = (pages + 1) < page.number
        last = (page.paginator.num_pages - pages - 1) >= page.number
        url_params = url_params.urlencode()

        template_context = {
            'paginator': page,
            'url_params': url_params,
            'first': first,
            'last': last,
            'plural_name': plural_name,
            'url_hash': url_hash,
            'legacy': {  # Поддержка legacy кода со старой логикой пагинатора во вьюшках
                'ppp': context.get('ppp'),
                'page': page.number,
                'order': context.get('order'),
                'direction': context.get('direction'),
                'state': context.get('state'),
                's': url_params,
                'set_option_url': reverse('profiles:set_option'),
                'next': context['request'].build_absolute_uri(),
            }
        }
        return render_to_string(template_name, template_context)


@register.tag
def paginator(parser, token):
    """Пагинатор в шаблонах

    Позиционные параметры::
        paginator: объект `django.core.paginator.Paginator'

    Все остальные позиционные объекты считаются дополнительными параметрами для генерируемого URL и берутся из контекста шаблона.

    Ключевые параметры::
        template: шаблон для рендеринга
        pages: количество ссылок на страницы
        name: описание объектов во мн. числе (например, объектов/организаций/новостей)
        hash: anchor для ссылок (например, #comments)

    Примеры::
        {% paginator objects %}
        {% paginator news pages=5 template='paginator.html' %}
        {% paginator firms limit order_by template='paginator/paginator.html' name='организаций' %}
    """

    args, kwargs = parse_arguments(parser, token.split_contents()[1:])

    return PaginatorNode(args[0], *args[1:], **kwargs)
