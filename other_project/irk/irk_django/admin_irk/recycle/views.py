# coding=utf-8
from __future__ import absolute_import, unicode_literals

import json

from django.shortcuts import render

from irk.options.models import Site
from irk.recycle.models import Category, Dot, RelatedArticle
from irk.utils.templatetags.str_utils import do_typograph

YANDEX_API_KEY = '89182932-e0e9-4f0c-817f-32c2c6f15023'

def index(request):
    """
    Карта пунктов сдачи вторсырья
    """

    dots = []
    for dot in Dot.objects.all():
        dot_item = {
            'id': dot.id,
            'name': do_typograph(dot.name, 'title'),
            'description': do_typograph(dot.description, 'user'),
            'x': dot.x,
            'y': dot.y,
            'working_hours': do_typograph(dot.working_hours),
            'addres': dot.addres,
            'phone': dot.phone,
            'image': '',
            'categories': [id[0] for id in dot.categories.values_list('id')],
        }
        if dot.image:
            dot_item['image'] = dot.image.url

        dots.append(dot_item)

    categories = []
    for cat in Category.objects.all():
        cat_item = {
            'id': cat.id,
            'name': cat.name,
        }

        categories.append(cat_item)
    sites = Site.objects.filter(is_hidden=False, in_menu=True).order_by('position')

    context = {
        'articles': RelatedArticle.objects.filter(article__is_hidden=False).order_by('id'),
        'dots_json': json.dumps(dots),
        'categories_json': json.dumps(categories),
        'categories': Category.objects.order_by('order'),
        'sites': sites,
        'yandex_api_key': YANDEX_API_KEY,
    }

    return render(request, 'recycle/index.html', context)
