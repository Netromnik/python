# -*- coding: utf-8 -*-

from rest_framework import generics

from irk.map.models import Cities as City, Countryside, Cooperative
from irk.map.api.serializers import CitySerializer
from irk.utils.http import JsonResponse


class CityList(generics.ListAPIView):
    model = City
    serializer_class = CitySerializer

    def get_queryset(self):
        return self.model.objects.filter(cites__slugs='weather').order_by('id')

city_list = CityList.as_view()


class CityInstance(generics.RetrieveAPIView):
    model = City
    serializer_class = CitySerializer

    def get_queryset(self):
        return self.model.objects.filter(cites__slugs='weather')

city_instance = CityInstance.as_view()


def autocomplete_countryside(request):
    """Автодополнение для Садоводств"""

    query = request.GET.get('query', '')
    result = [
        {'value': title, 'data': id_}
        for title, id_ in Countryside.objects.filter(title__icontains=query).values_list('title', 'id')[:10]
    ]

    return JsonResponse({
        'query': query,
        'suggestions': result,
    })


def autocomplete_cooperative(request):
    """Автодополнение для Кооперативов"""

    query = request.GET.get('query', '')
    result = [
        {'value': title, 'data': id_}
        for title, id_ in Cooperative.objects.filter(title__icontains=query).values_list('title', 'id')[:10]
    ]

    return JsonResponse({
        'query': query,
        'suggestions': result,
    })
