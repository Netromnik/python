# -*- coding: utf-8 -*-

import datetime

import pytz
from django.utils.feedgenerator import Rss201rev2Feed, rfc2822_date
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.html import strip_tags

from irk.options.models import Site
from irk.news.models import News
from irk.utils.templatetags.str_utils import do_typograph
from irk.news.feeds.yandex import YandexFeed

__all__ = ('NewsFeed', 'YandexFeed')


timezone = pytz.timezone(settings.TIME_ZONE)


class NewsFeed(Rss201rev2Feed):
    """RSS новостей"""

    def __init__(self):
        super(NewsFeed, self).__init__(
            u'Твой Иркутск', u'https://www.irk.ru',
            u'Сайт для иркутян и гостей города.',
            feed_url='{}www.irk.ru{}'.format(settings.SITE_SCHEMA, reverse('news_rss')),
        )

        dt = datetime.datetime.now()-datetime.timedelta(minutes=5)
        news_site = Site.objects.get(slugs='news')
        self.items = News.material_objects.filter(sites=news_site, created__lte=dt, is_hidden=False,
                                         is_payed=False).order_by('-stamp', '-pk')[:15]

    def rss_attributes(self):
        attrs = super(NewsFeed, self).rss_attributes()
        attrs.update({'xmlns:dc': 'http://purl.org/dc/elements/1.1/'})

        return attrs

    def add_item_elements(self, handler, item):
        item = item.cast()
        url = item.get_absolute_url()
        if not url.startswith('http'):
            # Для новостей, которые содержат в заголовке BB код [url] возвращается полный адрес
            url = '{}www.irk.ru{}?utm_source=rss&utm_medium=rss_feed&utm_campaign=rss1'.format(settings.SITE_SCHEMA, url)

        updated = timezone.localize(item.updated)
        handler.addQuickElement(u'title', strip_tags(do_typograph(item.title, 'title,false')))
        handler.addQuickElement(u'link', url)
        handler.addQuickElement(u'description', do_typograph(item.caption or ''))
        handler.addQuickElement(u'pubDate', rfc2822_date(updated).decode('utf-8'))
        handler.addQuickElement(u'guid', url)

    def write_items(self, handler):
        """
        Выбираются последние новости, кроме последних 5 минут
        5 минут даются, чтобы редактор успел отредактировать новость
        """

        for item in self.items:
            handler.startElement(u'item', self.item_attributes(item))
            self.add_item_elements(handler, item)
            handler.endElement(u'item')

    def latest_post_date(self):
        updates = [i.updated for i in self.items]
        if len(updates) > 0:
            updates.sort()
            return timezone.localize(updates[-1])
        else:
            return timezone.localize(datetime.datetime.now())
