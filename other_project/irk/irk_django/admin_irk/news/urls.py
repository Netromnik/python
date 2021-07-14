# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from irk.adwords import views as adwords_views
from irk.blogs import views as blogs_views
from irk.news import views as news_views
from irk.news.feeds.yandex import YandexZenView
from irk.news.views import articles, flash, infographic, live, photo, podcast, subjects, tilda_articles, video
from irk.news.views.opensearch import NewsOpenSearch
from irk.polls.helpers import poll_urls
from irk.testing.urls import testing_urls

app_name = 'news'


infographic_urlpatterns = (
    [
        url(r'^$', infographic.index, name='index'),
        url(r'^paginator/$', infographic.paginator, name='paginator'),
        url(r'^(?P<infographic_id>\d+)/$', infographic.read, name='read'),
    ], 'infographic'
)

flash_urlpatterns = (
    [
        url(r'^$', flash.index, name='index'),
        url(r'^dtp/$', flash.index_dtp, name='index_dtp'),
        url(r'^data/$', flash.data, name='data'),
        url(r'^(?P<flash_id>\d+)/$', flash.read, name='read'),
        url(r'^(?P<flash_id>\d+)/toggle/$', flash.toggle, name='toggle'),
    ], 'flash'
)

live_urlpatterns = (
    [
        url(r'^(?P<live_id>\d+)/update/$', live.update, name='update'),
        url(r'^(?P<live_id>\d+)/feed.rss$', live.feed, name='feed'),  # Фид для яндекс.новостей
    ], 'live'
)

articles_urlpatterns = (
    [
        url(r'^$', articles.index, name='index'),
        url(r'^(?P<slug>\w+)/$', articles.category, name='category'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', articles.read, name='read'),
    ], 'article'
)

tilda_urlpatterns = (
    [
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', tilda_articles.read, name='read'),
    ], 'tilda_article'
)

subjects_urlpatterns = (
    [
        url(r'^$', subjects.index, name='index'),
        # Кастомный сюжет для нового года
        url(r'^newyear2019/$', subjects.newyear2019_read, name='newyear2019_read', kwargs={'slug': 'newyear2019'}),
        url(r'^(?P<slug>[\w\d-]+)/$', subjects.read, name='read'),
        url(r'^(?P<slug>\d+)/$', subjects.read_legacy, name='read_legacy'),
    ], 'subjects'
)

photo_urlpatterns = (
    [
        url(r'^$', photo.index, name='index'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', photo.read, name='read'),
    ], 'photo'
)

video_urlpatterns = (
    [
        url(r'^$', video.index, name='index'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', video.read,
            name='read'),
    ], 'video'
)

podcast_urlpatterns = (
    [
        url(r'^$', podcast.index, name='index'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', podcast.read, name='read'),
    ], 'podcast'
)

news_urlpatterns = (
    [
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', news_views.archive, name='date'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', news_views.news_read, name='read'),
        url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<id>\d+)/$', news_views.news_read, name='read'),
        url(r'^$', news_views.index, name='index')
    ], 'news'
)

subscription_urlpatterns = (
    [
        url(r'^$', news_views.subscription, name='index'),
        url(r'^ajax/$', news_views.subscription_ajax, name='ajax'),
        url(r'^confirm/$', news_views.subscription_confirm, name='confirm'),
        url(r'^unsubscribe/$', news_views.subscription_unsubscribe, name='unsubscribe'),
    ], 'subscription'
)

blogs_urlpatterns = (
    [
        url(r'^$', blogs_views.index, name='index'),
        url(r'^authors/$', blogs_views.authors, name='authors'),
        url(r'^(?P<username>[\.\s\w-]+)/$', blogs_views.author, name='author'),
        url(r'^(?P<username>[\.\s\w-]+)/(?P<entry_id>\d+)/$', blogs_views.read, name='read'),
        url(r'^(?P<username>[\.\s\w-]+)/(?P<entry_id>\d+)/update/$', blogs_views.update, name='update'),
        url(r'^(?P<username>[\.\s\w-]+)/(?P<entry_id>\d+)/publish/$', blogs_views.publish, name='publish'),
        url(r'^(?P<username>[\.\s\w-]+)/create/$', blogs_views.create, name='create'),
    ], 'blogs'
)

# Голосования
urlpatterns = poll_urls('news')

# Тесты
urlpatterns += testing_urls('news')


urlpatterns += [
    url(r'^search/$', news_views.search, name='search'),
    url(r'^opensearch/$', NewsOpenSearch.as_view(), name='opensearch'),
    url(r'^api/', include('irk.news.api.urls')),

    url(r'^yandex.rss$', news_views.yandex_rss, name='yandex_rss'),
    url(r'^yandex/zen/$', YandexZenView(), name='yandex_zen'),
    url(r'^calendar/$', news_views.calendar_block, name='calendar'),

    # Блоги
    url(r'^blogs/', include(blogs_urlpatterns)),

    # Подписка на новости
    url(r'^subscription/', include(subscription_urlpatterns)),

    # Статьи
    url(r'^articles/', include(articles_urlpatterns)),

    # Тильдовские статьи
    url(r'^tarticles/', include(tilda_urlpatterns)),

    # Сюжеты
    url(r'^subjects/', include(subjects_urlpatterns)),

    # Фото
    url(r'^photo/', include(photo_urlpatterns)),

    # Видео
    url(r'^video/', include(video_urlpatterns)),

    # Подкасты
    url(r'^podcast/', include(podcast_urlpatterns)),

    # Инфографика
    url(r'^graphics/', include(infographic_urlpatterns)),

    # Народные новости
    url(r'^flash/', include(flash_urlpatterns)),

    # Онлайн-трансляции
    url(r'^live/', include(live_urlpatterns)),

    # Эксперт
    url(r'^expert/', include('irk.experts.urls')),

    # Новости компаний
    url(r'^company/(?P<news_id>\d+)/$', adwords_views.company_news_read, name='company_news_read'),

    # Статистика кликов по соц. кнопкам
    url(r'^share-click/(?P<pk>\d+)/(?P<slug>\w+)/$', news_views.share_click, name='share_click'),

    # Примеры писем рассылки новостей
    url(r'^newsletter/(?P<period>\w+)/$', news_views.newsletter_materials, name='newsletter_materials'),

    # Новости
    url(r'^', include(news_urlpatterns)),

    # Раздел новостей
    url(r'^(?P<slug>\w+)/$', news_views.news_type, name='news_type'),

    # Главная новостей
    url(r'^$', news_views.index, name='index'),
]
