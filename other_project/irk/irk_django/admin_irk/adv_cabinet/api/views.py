# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.db.models import Max, Min, Q
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from irk.adv.models import Banner, Log, Period
from irk.adv_cabinet.permissions import IsBusinessAccount
from irk.adv_cabinet.serializers import LogListSerializer, BannerListSerializer
from irk.utils.helpers import int_or_none


def parse_date(date):
    FORMAT = '%Y-%m-%d' if date and '-' in date else '%Y%m%d'
    try:
        return datetime.strptime(date, FORMAT).date()
    except (ValueError, TypeError):
        return None


class BannerListAPIView(ListAPIView):
    """Список размещений"""

    serializer_class = BannerListSerializer
    permission_classes = (IsAuthenticated, IsBusinessAccount,)

    def get_queryset(self):

        site_id = int_or_none(self.request.query_params.get('site'))
        client_id = int_or_none(self.request.query_params.get('client'))

        date_start = parse_date(self.request.query_params.get('date_start', ''))
        date_end = parse_date(self.request.query_params.get('date_end', ''))

        if not date_start:
            date_start = datetime.today()

        if not date_end:
            date_end = datetime.today()

        client_filters = {}
        if client_id:
            client_filters['id'] = client_id

        banner_place_filters = {}
        place_filters = {}
        if site_id:
            banner_place_filters['places__site_id'] = site_id
            place_filters['site_id'] = site_id

        clients = self.request.user.profile.business_account.clients.filter(is_deleted=False, is_active=True) \
            .filter(**client_filters)

        if not clients:
            return []

        banners = Banner.objects.filter(client_id__in=clients.values_list('id', flat=True)) \
            .filter(**banner_place_filters)

        periods = Period.objects.filter(banner_id__in=banners.values_list('id', flat=True)) \
            .filter(Q(date_from__range=(date_start, date_end)) |
                    Q(date_to__range=(date_start, date_end)) |
                    Q(date_from__lt=date_start, date_to__gt=date_end)) \
            .order_by('-date_from')

        data = []
        for period in periods:

            places = []

            for place in period.banner.places.filter(**place_filters):
                site = place.site.name if place.site else ''
                item = {
                    'place': place.name,
                    'site': site,
                }

                places.append(item)

            item = {
                'period': str(period),
                'places': places,
                'link': reverse('adv_cabinet:banner', kwargs={'banner_id': period.banner.pk})
            }
            data.append(item)

        return data


class LogListAPIView(ListAPIView):
    """Статистика размещений"""

    serializer_class = LogListSerializer
    permission_classes = (IsAuthenticated, IsBusinessAccount,)

    def get_log_action_cnt(self, logs, action, date):
        return logs.filter(action=action, date=date).values_list('cnt', flat=True).first() or 0

    def get_queryset(self):

        banner = Banner.objects.filter(id=self.kwargs['pk']).first()
        if not banner:
            raise NotFound()

        date_start = parse_date(self.request.query_params.get('date_start'))
        date_end = parse_date(self.request.query_params.get('date_end'))

        filters = {}
        if date_start:
            filters['date__gte'] = date_start

        if date_end:
            filters['date__lte'] = date_end

        # Фильтр по датам периодов размещения
        date_filters = []

        for period in banner.period_set.all():
            date_filters.append(Q(date__gte=period.date_from, date__lte=period.date_to))

        date_query = date_filters.pop()
        for item in date_filters:
            date_query |= item

        logs = Log.objects.filter(banner_id=banner.pk).filter(**filters).filter(date_query)

        result = logs.aggregate(Max('date'), Min('date'))

        date_min = result['date__min']
        date_max = result['date__max']

        if not (date_min and date_max):
            # если нет данных просмотров за этот период
            return []

        delta = date_max - date_min

        data = []

        for i in range(delta.days + 1):
            curr_date = date_min + timedelta(days=i)

            views = self.get_log_action_cnt(logs, Log.ACTION_VIEW, curr_date)
            scrolls = self.get_log_action_cnt(logs, Log.ACTION_SCROLL, curr_date)
            clicks = self.get_log_action_cnt(logs, Log.ACTION_CLICK, curr_date)

            ctr = '%.2f' % (float(clicks) / views * 100) if views and clicks else 0

            item = {'date': curr_date,
                    'views': views,
                    'scrolls': scrolls,
                    'clicks': clicks,
                    'ctr': ctr}

            data.append(item)
        return data
