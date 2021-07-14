# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('newyear2014/tags/main_menu.html')
def main_menu(path):
    newyear2014_indexes = [
        reverse('newyear2014.views.horoscope.index'),
        # reverse('newyear2014.views.afisha.index'),
        # reverse('newyear2014.views.articles.index'),
        # reverse('newyear2014.views.contests.index'),
        reverse('newyear_gifts'),
        reverse('newyear_hostels'),
        reverse('newyear_corporates'),
    ]

    active_index = None
    for newyear2014_index in newyear2014_indexes:
        if path.startswith(newyear2014_index):
            active_index = newyear2014_index
            break

    return {
        'current_path': path,
        'active_index': active_index
    }
