# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from irk.obed import views
from irk.obed.views import establishment, articles, comments
from irk.polls.helpers import poll_urls
from irk.testing.urls import testing_urls

app_name = 'obed'


contests_urlpatterns = (
    [
        url(r'^$', views.contests_list, name='list'),
        url(r'^(?P<slug>[-\w]+)/$', views.contests_read, name='read'),
        url(r'^(?P<slug>[-\w]+)/(?P<participant_id>\d+)/$', views.participant_read, name='participant_read'),
        url(r'^(?P<slug>[-\w]+)/add/$', views.participant_create, name='participant_create'),
    ], 'contests'
)

establishment_urlpatterns = (
    [
        url(r'^(?P<firm_id>\d+)/events/$', establishment.tab_content, {'tab_name': 'events'}, name='events'),
        url(r'^(?P<firm_id>\d+)/menu/$', establishment.tab_content, {'tab_name': 'menu'}, name='menu'),
        url(r'^(?P<firm_id>\d+)/comments/$', establishment.tab_content, {'tab_name': 'comments'}, name='comments'),
        url(r'^add/$', establishment.add, name='add'),
        url(r'^(?P<firm_id>\d+)/edit/$', establishment.edit, name='edit')
    ], 'establishment'
)

articles_urlpatterns = (
    [
        url(r'^$', articles.article_list, name='index'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', articles.article_read, name='read'),
        url(r'^see_also/(?P<category_id>\d+)/$', articles.see_also_list, name='see_also_list'),
        url(r'^(?P<section_category_slug>[\w\d-]+)/$', articles.category_article_list,
            name='category'),
    ], 'article'
)

reviews_urlpatterns = (
    [
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', articles.review_read, name='read'),
    ], 'review'
)

tilda_urlpatterns = (
    [
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', articles.tilda_read, name='read'),
    ], 'tilda'
)

urlpatterns = poll_urls('obed')
urlpatterns += testing_urls('obed')
urlpatterns += [

    # Фотоконкурсы
    url(r'^contests/', include(contests_urlpatterns)),

    # Ajax заведения
    url(r'^establishment/', include(establishment_urlpatterns)),

    # Заведение
    url(r'^catering/establishment/(?P<firm_id>\d+)/$', establishment.direct_redirect),
    url(r'^(?P<section_slug>[\w]+)/establishment/(?P<firm_id>\d+)/$', establishment.read, name='establishment_read'),

    # Статьи
    url(r'^articles/', include(articles_urlpatterns)),
    url(r'^reviews/', include(reviews_urlpatterns)),
    url(r'^tarticles/', include(tilda_urlpatterns)),

    # Ajax-endpoint для последних отзывов на главной
    url(r'^comments/$', comments.recent_messages, name='recent_messages'),

    url(r'^search/$', views.search, name='search'),

    # Корпоративы и гастрономический фестиваль 1.04.2018
    url(r'^corporatives/$', views.corporatives, name='corporatives'),
    url(r'^barofest/$', views.barofest, name='barofest'),
    url(r'^summer-terraces/$', views.summer_terraces, name='summer_terraces'),
    url(r'^deliveries/$', views.deliveries, name='deliveries'),

    url(r'^corporatives/block/$', views.corporatives_block, name='corporatives_block'),
    url(r'^deliveries/block/$', views.delivery_block, name='delivery_block'),

    # Рассылка
    url(r'^events/$', views.subscribe, name='subscribe'),

    url(r'^list/$', establishment.section_list, name='list'),
    url(r'^(?P<section_slug>[-\w]+)/$', establishment.section_list, name='section_list'),

    url(r'^$', views.index, name='index'),
]
