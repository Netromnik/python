# -*- coding: utf-8 -*-

"""Сюжеты новостей"""

from django.core.paginator import EmptyPage, InvalidPage
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.generic import View

from irk.utils.helpers import int_or_none
from irk.utils.http import json_response
from irk.utils.paginator import ReversePaginator
from irk.utils.views.mixins import PaginateMixin

from irk.news.helpers import MaterialController
from irk.news.models import Subject, News, BaseMaterial
from irk.news.permissions import is_moderator


def index(request):
    """Список сюжетов"""

    try:
        page = int(request.GET.get('page', 0))
    except ValueError:
        page = 0

    paginator = ReversePaginator(Subject.objects.filter(is_visible=True).order_by('pk'), 10)
    if page < 1:
        page = paginator.num_pages

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)

    context = {
        'paginator': paginator,
        'objects': objects,
        'page': page,
    }

    return render(request, 'news-less/subjects/index.html', context)


class ReadView(PaginateMixin, View):
    """Страница сюжета (темы)"""

    template = 'news-less/subjects/read.html'
    ajax_template = 'news-less/subjects/snippets/ribbon_materials_list.html'
    main_materials_limit = 4
    page_limit_default = 5

    def get(self, request, *args, **kwargs):
        """Вернуть ответ"""

        self._parse_params()

        context = self.get_context()

        if request.is_ajax():
            return self._render_ajax_response(context)

        return render(request, self.template, context)

    def _parse_params(self):
        """Разобрать параметры"""

        self._show_hidden = is_moderator(self.request.user)
        self._subject_slug = self.kwargs.get('slug', '')

        # Параметры пагинации
        start_index = int_or_none(self.request.GET.get('start')) or self.start_index
        self.start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self.page_limit = min(page_limit, self.page_limit_max)

    def get_context(self):
        """Получить контекст"""

        subject = get_object_or_404(Subject, slug=self._subject_slug)
        main_materials = self._get_main_materials(subject)
        # other_materials = self._get_other_materials(subject, main_materials)

        materials = self._get_ribbon_materials(subject, main_materials)
        ribbon_materials, page_info = self._paginate(materials)

        important_materials = self._get_important_materials()

        return {
            'subject': subject,
            'main_materials': main_materials,
            'ribbon_materials': ribbon_materials,
            # 'other_materials': other_materials,
            'important_materials': important_materials,
            'page_info': page_info,
            'show_hidden': self._show_hidden,
        }

    @json_response
    def _render_ajax_response(self, context):
        """Подгрузка материалов через Ajax"""

        result = dict(
            html=render_to_string(self.ajax_template, context),
            **context['page_info']
        )

        return result

    def _get_main_materials(self, subject):
        """Получить главные материалы сюжета"""

        materials = subject.news_basematerial \
            .filter(subject_main=True) \
            .order_by('-stamp', '-published_time') \
            .select_subclasses()

        if not self._show_hidden:
            materials = materials.filter(is_hidden=False)

        return materials[:self.main_materials_limit]

    def _get_ribbon_materials(self, subject, main_materials):
        """Получить материалы для ленты"""

        main_materials_ids = list(main_materials.values_list('id', flat=True))

        materials = subject.news_basematerial \
            .exclude(pk__in=main_materials_ids) \
            .order_by('-stamp', '-published_time') \
            .select_subclasses()

        if not self._show_hidden:
            materials = materials.filter(is_hidden=False)

        return materials

    def _get_other_materials(self, subject, main_materials):
        """
        Получить дополнительные материалы.

        Отображаются в правой колонке.
        Для каждого главного материала выбирается один дополнительный на основе тегов.
        """

        other_materials = []

        for material in main_materials:
            for similar_material in material.tags.similar_objects():
                # Новости не выводим
                if isinstance(similar_material, News):
                    continue

                # Пропускаем скрытые, если их нельзя отображать
                if not self._show_hidden and similar_material.is_hidden:
                    continue

                if (similar_material not in other_materials) and (similar_material.subject != subject):
                    other_materials.append(similar_material)
                    # Переходим к следующему главному материалу
                    break

        return other_materials

    def _get_important_materials(self):
        """Получить главные новости"""

        mc = MaterialController(show_hidden=self._show_hidden)
        return mc.get_important_materials()


class Newyear2019ReadView(ReadView):

    template = 'news-less/subjects/newyear2019_read.html'
    ajax_template = 'news-less/subjects/snippets/ribbon_newyear_materials_list.html'
    newyear_news_limit = 3

    def _get_ribbon_materials(self, subject, main_materials):
        """Получить материалы для ленты"""

        main_materials_ids = list(main_materials.values_list('id', flat=True))

        materials = BaseMaterial.longread_objects.filter(subject=subject) \
            .exclude(pk__in=main_materials_ids) \
            .order_by('-stamp', '-published_time') \
            .select_subclasses()

        if not self._show_hidden:
            materials = materials.filter(is_hidden=False)

        return materials

    def _get_newyear_news(self, subject):
        """Получить новогодние новости"""

        materials = News.objects.filter(subject=subject) \
            .order_by('-stamp', '-published_time') \

        if not self._show_hidden:
            materials = materials.filter(is_hidden=False)

        return materials[:self.newyear_news_limit]

    def get_context(self):
        """Получить контекст"""

        context = super(Newyear2019ReadView, self).get_context()

        context['newyear2019_news'] = self._get_newyear_news(context['subject'])

        return context


def read_legacy(request, slug):
    """Для старых ссылок на сюжеты делаем редирект на новый URL"""

    return HttpResponsePermanentRedirect(reverse('news:subjects:read', kwargs={'slug': slug}))


read = ReadView.as_view()
newyear2019_read = Newyear2019ReadView.as_view()
