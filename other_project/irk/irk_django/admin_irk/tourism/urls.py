# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from irk.news.helpers import site_news_urls
from irk.polls.helpers import poll_urls
from irk.tourism import views
from irk.tourism.views import firms, companion, tour, article, infographic, transp, place

app_name = 'tourism'

articles_urlpatterns = (
    [
        url(r'^$', RedirectView.as_view(url=reverse_lazy('tourism:index'), permanent=True), name='index'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', article.read, name='read'),
    ], 'article'
)

companion_urlpatterns = (
    [
        url(r'^$', companion.search_companion, name='search'),
        url(r'^create/$', companion.create_companion, name='create'),
        url(r'^my/$', companion.my_companion, name='my'),
        url(r'^my/delete/(?P<companion_id>\d+)/$', companion.delete_companion, name='delete'),
        url(r'^my/edit/(?P<companion_id>\d+)/$', companion.edit_companion, name='edit'),
        url(r'^(?P<companion_id>\d+)/$', companion.read_companion, name='read'),
    ], 'companion'
)

firm_urlpatterns = (
    [
        url(r'^(?P<section_slug>\w+)/search/$', RedirectView.as_view(url=reverse_lazy('tourism:search'),
                                                                     permanent=True), name='section_search'),
        url(r'^(?P<section_slug>\w+)/$', firms.section_firm_list, {'content_model': True}, name='section_firm_list'),
        url(r'^(?P<section_slug>\w+)/create/$', firms.create, name='create'),
        url(r'^(?P<section_slug>\w+)/(?P<firm_id>\d+)/$', firms.section_firm, {'content_model': True}, name='read'),
        url(r'^(?P<section_slug>\w+)/(?P<firm_id>\d+)/edit/$', firms.edit_firm, {'content_model': True}, name='edit'),
        url(r'^(?P<section_slug>\w+)/(?P<firm_id>\d+)/add_tour/$', tour.add_tour, name='add_tour'),
    ], 'firm'
)

tour_urlpatterns = (
    [
        url(r'^(?P<tour_id>\d+)/$', tour.read_tour, name='read'),
        url(r'^(?P<tour_id>\d+)/success/$', tour.success_tour, name='success'),
        url(r'^(?P<tour_id>\d+)/edit/$', tour.edit_tour, name='edit'),
        url(r'^(?P<tour_id>\d+)/delete/$', tour.delete_tour, name='delete'),
        url(r'^(?P<tour_id>\d+)/update_status/$', tour.update_status, name='update_status'),
    ], 'tour'
)

infographic_urlpatterns = (
    [
        url(r'^$', infographic.index, name='index'),
        url(r'^(?P<pk>\d+)/$', infographic.read, name='read'),
    ], 'infographic'
)

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^search/$', views.global_search, name='search'),

    # Бронирование билетов
    url(r'^avia/$', views.aviasales, name='aviasales'),
    url(r'^hotel/order/$', views.hotel_order, name='hotel_order'),

    # Фирмы
    url(r'^yp/', include(firm_urlpatterns)),

    # Компаньоны
    url(r'^companion/', include(companion_urlpatterns)),

    # Туры
    url(r'^tour/', include(tour_urlpatterns)),

    # Блог туризма (Статьи)
    url(r'^blog/', include(articles_urlpatterns)),

    # Инфографика
    url(r'^graphics/', include(infographic_urlpatterns)),

    # Транспорт
    url(r'^etrains/$', transp.transport_etrains, name='transport_etrains'),
    url(r'^trains/$', transp.transport_trains, name='transport_trains'),
    url(r'^suburban/$', RedirectView.as_view(url='/news/transport1/', permanent=True), name='suburban'),
    url(r'^gardening/$', RedirectView.as_view(url='/news/transport1/', permanent=True), name='gardening'),
    url(r'^airport/$', transp.air_board, name='airport'),

    # Места отдыха
    url(r'^places/$', place.places, name='places'),
    url(r'^places/(?P<type_slug>\w+)/$', place.places, name='places'),
    url(r'^(?P<place_slug>\w+)/$', place.place, name='place'),
    url(r'^(?P<parent_slug>\w+)/(?P<place_slug>\w+)/$', place.sub_place, name='sub_place'),

]

urlpatterns += site_news_urls(__name__, 'news')

# Голосования
urlpatterns += poll_urls('tourism')
