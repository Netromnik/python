# -*- coding: utf-8 -*-

from django import template

from irk.newyear2014.models import Horoscope


register = template.Library()


@register.inclusion_tag('newyear2014/tags/horoscope_menu.html')
def horoscope_menu(current_horoscope=None, show_link=False):

    show_link = True if show_link == 'True' else False

    horoscopes = Horoscope.objects.all().order_by('-position')

    return {
        'objects': horoscopes,
        'current': current_horoscope,
        'show_link': show_link
    }
