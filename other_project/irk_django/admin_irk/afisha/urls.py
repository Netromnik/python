# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from irk.afisha import views
from irk.afisha.views import announces, events, articles, event, photo, reviews
from irk.afisha.views.opensearch import EventsOpenSearch
from irk.news.helpers import site_news_urls
from irk.polls.helpers import poll_urls
from irk.testing.urls import testing_urls

app_name = 'afisha'

urlpatterns = site_news_urls(__name__, 'news')

urlpatterns += poll_urls('afisha')
urlpatterns += testing_urls('afisha')

contests_urlpatterns = (
    [
        url(r'^$', views.contests_list, name='list'),
        url(r'^(?P<slug>[-\w]+)/$', views.contests_read, name='read'),
        url(r'^(?P<slug>[-\w]+)/(?P<participant_id>\d+)/$', views.participant_read, name='participant_read'),
        url(r'^(?P<slug>[-\w]+)/add/$', views.participant_create, name='participant_create'),
    ], 'contests'
)

announces_urlpatterns = (
    [
        url(r'^$', announces.events_list, name='events_list'),
        # Ajax-endpoint для блока дополнительных анонсов
        url(r'^extra/$', announces.extra_announcements, name='extra'),
        url(r'^extra/(?P<event_type_alias>[-\w]+)/$', announces.extra_announcements,
            name='extra'),
        url(r'^(?P<event_type>[^\/]+)/$', announces.events_list, name='events_list'),
    ], 'announces'
)

reviews_urlpatterns = (
    [
        url(r'^$', reviews.index, name='index'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', reviews.read, name='read'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<id>\d+)/$', reviews.read, name='read'),
    ], 'review'
)

article_urlpatterns = (
    [
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', articles.read,
            name='read'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<id>\d+)/$', articles.read,
            name='read'),
    ], 'article'
)

photo_urlpatterns = (
    [
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', photo.read,
            name='read'),
    ], 'photo'
)

urlpatterns += [
    # Анонсы
    url(r'^announces/', include(announces_urlpatterns)),

    url(r'^photo/', include(photo_urlpatterns)),

    url(r'^materials/extra/$', articles.extra_materials, name='events_extra_materials'),
    url(r'^cinema/extra/$', events.extra_cinema, name='events_extra_cinema'),
    url(r'^culture/extra/$', events.extra_culture, name='events_extra_culture'),

    # Фотоконкурсы
    url(r'^contests/', include(contests_urlpatterns)),

    # Ajax Endpoints
    url(r'^events/$', events.events_list, name='events_list'),
    url(r'^(?P<event_type>[a-z]+)/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/events/$', events.events_list,
        name='events_list'),
    url(r'^(?P<event_type>[a-z]+)/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<event_id>\d+)/sessions/$',
        event.sessions, name='event_session'),
    url(r'^events/calendar/$', events.calendar_paginator, name='events_calendar_paginator'),
    url(r'^events/calendar-carousel/$', events.calendar_carousel, name='events_calendar_carousel'),

    # Создание пользователями событий
    url(r'^create/$', views.create, name='event_create'),
    url(r'^created/commercial/$', views.created, {'is_commercial': 'true'}, name='commercial_event_created'),
    url(r'^created/$', views.created, name='event_created'),

    url(r'^search/$', event.search, name='search'),
    url(r'^opensearch/$', EventsOpenSearch.as_view(), name='opensearch'),

    # Статьи афиши
    url(r'^articles/', include(article_urlpatterns)),

    # Рецензии на события
    url(r'^reviews/', include(reviews_urlpatterns)),

    # Пользователь нажал на кнопку "Купить билет"
    url(r'^buy-button-click/$', event.buy_button_click, name='buy_button_click'),

    # События
    url(r'^(?P<event_type>[a-z]+)/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<event_id>\d+)/$', event.read,
        name='event_read'),
    url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<event_id>\d+)/$', event.event_redirect,
        name='event_redirect'),
    url(r'^(?P<event_type>[a-z]+)/(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', events.type_index,
        name='events_type_index'),
    url(r'^(?P<event_type>[a-z]+)/$', events.type_index, name='events_type_index'),

    # Главная
    url(r'^$', views.index, name='index'),
]
