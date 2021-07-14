# -*- coding: utf-8 -*-
"""
Переадресация старых урлов спецпроектов на новые
Раньше материалы при прикреплении к спецпроекту меняли юрл. Теперь нет.
"""

from django.conf.urls import url
from django.http.response import HttpResponsePermanentRedirect

from irk.news.models import BaseMaterial


def redirect_index(request, slug):
    """
    Редирект индекса спецпроекта
    /news/9may/ -> /special/9may/
    /news/9may/photo/ -> /special/9may/
    """

    return HttpResponsePermanentRedirect('/special/{}/'.format(slug))


def redirect_read(request, pk):
    """
    Редирект конкретного материала
    /news/school/article/90560/ -> /news/articles/20200618/fest/
    """

    url = BaseMaterial.objects.get(id=pk).get_absolute_url()
    return HttpResponsePermanentRedirect(url)


def special_project_urls(app, slug):
    types = 'article|photo|graphics|video|review'
    urlpatterns = [
        # индексы
        url(r'^{}/({})/(?:(?:{})/)?$'.format(app, slug, types), redirect_index),
        # риды
        url(r'^{}/{}/(?:{})/(\d+)/$'.format(app, slug, types), redirect_read),
    ]

    return urlpatterns


urlpatterns = special_project_urls('afisha', 'film')
urlpatterns += special_project_urls('afisha', 'jazz')

urlpatterns += special_project_urls('obed', 'columnist')

urlpatterns += special_project_urls('tourism', 'abroad')
urlpatterns += special_project_urls('tourism', 'club')

urlpatterns += special_project_urls('news', '9may')
urlpatterns += special_project_urls('news', 'alphabet')
urlpatterns += special_project_urls('news', 'anniversary')
urlpatterns += special_project_urls('news', 'books')
urlpatterns += special_project_urls('news', 'building')
urlpatterns += special_project_urls('news', 'buildingtime')
urlpatterns += special_project_urls('news', 'collection')
urlpatterns += special_project_urls('news', 'court')
urlpatterns += special_project_urls('news', 'experience')
urlpatterns += special_project_urls('news', 'fabrika-betonov')
urlpatterns += special_project_urls('news', 'family')
urlpatterns += special_project_urls('news', 'favourite')
urlpatterns += special_project_urls('news', 'financial')
urlpatterns += special_project_urls('news', 'health')
urlpatterns += special_project_urls('news', 'help')
urlpatterns += special_project_urls('news', 'how')
urlpatterns += special_project_urls('news', 'inspection')
urlpatterns += special_project_urls('news', 'japan')
urlpatterns += special_project_urls('news', 'online')
urlpatterns += special_project_urls('news', 'podcasting')
urlpatterns += special_project_urls('news', 'policy')
urlpatterns += special_project_urls('news', 'problems')
urlpatterns += special_project_urls('news', 'remont')
urlpatterns += special_project_urls('news', 'uncomfortable')
urlpatterns += special_project_urls('news', 'videointerview')
urlpatterns += special_project_urls('news', 'vote')
urlpatterns += special_project_urls('news', 'startup')
urlpatterns += special_project_urls('news', 'school')
