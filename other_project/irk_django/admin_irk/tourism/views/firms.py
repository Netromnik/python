# -*- coding: utf-8 -*-

import random

from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.db.models.fields import NOT_PROVIDED
from django.core.urlresolvers import reverse_lazy

from irk.phones.views.base.create import CreateFirmBaseView
from irk.phones.views.base.list import ListFirmBaseView
from irk.phones.views.base.read import ReadFirmBaseView
from irk.phones.views.base.update import UpdateFirmBaseView
from irk.tourism.models import Tour, Hotel, TourBase, TourFirm
from irk.phones.models import Sections as Section, Firms
from irk.tourism import permissions
from irk.tourism.permissions import is_moderator, get_moderators
from irk.tourism.permissions import can_edit_firm
from irk.tourism.forms.firm import HotelForm, TourBaseForm, TourFirmForm
from irk.utils.notifications import tpl_notify


class ListFirmView(ListFirmBaseView):
    template = 'tourism/firm/list.html'

    def get_queryset(self, request, extra_params):
        try:
            section = Section.objects.filter(slug=extra_params['section_slug'])[0]
        except IndexError:
            raise Http404(u'Нет рубрики с таким алиасом')

        if extra_params.get('content_model'):
            return section.content_type.model_class().objects.filter(visible=True,).\
                select_related('firms_ptr').order_by('firms_ptr__name')
        else:
            return section.firms_set.filter(visible=True,).order_by('name').select_related('firms_ptr')

    def extra_context(self, request, queryset, extra_params):
        section = Section.objects.filter(slug=extra_params['section_slug'])[0]
        return {
            'can_create': 'content_model' in extra_params,
            'section': section,
            'using_content_model': extra_params.get('content_model'),
            'search_type': 'firm',
        }

section_firm_list = ListFirmView.as_view()


class CreateFirmView(CreateFirmBaseView):
    forms = {
        TourBase: TourBaseForm,
        TourFirm: TourFirmForm,
        Hotel: HotelForm,
    }

    def dispatch(self, request, *args, **kwargs):
        try:
            self.section = Section.objects.filter(slug=kwargs['section_slug'])[0]
        except IndexError:
            raise Http404()

        return super(CreateFirmView, self).dispatch(request, *args, **kwargs)

    def get_template(self, request, obj, template_context, create):
        return (
            'tourism/%s/create.html' % self.section.content_type.model if self.section.content_type else 'firm',
            'tourism/firm/create.html',
        )

    def extra_context(self, request, obj=None):
        return {
            'section': self.section,
            'search_type': 'firm',
        }

    def get_form(self, request, obj=None):
        return self.forms[self.section.content_type.model_class()]

    def get_model(self, request):
        return self.section.content_type.model_class()

    def response_completed(self, request, obj):
        return render(request, 'tourism/firm/created.html', {'section': self.section})

    def notifications(self, request, obj, extra_context=None):
        if not is_moderator(request.user):
            tpl_notify(u'Новая туристическая организация', 'tourism/notif/firms/added.html', {'firm': obj}, request,
                       emails=get_moderators().values_list('email', flat=True))

    @transaction.atomic
    def save_model(self, request, obj, form):
        obj.save()

        # Создаем дополнительные, выбранные пользователем, контентные модели
        for model_slug in form.cleaned_data.get('models', ()):
            model = form.CHOICES_MODELS[model_slug]
            # Пропускаем уже созданную только что контентную модель
            if model == type(obj):
                continue

            # Создаем данные для контентной модели
            kwargs = {}
            for field in model._meta.fields:
                # Учитываем default значения полей, если они указаны
                kwargs[field.name] = getattr(obj, field.name, field.default if field.default != NOT_PROVIDED else None)
            additional_obj = model(**kwargs)
            additional_obj.save()

create = CreateFirmView.as_view()


