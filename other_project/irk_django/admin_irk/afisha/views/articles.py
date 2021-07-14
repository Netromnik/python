# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from irk.afisha.controllers import ExtraMaterialController
from irk.afisha.models import Article
from irk.afisha.settings import DEFAULT_EXTRA_AJAX_COUNT, INDEX_EXTRA_MATERIAL
from irk.news.views.base.read import SectionNewsReadBaseView
from irk.utils.helpers import int_or_none
from irk.utils.http import json_response


class ArticleReadView(SectionNewsReadBaseView):
    model = Article

read = ArticleReadView.as_view()


@json_response
def extra_materials(request):
    """
    Подгрузка дополнительных материалов
    """

    start_index = int_or_none(request.GET.get('start')) or 0
    limit = int_or_none(request.GET.get('limit')) or DEFAULT_EXTRA_AJAX_COUNT

    controller = ExtraMaterialController()
    object_list, page_info = controller.get_materials(start_index, limit)

    context = {
        'material_list': object_list,
        'request': request,
        'has_extra_materials': INDEX_EXTRA_MATERIAL,
    }

    return dict(
        html=render_to_string('afisha/tags/afisha_extra_materials_list.html', context, request=request),
        **page_info
    )
