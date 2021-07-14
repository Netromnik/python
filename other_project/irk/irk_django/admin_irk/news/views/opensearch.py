# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.core.urlresolvers import reverse

from irk.utils.opensearch import BaseOpenSearchView


class NewsOpenSearch(BaseOpenSearchView):
    short_name = 'Новости IRK.ru'
    description = 'Новости Иркутска: экономика, спорт, медицина, культура, происшествия'

    def get_url(self):
        return '{}?q={{searchTerms}}'.format(reverse('news:search'))
