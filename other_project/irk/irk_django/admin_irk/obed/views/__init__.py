# -*- coding: utf-8 -*-

import random

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from irk.contests.views.base.list import ListContestBaseView
from irk.contests.views.base.participant_create import CreateParticipantBaseView
from irk.contests.views.base.participant_read import ReadParticipantBaseView
from irk.contests.views.base.read import ReadContestBaseView
from irk.news.models import BaseMaterial, Metamaterial
from irk.obed.models import Establishment, Article, ArticleCategory, GuruCause, Review, Poll, Test, Okrug, TildaArticle
from irk.obed.permissions import can_edit_news
from irk.obed.templatetags.obedtags import establishment_url
from irk.phones.models import Address
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse

contests_read = ReadContestBaseView.as_view(template_name='obed/contests/read.html')
contests_list = ListContestBaseView.as_view(template_name='obed/contests/list.html')
participant_read = ReadParticipantBaseView.as_view(template_name='obed/contests/participant/read.html')
participant_create = CreateParticipantBaseView.as_view(template_dir='obed/contests/participant/add')


def index(request):
    """Индекс Обеда"""

    categories = list(ArticleCategory.objects.exclude(slug='list').order_by('position'))

    # Выводим статью для выбранной вкладки
    current_tab = request.GET.get('tab', 'all')
    show_hidden = can_edit_news(request.user)
    if current_tab == 'all':
        # Статьи, обзоры, голосования обеда
        # NOTE: если меняется выборка, то нужно также обновить ArticleListView._get_base_queryset
        material_types = [Article, Review, Poll, Metamaterial, Test, TildaArticle]
        materials = BaseMaterial.material_objects \
            .filter_models(*material_types) \
            .filter(sites=request.csite) \
            .order_by('-stamp', '-published_time')

        if not show_hidden:
            materials = materials.filter(is_hidden=False)

        materials = materials.only('id')[:10]
        materials = [m.cast() for m in materials]
    else:
        # Статьи и обзоры
        materials = Article.material_objects \
            .filter(sites=request.csite, section_category__slug=current_tab) \
            .order_by('-stamp', '-published_time')

        if not show_hidden:
            materials = materials.filter(is_hidden=False)
        materials = materials[:10]

    # Новогодние корпоративы
    corporatives = []
    if settings.OBED_CORPORATIVES:
        corporatives = list(Establishment.objects
            .filter(is_active=True, visible=True, corporative=True)
            .exclude(corporative_description__isnull=True)
            .exclude(corporative_description__exact='')
        )
        random.shuffle(corporatives)

    # Летние веранды
    summer_terraces = list(Establishment.objects
        .filter(is_active=True, visible=True, summer_terrace=True)
        .exclude(summer_terrace_description__isnull=True)
        .exclude(summer_terrace_description__exact='')
    )
    random.shuffle(summer_terraces)

    # гастрономический фестиваль
    barofest_participants = list(Establishment.barofest_participants
        .filter(is_active=True, visible=True)
    )
    random.shuffle(barofest_participants)

    # доставки
    deliveries = []
    if settings.OBED_DELIVERY:
        deliveries = list(Establishment.objects
            .filter(is_active=True, visible=True, delivery=True)
            .exclude(delivery_description__isnull=True)
            .exclude(delivery_description__exact='')
        )
        random.shuffle(deliveries)

    # Блок "Куда пойти"
    gurucases = GuruCause.objects.all().order_by('position')

    new_establishments = list(Establishment.objects
        .filter(is_active=True, visible=True, is_new=True)
        .select_related('last_review', 'main_section')
    )[:10]
    random.shuffle(new_establishments)

    context = {
        'article_list': materials,
        'article_categories': categories,
        'current_tab': current_tab,
        'corporatives': corporatives,
        'summer_terraces': summer_terraces,
        'barofest_participants': barofest_participants,
        'deliveries': deliveries,
        'gurucases': gurucases,
        'new_establishments': new_establishments,
    }

    return render(request, 'obed/index.html', context)


def search(request):
    """Поиск по обеду"""

    q = request.GET.get('q', '').strip()
    # Параметры пагинации
    start_index = int_or_none(request.GET.get('start')) or 0
    start_index = max(start_index, 0)
    page_limit = int_or_none(request.GET.get('limit')) or 24
    page_limit = min(page_limit, 24)

    search_result = Establishment.search.query({'q': q})
    object_count = search_result.count()

    if object_count:
        end_index = start_index + page_limit
        end_index = min(end_index, object_count)
        object_list = search_result[start_index:end_index]
        page_info = {
            'has_next': object_count > end_index,
            'next_start_index': end_index,
            'next_limit': min(page_limit, object_count - end_index),
        }
    else:
        object_list = []
        page_info = {}

    context = {
        'q': q,
        'object_list': object_list,
        'object_count': object_count,
    }

    if request.is_ajax():
        return JsonResponse(dict(
            html=render_to_string('obed/establishment/list.html', context),
            **page_info
        ))

    context.update(page_info)

    return render(request, 'obed/search_result.html', context)


