# -*- coding: utf-8 -*-

"""RSS для Яндекс.ленты"""

import datetime
import mimetypes
import os
import logging

import bleach
import pytz
from sorl.thumbnail.base import ThumbnailException
from sorl.thumbnail.main import DjangoThumbnail

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.utils.feedgenerator import DefaultFeed, RssFeed, rfc2822_date, Enclosure
from django.utils.html import strip_tags
from django.utils.encoding import smart_text

from irk.afisha.models import Article as AfishaArticle
from irk.afisha.models import Photo as AfishaPhoto
from irk.afisha.models import Review as AfishaReview
from irk.news.models import Article as NewsArticle
from irk.news.models import Photo as NewsPhoto
from irk.news.models import BaseMaterial, Live, News, Subject, TildaArticle
from irk.obed.models import Article as ObedArticle
from irk.obed.models import Review as ObedReview
from irk.options.models import Site
from irk.utils.files.helpers import static_link
from irk.utils.templatetags.str_utils import do_typograph
from irk.utils.text.processors.zen import processor as zen_processor

timezone = pytz.timezone(settings.TIME_ZONE)
log = logging.getLogger(__name__)


class YandexFeed(RssFeed):
    """RSS новостей для экспорта в Яндекс

    Спецификация формата:
    """

    _version = u'2.0'

    def __init__(self):
        super(YandexFeed, self).__init__(
            u'Твой Иркутск', u'http://www.irk.ru',
            u'Сайт для иркутян и гостей города.',
            feed_url='{}www.irk.ru{}'.format(settings.SITE_SCHEMA, reverse('news:yandex_rss')),
        )

        dt = datetime.datetime.now() - datetime.timedelta(minutes=5)
        news_site = Site.objects.get(slugs='news')
        self.items = News.objects.filter(sites=news_site, created__lte=dt, is_hidden=False,
                                         is_payed=False, is_exported=True).order_by('-pk')[:15]

    def rss_attributes(self):
        attrs = super(YandexFeed, self).rss_attributes()
        attrs.update({'xmlns:yandex': 'http://news.yandex.ru'})
        return attrs

    def add_root_elements(self, handler):
        super(YandexFeed, self).add_root_elements(handler)
        handler.addQuickElement(u'yandex:logo', static_link('img/rss-logo.png'))
        handler.addQuickElement(u'yandex:logo', static_link('img/rss-logo-square.png'), attrs={'type': 'square'})

    def add_item_elements(self, handler, item):
        item = item.cast()
        url = item.get_absolute_url()
        if not url.startswith('http://'):
            # Для новостей, которые содержат в заголовке BB код [url] возвращается полный адрес
            url = '{}www.irk.ru{}?utm_source=rss2&utm_medium=rss_feed&utm_campaign=rss_ya'.format(
                settings.SITE_SCHEMA, url
            )

        updated = timezone.localize(item.updated)
        handler.addQuickElement(u'title', strip_tags(do_typograph(item.title, 'title,false')))
        handler.addQuickElement(u'link', url)
        handler.addQuickElement(u'description', do_typograph(item.caption or ''))
        handler.addQuickElement(u'pubDate', rfc2822_date(updated).decode('utf-8'))
        handler.addQuickElement(u'yandex:full-text', do_typograph(item.content))
        handler.addQuickElement(u'guid', url)

        self.add_official_comment(handler, item)
        self.add_video(handler, item)

        try:
            thumb = DjangoThumbnail(item.gallery.main_image().image, (300, 275))
            handler.addQuickElement(u'enclosure', attrs={'type': 'image/jpeg', 'url': thumb.absolute_url})
        except (AttributeError, ThumbnailException):
            pass

        try:
            live = Live.objects.filter(news=item)[0]  # TODO: выборка через .values_list('id', flat=True)
            handler.addQuickElement(
                u'yandex:online',
                '{}www.irk.ru{}'.format(settings.SITE_SCHEMA, reverse('news:live:feed', args=[live.pk, ]))
            )
        except IndexError:
            pass

        try:
            handler.addQuickElement(u'category', item.news_category.title)
        except (AttributeError, Subject.DoesNotExist):
            pass


    def add_official_comment(self, handler, item):
        """ Официальный комментарий """
        if item.official_comment_text:
            handler.startElement(u'yandex:official-comment', {})

            attrs = {'origin-name': item.official_comment_name, 'anchor': 'official-comment'}
            if item.official_comment_link:
                attrs['origin'] = item.official_comment_link
            if item.official_comment_logo:
                attrs['logo'] = item.official_comment_logo.url
            handler.addQuickElement(u'yandex:comment-text', item.official_comment_text, attrs=attrs)
            if item.official_comment_bind:
                handler.addQuickElement(u'yandex:bind-to', item.official_comment_bind)

            handler.endElement(u'yandex:official-comment')

    def add_video(self, handler, item):
        """Видео"""

        if item.rss_video_preview and item.rss_video_link:
            handler.startElement(u'media:group', {})
            handler.addQuickElement(u'media:player', attrs={'url': item.rss_video_link})
            handler.addQuickElement(u'media:thumbnail', attrs={'url': item.rss_video_preview.url})
            handler.endElement(u'media:group')

    def write_items(self, handler):
        """Выбираются последние новости, кроме последних 5 минут

        Это дается на то время, чтобы редактор успел отредактировать новость
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


class YandexLiveFeed(RssFeed):
    _version = u'2.0'

    def __init__(self, live):
        title = do_typograph(live.news, 'title')
        super(YandexLiveFeed, self).__init__(
            title, live.news.get_absolute_url(),
            title, feed_url='{}www.irk.ru{}'.format(
                settings.SITE_SCHEMA, reverse('news:live:feed', args=[live.pk, ])
            ),
        )

        self.live = live

        self.items = live.entries.all().order_by('-date', '-created')

    def add_item_elements(self, handler, item):
        handler.addQuickElement('description', do_typograph(item.text, 'admin,True'))
        item_datetime_created = datetime.datetime.combine(self.live.news.stamp, item.created)
        handler.addQuickElement('pubDate', rfc2822_date(timezone.localize(item_datetime_created)).decode('utf-8'))

    def latest_post_date(self):
        try:
            last_post_time = self.live.entries.all().order_by('-date', '-created').values_list('created', flat=True)[0]
        except IndexError:
            last_post_time = datetime.datetime.now().time()
        last_post_datetime = datetime.datetime.combine(self.live.news.stamp, last_post_time)
        return timezone.localize(last_post_datetime)


class YandexZenFeed(DefaultFeed):
    """Yandex Zen feed generator"""

    def rss_attributes(self):
        return {
            'version': '2.0',
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
            'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
            'xmlns:media': 'http://search.yahoo.com/mrss/',
            'xmlns:atom': 'http://www.w3.org/2005/Atom',
            'xmlns:georss': 'http://www.georss.org/georss',
        }

    def add_root_elements(self, handler):
        # Переопределяем поле language, иначе оно берется из settings, где представлено в другом формате.
        if self.feed['language'] is not None:
            self.feed['language'] = 'ru'

        super(YandexZenFeed, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        super(YandexZenFeed, self).add_item_elements(handler, item)

        if item['author'] is not None:
            handler.addQuickElement('author', item['author'])

        handler.addQuickElement('content:encoded', item['content'])


class YandexZenView(Feed):
    feed_type = YandexZenFeed
    title = u'Твой Иркутск'
    link = reverse_lazy('news:yandex_zen')
    description = u'Сайт для иркутян и гостей города.'
    material_limit = 50

    def items(self):
        subclasses = (NewsArticle, NewsPhoto, AfishaArticle, AfishaReview, AfishaPhoto, ObedArticle, ObedReview, TildaArticle)
        materials = (BaseMaterial.longread_objects
            .filter_models(*subclasses)
            .filter(is_advertising=False, is_hidden=False)
            .order_by('-stamp')
            .select_subclasses(*subclasses)
            [:self.material_limit]
        )

        return materials

    def item_pubdate(self, item):
        try:
            return datetime.datetime.combine(item.stamp, item.published_time)
        except TypeError:
            return datetime.datetime.combine(item.stamp, datetime.time(11, 0))

    def item_description(self, item):
        return self.typograph(item.caption)

    def item_extra_kwargs(self, item):
        return {
            'author': item.author,
            'content': self.get_content(item),
        }

    def get_content(self, item):

        content = ''
        content += self.get_first_image_content(item)
        if isinstance(item, TildaArticle):
            content += item.prepare_content()
        else:
            content += self.typograph(item.content)

        return content

    def get_first_image_content(self, item):
        if not item.wide_image:
            return ''
        try:
            context = {
                'src': item.wide_image.url,
                'title': item.image_label if hasattr(item, 'image_label') else '',
                'width': item.wide_image.width,
                'height': item.wide_image.height,
            }
        except IOError as err:
            log.error("Can't load image file {}. Error: {}".format(item.wide_image, err))
            return ''

        return render_to_string('bb_codes/zen/image.html', context)

    def item_enclosures(self, item):
        if not item.wide_image:
            return []

        enc = Enclosure(
            url=item.wide_image.url,
            length=smart_text(self._filesize(item.wide_image.name)),
            mime_type=smart_text(self._mimetype(item.wide_image.name)))
        return [enc]

    def get_first_image_enc(self, item):
        if not item.wide_image:
            return []

        return [{'url': item.wide_image.url, 'type': self._mimetype(item.wide_image.name)}]

    def get_pictures_enc(self, item):
        gallery = item.gallery.main()
        if not gallery:
            return []

        pictures = gallery.pictures.order_by('-gallerypicture__main')
        enclosures = []
        for pic in pictures:
            # fix bug: если mimetype вернет None, то xml writer не сможет потом вывести ленту
            # пусть лучше будет пустая строка
            mime = self._mimetype(pic.image.name) or ''
            enclosures.append({
                'url': pic.image.url,
                'type': mime,
            })

        return enclosures

    def typograph(self, value):
        value = bleach.clean(value, strip=True)
        return zen_processor.format(value, escape_html=False)

    def _mimetype(self, filename):
        _, ext = os.path.splitext(filename)
        return mimetypes.types_map.get(ext)

    def _filesize(self, filename):
        full_path = os.path.join(settings.MEDIA_ROOT, filename)
        return os.path.getsize(full_path)
