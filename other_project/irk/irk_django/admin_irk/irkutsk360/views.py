# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db.models import Q
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import Http404

from irk.irkutsk360.models import Fact, Congratulation
from irk.irkutsk360.settings import IRKUTSK360_PRISM_ID, IRKUTSK360_SITE_SLUG, IRKUTSK360_STORY_SLUG
from irk.afisha.models import CurrentSession
from irk.afisha.views.events import EventsListView
from irk.special.models import Project
from irk.news.models import BaseMaterial, Article, Photo
from irk.options.models import Site
from irk.utils.http import JsonResponse
from irk.utils.helpers import int_or_none


class IndexView(View):

    template = 'irkutsk360/index.html'
    ajax_template = 'irkutsk360/list.html'
    material_page_limit = 8
    event_page_limit = 2

    def get(self, request, *args, **kwargs):
        self.page = int_or_none(self.request.GET.get('page')) or 1

        if request.is_ajax():
            return self._render_ajax_response(request)

        context = self.get_context_data()

        return render(request, self.template, context)


    def _render_ajax_response(self, request):
        """Подгрузка материалов через Ajax"""

        context = self.get_context_data()

        return render(request, self.ajax_template, context)


    def get_context_data(self):
        advertising_material = self.get_advertising_material() if self.page == 1 else None

        events = self.paginate_queryset(self.get_events_queryset(),
            self.event_page_limit)

        # Если событий нет то получаем больше материалов
        if not events:
            self.material_page_limit += self.event_page_limit

        if advertising_material:
            self.material_page_limit -= 1

        materials = self.paginate_queryset(self.get_materials_queryset(),
            self.material_page_limit)

        object_list = [m.cast() for m in materials]

        if events and len(events) == self.event_page_limit:
            object_list.insert(1, events[0])
            object_list.insert(5, events[1])

        if advertising_material:
            object_list.insert(4, advertising_material)

        context = {
            'object_list': object_list,
        }

        return context

    def paginate_queryset(self, queryset, limit):
        paginator = Paginator(queryset, limit)
        try:
            page_obj = paginator.page(self.page)
        except (EmptyPage, InvalidPage):
            raise Http404()

        return page_obj.object_list

    def get_events_queryset(self):
        filters = {
            'end_date__gte': datetime.datetime.now(),
            'is_hidden': False,
            'event__prisms': IRKUTSK360_PRISM_ID,
        }
        sessions = CurrentSession.objects.filter(**filters).with_tickets()\
            .prefetch_related('guide').select_related('period').order_by('real_date')

        events = []
        for session in sessions:
            event = session.event
            event.schedule.append(session)
            events.append(event)

        return events

    def get_irkutsk360_site(self):
        return Site.objects.get(slugs=IRKUTSK360_SITE_SLUG)

    def get_materials_queryset(self):
        return BaseMaterial.longread_objects.for_site(self.get_irkutsk360_site()) \
        .filter(is_hidden=False).order_by('-stamp', '-published_time')

    def get_advertising_material(self):
        return BaseMaterial.longread_objects.for_site(self.get_irkutsk360_site()) \
             .filter(is_hidden=False).filter(is_advertising=True).order_by('-stamp', '-published_time').first()


class Afisha360View(EventsListView):

    paginate_by = 10
    template_name = 'irkutsk360/afisha.html'
    ajax_template_name = 'irkutsk360/afisha_list.html'
    paginator_class = Paginator

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.ajax_template_name,]
        else:
            return [self.template_name]

    def get_filter_data(self):
        data = self.request.GET.copy()
        data['prism'] = IRKUTSK360_PRISM_ID
        return data

    def paginate(self, objects):
        page_kwarg = self.page_kwarg
        page = self.request.GET.get(page_kwarg) or 1

        paginate = self.paginator_class(objects, self.paginate_by)

        try:
            objects = paginate.page(page)
        except (EmptyPage, InvalidPage):
            raise Http404()

        return objects

afisha360_index = Afisha360View.as_view()


class StoryView(ListView):
    model = Article
    template_name = 'irkutsk360/stories.html'
    ajax_template_name = 'irkutsk360/stories_list.html'
    paginate_by = 10

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.ajax_template_name,]
        else:
            return [self.template_name]

    def get_queryset(self):
        project = get_object_or_404(Project, slug=IRKUTSK360_STORY_SLUG)
        return project.news_materials.filter(~Q(is_hidden=True)).select_subclasses().order_by('-stamp')


class GalleryView(ListView):
    model = Photo
    template_name = 'irkutsk360/gallery.html'
    ajax_template_name = 'irkutsk360/gallery_list.html'
    paginate_by = 7

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.ajax_template_name,]
        else:
            return [self.template_name]

    def get_queryset(self):
        irkutsk360_site = Site.objects.get(slugs=IRKUTSK360_SITE_SLUG)
        return self.model.longread_objects.for_site(irkutsk360_site).order_by('-stamp', '-published_time')


class CongratulationsFormVie    w(CreateView):
    model = Congratulation
    template_name = 'irkutsk360/congratulations/add.html'
    fields =  ['name', 'contact', 'position', 'content']

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'result': 'ok'})


class CongratulationsView(ListView):
    model = Congratulation
    template_name = 'irkutsk360/congratulations/index.html'

    def get_queryset(self):
        queryset = super(CongratulationsView, self).get_queryset()
        return queryset.filter(is_visible=True)


class FactView(DetailView):
    model = Fact
    pk_url_kwarg = 'number'
    template_name = 'irkutsk360/tags/facts.html'

    def get_object(self):
        number = self.kwargs.get(self.pk_url_kwarg)

        next_number = int(number) + 1

        return get_object_or_404(Fact, number=next_number)