def corporatives(request):
    """ Корпоративы """

    establishments = Establishment.objects.filter(is_active=True, visible=True, corporative=True).order_by('name')

    see_also_establishments = list(establishments.filter(Q(corporative_description__isnull=True) |
                                                    Q(corporative_description__exact='')))
    random.shuffle(see_also_establishments)

    main_establishments = list(establishments.exclude(corporative_description__isnull=True)\
        .exclude(corporative_description__exact=''))
    random.shuffle(main_establishments)

    context = {
        'see_also_establishments': see_also_establishments,
        'main_establishments': main_establishments,
    }

    return render(request, "obed/corporatives.html", context)


def barofest(request):
    """
    Байкальский гастрономический фестиваль 1.04.2018

    Шаблон и принцип построения такой же, как у корпоративов. Выводит список заведений,
    у которых в админке описана причастность к барофесту.
    """
    establishments = Establishment.barofest_participants.filter(is_active=True, visible=True).order_by('name')

    context = {
        'see_also_establishments': None,  # наследие от corporatives
        'main_establishments': establishments,
    }

    return render(request, 'obed/barofest.html', context)


def summer_terraces(request):
    """
    Летние веранды
    """
    establishments = list(Establishment.objects \
        .filter(is_active=True, visible=True, summer_terrace=True) \
        .exclude(summer_terrace_description__exact='')
    )

    random.shuffle(establishments)

    context = {
        'establishments': establishments,
    }

    return render(request, 'obed/summer_terraces.html', context)


def deliveries(request):
    """
    Доставки
    """
    establishments = list(Establishment.objects \
        .filter(is_active=True, visible=True, delivery=True) \
        .exclude(delivery_description__exact='')
    )

    random.shuffle(establishments)

    # округа для фильтра
    districts = list(Okrug.objects.values('id', 'name'))

    context = {
        'filter_districts': districts,
        'establishments': establishments,
    }

    return render(request, 'obed/deliveries.html', context)


def subscribe(request):
    """Страница рассылки"""

    return render(request, 'obed/subscribe_page.html')


def corporatives_block(request):
    """Блок корпоративов на главной"""

    corporatives = []
    context = {'corporatives': corporatives}

    query = Establishment.objects.select_related('main_section') \
        .filter(is_active=True, visible=True, corporative=True) \
        .exclude(corporative_description__isnull=True) \
        .exclude(corporative_description__exact='')

    for estab in query:
        corporatives.append({
            'id': estab.id,
            'name': estab.name,
            'url': b'{}?tab=corporative#content'.format(establishment_url({}, estab)),
            'main_address': None,  # заполним ниже
            'card_image': estab.card_image,
        })

    # дальше идет оптимизированная логика, которая добавляет в каждое
    # заведение main_address, точно так же, как это бы сделал property
    # в объекте Firms, но мой код оптимизирован для работы в цикле

    # построим индекс адресов по id заведения
    query = Address.objects.select_related('city_id') \
        .filter(firm_id__in=[x['id'] for x in corporatives])
    addresses = {x.firm_id_id: x for x in query}
    addresses_main = {x.firm_id_id: x for x in query.filter(is_main=True)}

    # и к каждому заведению добавим объект адреса
    for item in corporatives:
        item['main_address'] = addresses_main.get(item['id']) or addresses.get(item['id'])

    random.shuffle(corporatives)

    return render(request, 'obed/snippets/corporatives_block.html', context)


def delivery_block(request):
    """Блок доствок на главной"""

    deliveries = []
    context = {'deliveries': deliveries}

    query = Establishment.objects.select_related('main_section') \
        .filter(is_active=True, visible=True, delivery=True) \
        .exclude(delivery_description__isnull=True) \
        .exclude(delivery_description__exact='')

    for estab in query:
        deliveries.append({
            'id': estab.id,
            'name': estab.name,
            'url': b'{}?tab=delivery#content'.format(establishment_url({}, estab)),
            'main_address': None,  # заполним ниже
            'card_image': estab.card_image,
        })

    # дальше идет оптимизированная логика, которая добавляет в каждое
    # заведение main_address, точно так же, как это бы сделал property
    # в объекте Firms, но мой код оптимизирован для работы в цикле

    # построим индекс адресов по id заведения
    query = Address.objects.select_related('city_id') \
        .filter(firm_id__in=[x['id'] for x in deliveries])
    addresses = {x.firm_id_id: x for x in query}
    addresses_main = {x.firm_id_id: x for x in query.filter(is_main=True)}

    # и к каждому заведению добавим объект адреса
    for item in deliveries:
        item['main_address'] = addresses_main.get(item['id']) or addresses.get(item['id'])

    random.shuffle(deliveries)

    return render(request, 'obed/snippets/delivery_block.html', context)
