# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import View

from irk.news.models import BaseMaterial, Metamaterial
from irk.special.models import Project, Sponsor
from irk.special.permissions import is_moderator
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse
from irk.utils.views.mixins import PaginateMixin


def sponsor_click(request, sponsor_id):
    """Редирект на сайт спонсора"""

    sponsor = get_object_or_404(Sponsor, pk=sponsor_id)
    return redirect(sponsor.link)


class Index(PaginateMixin, View):
    """Индекс спецпроекта"""

    template = 'special/index/index_branding.html'
    paginate_template = 'special/index/material_list.html'

    page_limit_default = 10

    def get(self, *args, **kwargs):

        self._parse_params()

        # хак, чтобы не делать для спецпроектов Бетонова пейджинацию
        NO_PAGINATION_PROJECTS = ('buildingtime', 'fabrika-betonov')
        if self.kwargs.get('slug', '') in NO_PAGINATION_PROJECTS:
            self.page_limit = 50

        materials = self.get_materials()
        object_list, page_info = self._paginate(materials)

        context = {
            'project': self.project,
            'materials': [m.cast() for m in object_list],
            'layout': 'special/layout.html',
            'page_info': page_info,
        }

        if self.request.is_ajax():
            return self._render_ajax_response(context, page_info)

        return render(self.request, self.get_templates(), context)

    def get_materials(self):
        materials = BaseMaterial.material_objects.filter(project=self.project).order_by('-stamp', '-id')
        if not is_moderator(self.request.user):
            materials = materials.filter(is_hidden=False)

        return materials

    def get_templates(self):
        """Путь к шаблону индекса, можно задать кастомный"""

        custom_folder = '{}_{}'.format(self.project.site.slugs, self.project.slug)

        return (
            'special/{}/index/index_branding.html'.format(custom_folder),
            self.template,
        )

    def _parse_params(self):
        """Разобрать параметры переданные в url и в строке запроса"""

        project_slug = self.kwargs.get('slug')
        self.project = get_object_or_404(Project, slug=project_slug)

        # Параметры пагинации
        start_index = int_or_none(self.request.GET.get('start')) or 0
        self.start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self.page_limit = min(page_limit, self.page_limit_max)

    def _render_ajax_response(self, context, page_info):
        """
        Отправить ответ на Ajax запрос

        :param dict context: контекст шаблона
        :param dict page_info: информация о странице
        """

        return JsonResponse(dict(
            html=render_to_string(self.paginate_template, context),
            **page_info
        ))


def project_list(request):
    """Список всех спецпроектов"""

    projects = Project.objects.all()
    metamaterials = Metamaterial.objects.filter(is_special=True)

    exclude_projects = []

    for project in projects:
        materials = project.news_materials.all()
        if not is_moderator(request.user):
            materials = materials.filter(is_hidden=False)
        material = materials.order_by('-stamp', '-pk').first()

        if material:
            project.material = material.cast()
            project.stamp = material.stamp
        else:
            exclude_projects.append(project)

    projects = list(projects)
    for exclude_project in exclude_projects:
        projects.remove(exclude_project)

    projects = sorted(projects, key=lambda x: x.stamp, reverse=True)

    context = {
        'projects': projects,
        'metamaterials': metamaterials,
    }

    return render(request, 'special/index.html', context)


index = Index.as_view()
