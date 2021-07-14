# -*- coding: utf-8 -*-

import datetime
import logging
from copy import copy

from django import template
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from irk.obed.models import Establishment
from irk.obed.forms import EstablishmentSearchForm
from irk.phones.models import Sections


EMPTY_CACHE_VALUE = object()

register = template.Library()

logger = logging.getLogger(__name__)


@register.inclusion_tag('obed/tags/full_rubricator.html', takes_context=True)
def fullrubricator(context):

    establishment_ct = ContentType.objects.get_for_model(Establishment)
    SECTION_URLS = {
        section_slug: reverse('obed:section_list', kwargs={'section_slug': section_slug})
        for section_slug in Sections.objects.filter(content_type=establishment_ct).values_list('slug', flat=True)
    }

    request = context.get('request')
    current_section = context.get('current_section')
    sections = Sections.objects.filter(content_type=establishment_ct).order_by("position")
    on_section_page = request.path == SECTION_URLS.get(current_section.slug) if current_section else False

    return {
        'sections': sections,
        'current_section': current_section,
        'on_section_page': on_section_page,
        'request': request
    }


@register.simple_tag(takes_context=True)
def establishment_url(context, establishment, section=None):
    """
    Шаблонный тег для определения url заведения с учетом текущей рубрики и условий отображения карточки заведения.
    Учитывается отображение карточки на странице корпоративов и бизнес-ланчей.

    :param dict context: контекст шаблона
    :param Establishment establishment: Объект заведения
    :return: url
    :rtype: str
    """

    business_lunch_page = context.get('business_lunch_page')

    if not section:
        try:
            section = establishment.main_section
        except Sections.DoesNotExist:
            # В БД есть заведения у которых нет главной рубрики. Это ошибка на уровне БД. Таким заведениям нужно вручную
            # проставить главную рубрику.
            logger.error(u'У заведения "{}" нет главной рубрики!'.format(establishment))
            return ''

    url = reverse('obed:establishment_read', kwargs={'section_slug': section.slug, 'firm_id': establishment.pk})

    if business_lunch_page:
        url = u'{}?tab=about#content'.format(url)
    else:
        pass

    return url


@register.simple_tag(takes_context=True)
def establishment_list_url(context, section_slug):
    request = context.get('request')
    if section_slug:
        url = reverse('obed:section_list', kwargs={'section_slug': section_slug})
    else:
        url = reverse('obed:list')
        request = context.get('request')

    # Убираем get параметры которые не должны сохранятся при смене рубрики
    get_params = copy(request.GET)
    if 'q' in get_params:
        del get_params['q']
    if 'tab' in get_params:
        del get_params['tab']

    if get_params:
        url = '{}?{}'.format(url, get_params.urlencode())
    return url


@register.inclusion_tag('obed/snippets/search_filter.html', takes_context=True)
def search_filter(context):
    request = context.get('request')
    current_section = context.get('current_section')
    form = EstablishmentSearchForm(request.GET)

    return {
        'form': form,
        'current_section': current_section
    }


def event_sort(event):
    return event.sessions.get_day().periods[0].sessions[0].time


def today_event_sort(event):
    now = datetime.datetime.now()
    for session in event.sessions.get_day().periods[0].sessions:
        if session.time >= now.time():
            return session.time
