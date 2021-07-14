# -*- coding: utf-8 -*-

from rest_framework import generics
from django.utils.datastructures import MultiValueDictKeyError

from irk.news.models import News
from irk.news.api.serializers import NewsListSerializer, NewsReadSerializer


class NewsList(generics.ListAPIView):
    model = News
    serializer_class = NewsListSerializer
    paginate_by = 25
    paginate_by_param = 'page'
    filter_fields = ('slug', 'stamp', 'category')

    def get_queryset(self):
        qs = self.model.objects.filter(is_hidden=False).order_by('-stamp', '-pk').prefetch_related('category')
        try:
            since_id = int(self.request.QUERY_PARAMS['since_id'])
            qs = qs.filter(pk__gt=since_id)
        except (MultiValueDictKeyError, ValueError):
            pass
        try:
            before_id = int(self.request.QUERY_PARAMS['before_id'])
            qs = qs.filter(pk__lt=before_id)
        except (MultiValueDictKeyError, ValueError):
            pass

        return qs

news_list = NewsList.as_view()


class NewsRead(generics.RetrieveAPIView):
    model = News
    serializer_class = NewsReadSerializer

    def get_queryset(self):
        return self.model.objects.filter(is_hidden=False).order_by('-stamp', '-pk').prefetch_related('category')

news_read = NewsRead.as_view()
