# -*- coding: utf-8 -*-

from django.views.generic import RedirectView
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy

from irk.news.urls import site_news_urls


urlpatterns = patterns('newyear2014.views',
    url(r'^$', 'index'),
    url(r'^afisha/$', 'afisha.index'),

    # Sections for new year 2016
    url(r'^corporates/$', 'corporates', name='newyear_corporates'),

    url(r'^offers/$', 'offers.index'),
    url(r'^offers/(?P<offer_id>\d+)/$', 'offers.read'),
    url(r'^horoscope/$', 'horoscope.index'),
    url(r'^horoscope/(?P<horoscope_id>\d+)/$', 'horoscope.read'),
    url(r'^horoscope/zodiac/(?P<zodiac_id>\d+)/$', 'horoscope.zodiac_read'),
    url(r'^prediction/$', 'prediction.index'),
    url(r'^wish/$', 'wish.index'),
    url(r'^wish/sent/$', 'wish.sent'),
    url(r'^guru/$', 'guru.index'),
    url(r'^games/$', 'games.index'),
    url(r'^games/climber/$', 'climber.index'),
    url(r'^games/puzzle/$', 'puzzle.index'),
    url(r'^congratulation/$', 'congratulation.index'),
    url(r'^contests/$', 'contests.index'),
    url(r'^contests/text/$', RedirectView.as_view(url=reverse_lazy('newyear2014.views.contests.index'),
                                                  permanent=False)),
    url(r'^contests/photo/$', RedirectView.as_view(url=reverse_lazy('newyear2014.views.contests.index'),
                                                   permanent=False)),
    url(r'^contests/text/(?P<pk>\d+)/$', 'contests.text.read'),
    url(r'^contests/text/(?P<pk>\d+)/participate/$', 'contests.text.create'),
    url(r'^contests/text/(?P<pk>\d+)/(?P<participant_id>\d+)/$', 'contests.text.participant'),
    url(r'^contests/photo/(?P<pk>\d+)/$', 'contests.photo.read'),
    url(r'^contests/photo/(?P<pk>\d+)/participate/$', 'contests.photo.create'),
    url(r'^contests/photo/(?P<pk>\d+)/(?P<participant_id>\d+)/$', 'contests.photo.participant'),
    url(r'^wallpapers/$', 'wallpapers.index'),
    url(r'^wallpapers/download/(?P<pk>\d+)/(?P<size>\w+)/$', 'wallpapers.download'),
    url(r'^graphics/$', 'infographic.index'),
    url(r'^graphics/(?P<pk>\d+)/$', 'infographic.read'),
    url(r'^instagram/(?P<tag_id>\d+)/$', 'instagram.instagram_tag'),
    url(r'^instagram/(?P<tag_id>\d+)/more/$', 'instagram.instagram_more'),

    # Перегружаем списки фоторепортажей и статей
    url(r'^photo/$', 'articles.photo'),
    url(r'^articles/$', 'articles.index'),
)

urlpatterns += site_news_urls(__name__, 'article', url_prefix='articles')
urlpatterns += site_news_urls(__name__, 'photo', url_prefix='photo')
