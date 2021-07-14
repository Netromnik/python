# -*- coding: utf-8 -*-

"""Class-based view для просмотра информации об одном участнике"""

from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic.detail import DetailView

from irk.contests.models import Participant, Contest
from irk.contests.permissions import is_moderator


class ReadParticipantBaseView(DetailView):
    model = Participant
    pk_url_kwarg = 'participant_id'
    by_csite = True  # Конкурс открыт не из раздела конкурсов

    def get_queryset(self):
        queryset = super(ReadParticipantBaseView, self).get_queryset()
        return queryset.filter(is_active=True)

    def get_context_data(self, object, **kwargs):
        # Запрет показа участников викторин
        if object.contest.type == Contest.TYPE_QUIZ:
            raise Http404()

        context = super(ReadParticipantBaseView, self).get_context_data(**kwargs)
        try:
            context['previous'] = self.model.objects.filter(pk__lt=object.pk, contest=object.contest,
                                                            is_active=True).order_by('-pk')[0]
        except IndexError:
            pass
        try:
            context['next'] = self.model.objects.filter(pk__gt=object.pk, contest=object.contest,
                                                        is_active=True).order_by('pk')[0]
        except IndexError:
            pass
        context['other'] = self.model.objects.filter(contest=object.contest, is_active=True).exclude(
            pk=object.pk).order_by('?').prefetch_related('contest')[:4]

        context['is_moderator'] = is_moderator(self.request.user)
        return context

    def get_template_names(self):
        tpl_name = 'contests/participant/read_{}.html'.format(self.object.contest.type)
        if self.by_csite:
            site_slug = self.request.csite.slugs
            tpl_name = '{}/{}'.format(site_slug, tpl_name)
        return tpl_name


participant_detail = ReadParticipantBaseView.as_view()