class ReadFirmView(ReadFirmBaseView):

    redirect_url = reverse_lazy('tourism:index')

    def get_object(self, request, extra_params):
        try:
            self.section = Section.objects.filter(slug=extra_params['section_slug'])[0]
        except IndexError:
            raise Http404()

        if extra_params.get('content_model'):
            queryset = self.section.content_type.model_class().objects.all()
        else:
            queryset = self.section.firms_set.all()

        obj = queryset.filter(pk=extra_params['firm_id'], visible=True).first()

        # Переадресация на индекс раздела если объект не найден
        if not obj:
            if self.redirect_url:
                return redirect(self.redirect_url, permanent=True)
            raise Http404()
        return obj

    def extra_context(self, request, obj, extra_params):

        can_edit = can_edit_firm(request.user, obj)

        tours = {}
        tours_list = ()
        if isinstance(obj, TourFirm):
            tours_obj = Tour.objects.filter(firm=obj)
            if not can_edit:
                tours_obj = tours_obj.filter(is_hidden=False)
            tours_list = list(tours_obj)
            tours = {
                'hot': [x for x in tours_list if x.is_hot],
                'extinct': [x for x in tours_list if not x.is_hot],
            }

        # Объект к которому привязываются коменты
        # должен быть phones.models.Firms,
        # а в выборке может быть и контентная модель
        comments_object = obj if type(obj) is Firms else obj.firms_ptr

        return {
            'section': self.section,
            'comments_object': comments_object,
            'firm_page': True,
            'can_edit': can_edit,
            'tours': tours,
            'tours_list': tours_list,
            'hide_tours': extra_params.get('hide_tours', False),
            'search_type': 'firm',
        }

    def get_template(self, request, obj, template_context):
        return (
            'tourism/%s/read.html' % self.section.content_type.model if self.section.content_type else 'firm',
            'tourism/firm/read.html',
        )

section_firm = ReadFirmView.as_view()


class UpdateFirmView(UpdateFirmBaseView):
    forms = {
        TourBase: TourBaseForm,
        TourFirm: TourFirmForm,
        Hotel: HotelForm,
    }

    def get_object(self, request, extra_params):
        try:
            self.section = Section.objects.filter(slug=extra_params['section_slug'])[0]
        except IndexError:
            raise Http404()

        if extra_params.get('content_model'):
            queryset = self.section.content_type.model_class()
        else:
            queryset = self.section.firms_set.all()

        obj = get_object_or_404(queryset, visible=True, pk=extra_params['firm_id'])

        if not permissions.can_edit_firm(request.user, obj):
            return HttpResponseForbidden()

        return obj

    def get_form(self, request, obj=None):
        return self.forms[self.section.content_type.model_class()]

    def extra_context(self, request, obj=None):
        return {
            'section': self.section,
            'search_type': 'firm',
        }

    def get_template(self, request, obj, template_context, create):
        return (
            'tourism/%s/edit.html' % self.section.content_type.model if self.section.content_type else 'firm',
            'tourism/firm/edit.html',
        )

    def notifications(self, request, obj, extra_context):
        context = {
            'instance': obj,
        }
        tpl_notify(u'Отредактирована организация в разделе «Туризм»', 'tourism/firm/notif/create.html', context, request,
                   emails=permissions.get_moderators().values_list('email', flat=True))

    def response_completed(self, request, obj):
        return HttpResponseRedirect(".")

    @transaction.atomic
    def save_model(self, request, obj, form):
        obj.save()

        # Создаем дополнительные, выбранные пользователем, контентные модели
        for model_slug in form.cleaned_data.get('models', ()):
            model = form.CHOICES_MODELS[model_slug]
            # Пропускаем уже созданную только что контентную модель
            if model == type(obj):
                continue

            # Создаем данные для контентной модели
            kwargs = {}
            for field in model._meta.fields:
                # Учитываем default значения полей, если они указаны
                kwargs[field.name] = getattr(obj, field.name, field.default if field.default != NOT_PROVIDED else None)
            additional_obj = model(**kwargs)
            additional_obj.save()

edit_firm = UpdateFirmView.as_view()
