# -*- coding: utf-8 -*-

"""Class-based view для просмотра одного конкурса"""


from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse

from irk.contests.models import Contest


class ReadContestBaseView(DetailView):
    model = Contest
    slug_url_kwarg = 'slug'
    slug_field = 'slug'
    by_csite = True  # Конкурс открыт не из раздела конкурсов

    def get_queryset(self, *args, **kwargs):
        queryset = super(ReadContestBaseView, self).get_queryset()
        if self.by_csite:
            queryset = queryset.filter(sites=self.request.csite)
        else:
            # HACK: пока шаблоны только для обеда
            queryset = queryset.filter(vote_type=Contest.SITE_VOTE)

        return queryset

    def get_context_data(self, **kwargs):
        context = kwargs
        context_object_name = self.get_context_object_name(self.object)
        if context_object_name:
            context[context_object_name] = self.object
            context['participants'] = self.object.participants.filter(is_active=True).prefetch_related('contest')

        context['social_statistic'] = getattr(self.object, 'statistic_metrics', None)

        return context

    def get_template_names(self):
        tpl_name = 'contests/read_{}.html'.format(self.object.type)
        if self.by_csite:
            site_slug = self.request.csite.slugs
            tpl_name = '{}/{}'.format(site_slug, tpl_name)
        return [tpl_name, ]


contests_detail = ReadContestBaseView.as_view()
