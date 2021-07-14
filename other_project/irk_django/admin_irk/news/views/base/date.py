# -*- coding: utf-8 -*-

"""Список новостей за дату"""

import datetime

from django.http import Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist

from pytils.dt import ru_strftime
from irk.news.views.base.list import NewsListBaseView


class NewsDateBaseView(NewsListBaseView):

    use_pagination = False

    def get_queryset(self, request, extra_params=None):
        try:
            self.date = datetime.date(int(extra_params['year']), int(extra_params['month']), int(extra_params['day']))
        except ValueError:
            raise Http404(u'Неверная дата')

        queryset = super(NewsDateBaseView, self).get_queryset(request, extra_params).filter(stamp=self.date).prefetch_related('source_site')
        if not queryset.exists():  # Новостей за этот день нет
            raise Http404()

        return queryset

    def get_template(self, request, template_context):
        app_label = self.__module__.split('.', 1)[0]
        return self.template or '%s/%s/date.html' % (app_label, self.model._meta.object_name.lower())

    def extra_context(self, request, queryset, extra_params=None):
        context = super(NewsDateBaseView, self).extra_context(request, queryset, extra_params)

        try:
            previous_date = self.model.objects.filter(stamp__lt=self.date).order_by('-stamp').values_list('stamp', flat=True)[0]
            previous_date_url = reverse('news:news:date', args=('%04d' % previous_date.year,
                '%02d' % previous_date.month, '%02d' % previous_date.day))
        except IndexError:
            previous_date = None
            previous_date_url = None

        try:
            next_date = self.model.objects.filter(stamp__gt=self.date).order_by('stamp').values_list('stamp', flat=True)[0]
            next_date_url = reverse('news:news:date', args=('%04d' % next_date.year,
                '%02d' % next_date.month, '%02d' % next_date.day))
        except IndexError:
            next_date = None
            next_date_url = None

        context.update({
            'date': self.date,
            'previous_date': previous_date,
            'previous_date_url': previous_date_url,
            'next_date': next_date,
            'next_date_url': next_date_url,
        })

        return context

    def render_template(self, request, context):
        return render(request, self.get_template(request, context), context)
