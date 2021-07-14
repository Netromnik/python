# -*- coding: UTF-8 -*-
import logging

from django import template
from irk.phones.helpers import clean_firm_name

logger = logging.getLogger(__name__)

register = template.Library()

MAP_CITIES = (1, 2, 4, 9)


@register.inclusion_tag('map/tags/show_address.html', takes_context=True)
def show_address(context, address, note=True):
    
    context['flag'] = True
    if note == 'False' or note == 0:
        context['flag'] = False
    context['address'] = address
    return context


@register.inclusion_tag('map/tags/map_address.html')
def map_address(address):
    """Адрес организации со ссылкой на карту"""

    if address:
        return {
            'map_cities': MAP_CITIES,
            'address': address,
            'firm_name': clean_firm_name(address.firm_id.name),
        }
    else:
        logger.warning('Firm does not have a single address')
        return {}
