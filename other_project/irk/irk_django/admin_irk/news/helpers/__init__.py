# -*- coding: utf-8 -*-

import datetime
import logging
import os.path
import re
import smtplib
from math import ceil

from PIL import Image
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from django.utils.functional import cached_property

from irk.news.helpers.cache import clear_cache, load_from_cache, save_to_cache
from irk.options.models import Site
from irk.utils.cache import invalidate_tags
from irk.utils.exceptions import raven_capture
from irk.utils.helpers import grouper
from irk.utils.notifications import tpl_notify

logger = logging.getLogger(__name__)

RE_TITLE = re.compile(r'\[url\s(.*?)\]')


class GMT(datetime.tzinfo):
    """Временная зона относительно GMT"""

    def __init__(self, hours, minutes=0):
        self.hours = hours
        self.minutes = minutes

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.hours, minutes=self.minutes)

    def tzname(self, dt):
        return 'GMT +%s' % self.hours

    def dst(self, dt):
        return datetime.timedelta(0)


def twitter_image(url, large=False):
    """Возвращает адрес изображения по URL оригинальной фотографии

    Поддерживаются plixi.com, twitpic.com, yfrog.com"""

    if 'plixi.com' in url:
        return 'http://api.plixi.com/api/tpapi.svc/imagefromurl?size=640&url=%s' % url
    if 'yfrog.com' in url:
        return '%s:iphone' % url
    if 'twitpic.com' in url:
        if large:
            return 'http://twitpic.com/show/large/%s' % url.replace('http://twitpic.com', '').strip('/')
        return 'http://twitpic.com/show/thumb/%s' % url.replace('http://twitpic.com', '').strip('/')
    return None


def twitter_images(text):
    """Возвращает список изображений из твита"""

    links = re.findall(r'\b(((https*\:\/\/)|www\.)[^\"\']+?)(([!?,.\)]+)?(\s|$))', text)
    links = [x[0] for x in links]
    images = []
    for link in links:
        image = twitter_image(link)
        large_image = twitter_image(link, large=True)
        if image:
            images.append({'image': image, 'link': link, 'large': large_image})

    return images


def news_date_url(app_label, model, date, urlconf='urls'):
    """Ссылка на список новостей за дату"""

    if isinstance(model, models.Model):
        ct = ContentType.objects.get_for_model(model)
        model = ct.model

    kwargs = {
        'year': date.year,
        'month': '%02d' % date.month,
        'day': '%02d' % date.day,
    }

    try:
        return reverse('%s:%s:date' % (app_label, model), kwargs=kwargs, urlconf=urlconf)
    except NoReverseMatch:
        return reverse('%s:news:date' % app_label, kwargs=kwargs, urlconf=urlconf)


def site_news_urls(app, model_name, url_prefix=None):
    from irk.news.models import News, Article, Video, Photo
    from irk.news.views.base.list import NewsListBaseView
    from irk.news.views.base.read import NewsReadBaseView
    from irk.news.views.base.date import NewsDateBaseView

    MODEL_MAPPINGS = {
        'news': News,
        'article': Article,
        'photo': Photo,
        'video': Video,
    }

    if app.startswith('irk.'):
        # irk.tourism.urls -> tourism.urls
        app = app[4:]

    app = app.split('.', 1)[0]

    model = MODEL_MAPPINGS[model_name]

    if url_prefix is None:
        url_prefix = model_name

    template_base = '%s/%s/' % (app, model_name)

    read_cls = type('ReadView', (NewsReadBaseView,),
                    {'model': model, 'template': os.path.join(template_base, 'read.html')})
    date_cls = type('ListView', (NewsDateBaseView,),
                    {'model': model, 'template': os.path.join(template_base, 'date.html')})
    list_cls = type('ListView', (NewsListBaseView,),
                    {'model': model, 'template': os.path.join(template_base, 'index.html')})

    read_view = read_cls.as_view()
    date_view = date_cls.as_view()
    list_view = list_cls.as_view()

    urlpatterns = (
        [
            url(r'^$', list_view, name='index'),
            url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/$', date_view, name='date'),
            url(r'^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d+)/(?P<slug>[\w\d-]+)/$', read_view, name='read'),
        ], model_name
    )

    return [
        url(r'^{}/'.format(model_name), include(urlpatterns))
    ]


class MaterialController(object):
    """
    Контроллер для выборки материалов с кэшированием и блэкджеком.

    Кэшируются только первые страницы, остальные подгружаются через ajax.
    """

    # Количество материалов в ленте. Если равно None, возвращаются все материалы.
    RIBBON_SIZE = 20
    # Количество материалов в блоке «Главное».
    IMPORTANT_SIZE = 3
    # Количество материалов в блоке справа.
    SIDEBAR_SIZE = 4
    # Не выводить новости, запланированные к публикации после этого момента в будущем
    FUTURE_WINDOW = {'minutes': 30}

    def __init__(self, show_hidden=False):
        """
        :param bool show_hidden: Если True, то учитываются скрытые материалы
        """

        self._show_hidden = show_hidden
        self._site_id = Site.objects.filter(slugs='news').values_list('id', flat=True).first()
        self._news_ct_ids = list(ContentType.objects.filter(model='news').values_list('id', flat=True))

    def pregenerate_cache(self):
        """Прегенерация кэша для всех списков материалов"""

        old_show_hidden = self._show_hidden

        for show_hidden in [False, True]:
            self._show_hidden = show_hidden

            self.save_ribbon_materials()
            self.save_important_materials()
            # Категории должны соответствовать категориям в рубрикаторе news_tags.RUBRICATOR_URLS
            category_slugs = ['crime', 'politics', 'transport', 'ecology', 'sport', 'culture', 'society',
                              'finance']
            for slug in category_slugs:
                self.save_ribbon_materials_for_category_first_page(slug)
                self.save_last_longrid_materials_for_category(slug)

        self._show_hidden = old_show_hidden

        invalidate_tags(['news', 'article', 'video', 'photo', 'infographic', 'expert', 'polls'])
        logger.debug('Pregeneration cache for materials successful')

    def exclude_payed_news(self, queryset):
        """ Исключить платные новости """
        from irk.news.models import News

        news_payed_ids = list(News.material_objects.filter(is_payed=True).values_list('id', flat=True))
        return queryset.exclude(id__in=news_payed_ids)

    def get_ribbon_materials(self, page=1):
        """Получить ленту материалов для Главной Новостей"""

        if page > 1:
            queryset = self._get_queryset_for_ribbon()

            # Исключить платные новости из основной ленты
            queryset = self.exclude_payed_news(queryset)

            queryset = self._slice_page(queryset, page, self.RIBBON_SIZE)
            materials = self._concretize(queryset)
        else:
            key = self._generate_cache_key('ribbon')
            materials = load_from_cache(key)

        return materials

    def save_ribbon_materials(self):
        """Сохранить ленту материалов для Главной Новостей"""

        queryset = self._get_queryset_for_ribbon()

        # Исключить платные новости из основной ленты
        queryset = self.exclude_payed_news(queryset)

        materials = queryset[:self.RIBBON_SIZE]
        key = self._generate_cache_key('ribbon')
        save_to_cache(key, materials)

    def get_ribbon_materials_for_date(self, date):
        """Лента материалов для архива"""

        queryset = self._get_queryset_for_ribbon()
        queryset = queryset.filter(stamp=date)

        return self._concretize(queryset)

    def get_ribbon_materials_for_category(self, slug, page_number):
        """Получить ленту материалов для page_number страницы по категории (рубрике)"""

        if page_number > 1:
            queryset = self._get_queryset_for_ribbon()
            queryset = self._filter_category(queryset, slug)
            queryset = self._slice_page(queryset, page_number, self.RIBBON_SIZE)
            materials = self._concretize(queryset)
        else:
            key = self._generate_cache_key('ribbon_{}'.format(slug))
            materials = load_from_cache(key)

        if slug == 'finance':
            materials = self._finance_insert_longreads(materials, page_number == 1)

        return materials

    def save_ribbon_materials_for_category_first_page(self, slug):
        """Сохранить ленту материалов для первой страницы по категории (рубрике)"""

        queryset = self._get_queryset_for_ribbon()
        queryset = self._filter_category(queryset, slug)
        queryset = self._slice_page(queryset, 1, self.RIBBON_SIZE)

        key = self._generate_cache_key('ribbon_{}'.format(slug))
        save_to_cache(key, queryset)

    def get_last_longrid_materials_for_category(self, slug):
        """Получить 4 последних лонгрида для рубрики."""

        key = self._generate_cache_key('sidebar_{}'.format(slug))
        materials = load_from_cache(key)

        return materials

    def save_last_longrid_materials_for_category(self, slug):
        """Сохранить 4 последних лонгрида для рубрики."""

        news_cts = list(ContentType.objects.filter(model='news').values_list('id', flat=True))

        queryset = self._get_queryset()
        queryset = queryset.filter(is_advertising=False).exclude(content_type_id__in=news_cts)
        queryset = self._filter_category(queryset, slug)
        materials = queryset[:self.SIDEBAR_SIZE]

        key = self._generate_cache_key('sidebar_{}'.format(slug))
        save_to_cache(key, materials)

    def get_important_materials(self):
        """Получить материалы для блока Главное/Важное"""

        key = self._generate_cache_key('important')
        materials = load_from_cache(key)

        return materials

    def save_important_materials(self):
        """Сохранить материалы для блока Главное/Важное"""

        queryset = self._get_queryset()
        queryset = queryset.filter(is_important=True)
        materials = queryset[:self.IMPORTANT_SIZE]

        key = self._generate_cache_key('important')
        save_to_cache(key, materials)

    def _get_queryset(self):
        """Вернуть queryset общий для всех запросов материалов"""

        from irk.news.models import BaseMaterial

        exclude_material_ct = [
            ContentType.objects.get_by_natural_key('news', 'metamaterial'),
        ]

        queryset = BaseMaterial.material_objects \
            .filter(sites=self._site_id) \
            .exclude(content_type__in=exclude_material_ct) \
            .order_by('-stamp', '-published_time')

        if not self._show_hidden:
            queryset = queryset.filter(is_hidden=False)
        else:
            # редактору мешают далеко запланированные материалы
            queryset = queryset.exclude_future_drafts(**self.FUTURE_WINDOW)

        return queryset

    def _get_queryset_for_ribbon(self):
        """Вернуть queryset для ленты"""

        from irk.news.models import BaseMaterial

        material_super_ids = list(BaseMaterial.material_objects.filter(is_super=True).values_list('id', flat=True))
        queryset = self._get_queryset()
        queryset = queryset.filter(is_advertising=False).exclude(id__in=material_super_ids)

        return queryset


    @staticmethod
    def _filter_category(queryset, slug):
        """
        Применить условия для категории

        :param queryset: объект запроса
        :param str slug: алиас категории
        """

        queryset = queryset.filter(category__slug=slug)

        return queryset

    def _finance_insert_longreads(self, materials, insert=False):
        """
        Модификации для ленты "Бизнес и финансы"

        Три последних лонгрида стоят в ленте на фиксированных местах, вне зависимости
        от даты их публикации. Поэтому их нужно вырезать из основного потока ленты и вставить
        в первую страницу.
        """
        longreads = self._finance_last_longreads(3)
        longread_ids = [x.id for x in longreads]
        # исключим из основной ленты
        materials = [m for m in materials if m.id not in longread_ids]

        # и вставим отдельно
        if insert and len(longreads) == 3:
            materials.insert(7, longreads[2])
            materials.insert(5, longreads[1])
            materials.insert(2, longreads[0])

        return materials

    def _finance_last_longreads(self, count=3):
        """
        Возвращает последние статьи из рубрики "бизнес и финансы"
        """
        longreads = self._get_queryset()
        news_cts = self._news_ct_ids
        longreads = longreads.filter(is_advertising=False).exclude(content_type_id__in=news_cts)
        longreads = self._filter_category(longreads, 'finance')
        longreads = longreads[:count]
        longreads = self._concretize(longreads)

        return longreads

    def _slice_page(self, queryset, page_number, limit):
        """
        Подготовить материалы для постраничного вывода.

        :param queryset: объект запроса
        :param int limit: количетсво материалов на странице
        :param int page_number: номер страницы
        :return: набор материалов для конкретной страницы
        """

        number = page_number - 1

        start = max(number * limit, 0)
        end = start + limit

        queryset = queryset[start:end]

        return queryset

    def _generate_cache_key(self, identity):
        """
        Генерация постфикса ключа для кэша. Полный ключ формируется в функции сохранения/загрузки из кэша.

        :param str identity: индентификатор для ключа кэша

        Ключ формируется на основе параметра identity и значения поля "показывать скрытые".
        Примеры получаемых в итоге ключей:
            ribbon  - лента главной новостей
            ribbon.show_hidden - лента главной новостей со скрытыми материалами
            important - блок главное/важное
            important.show_hidden - блок главное/важное со скрытыми материалами
            ribbon_nice - лента категории "Добрые"
            ribbon_crime.show_hidden - лента категории "Происшествия" со скрытыми материалами
        """

        chunks = [identity, 'show_hidden' if self._show_hidden else '']

        return '.'.join([str(chunk) for chunk in chunks if chunk])

    def _concretize(self, queryset):
        """Получить фактические материалы из базовых"""

        return [material.cast() for material in queryset]


def image_parts_template(full_path):
    """ Формирование имени шаблона для частей порезаной картинки"""

    file_path, ext = os.path.splitext(full_path)
    return '{0}_part%s{1}'.format(file_path, ext)


def get_image_parts(full_path):
    """ Получает список частей разрезанной картинки. Возвращает текущую картинку при отсутствии частей"""

    template = image_parts_template(full_path)
    i = 0
    parts = []
    while True:
        part_path = template % i
        i += 1
        if os.path.isfile(part_path):
            im = Image.open(part_path)
            parts.append({'full_path': part_path,
                          'url': '%s%s' % (settings.MEDIA_URL, part_path.replace(settings.MEDIA_ROOT, '')),
                          'width': im.size[0],
                          'height': im.size[1]})
        else:
            break
    if not parts:
        im = Image.open(full_path)
        parts.append(
            {'full_path': full_path,
             'url': '%s%s' % (settings.MEDIA_URL, full_path.replace(settings.MEDIA_ROOT, '')),
             'width': im.size[0],
             'height': im.size[1]})
    return parts


def split_big_image(full_path):
    """ При высоте инфографики более 3000px разрезка ее на части """

    im = Image.open(full_path)
    width = im.size[0]
    high = im.size[1]
    parts_count = int(ceil(high / float(3000)))
    part_high = int(ceil(high / float(parts_count)))
    cur_y = 0
    next_y = 0
    i = 0
    template = image_parts_template(full_path)
    while high > cur_y:
        next_y += part_high
        if next_y > high:
            next_y = high
        im_crop = im.crop((0, cur_y, width, next_y))
        cur_y = next_y
        im_crop.save(template % i, quality=90)
        i += 1


class SimilarMaterialHelper(object):
    """
    Хелпер для получения похожих материалов.
    Похожесть материалов определяется следующим образом (по убыванию приоритета):
        1) Сюжет
        2) Связка с помощью тегов
        3) Спецпроект (если есть)
        4) Рубрика (категория)
        5) Раздел

    Выбираются материалы за последние 4 месяца.
    """

    # максимальный возраст материала в днях.
    MAX_MATERIAL_AGE = 4 * 30

    def __init__(self, material, show_hidden=False, longreads_limit=3):
        self._material = material
        self._project = getattr(self._material, 'project', None)
        self._show_hidden = show_hidden
        self._longreads_limit = longreads_limit
        self._similar_longreads = []

    def get_similar_longreads(self):
        """
        Получить похожие лонгриды.
        """

        # Лонгриды по сюжету
        if self._material.subject:
            self._add_similars(self._get_longreads(subject=self._material.subject), 'subject')

            if self._longreads_are_ready():
                return self._return_longreads()

        # Лонгриды по тегам
        if self._material.tags.exists():
            self._add_similars(self._get_similars_by_tags(), 'tags')

            if self._longreads_are_ready():
                return self._return_longreads()

        # Если материал из спецпроекта, то ищем похожие в спецпроекте.
        if self._project:
            self._add_similars(self._get_similars_by_project(), 'project')

            if self._longreads_are_ready():
                return self._return_longreads()

        # Лонгриды по рубрике (категории). Подбираются только для материалов раздела новости.
        if self._material.category and self._material.source_site.slugs == 'news':
            self._add_similars(self._get_longreads(category=self._material.category), 'category')

            if self._longreads_are_ready():
                return self._return_longreads()

        # Лонгриды по разделу.
        # При выборе по разделу возраст материалов не учитывается
        if self._material.source_site:
            self._add_similars(
                self._get_longreads(max_age=False, source_site=self._material.source_site), 'source_site'
            )

        # NOTE: считаем, что лонгриды по разделу всегда есть, и итоговый список к этому моменту будет сформирован.
        return self._return_longreads()

    def set_longreads_limit(self, limit):
        """
        Установить количество возращаемых лонгридов
        :param int limit: числов возвращаемых материалов
        """

        self._longreads_limit = int(limit)

    def _longreads_are_ready(self):
        return len(self._similar_longreads) >= self._longreads_limit

    def _get_longreads(self, max_age=True, **filtering):
        """
        Получить лонгриды

        :param bool max_age: ограничение по возрасту материала
        :param filtering: параметры фильтрации
        :return: список материалов
        """
        from irk.news.models import BaseMaterial

        queryset = BaseMaterial.longread_objects \
            .filter(**filtering) \
            .exclude(pk=self._material.pk) \
            .order_by('-stamp', '-published_time') \
            .defer('content', 'caption')

        if not self._show_hidden:
            queryset = queryset.filter(is_hidden=False)

        if max_age:
            queryset = queryset.filter(stamp__gte=self.start_date)

        return queryset[:self._longreads_limit]

    def _get_similars_by_project(self):
        """Получить похожие материалы по спецпроекту"""

        similars = []
        qs = self._project.news_materials
        if not self._show_hidden:
            qs = qs.filter(is_hidden=False)
        qs = qs \
            .filter(stamp__gte=self.start_date) \
            .exclude(pk=self._material.pk) \
            .order_by('-stamp', '-published_time')
        similars.extend(qs[:self._longreads_limit])

        return sorted(similars, key=lambda x: x.stamp, reverse=True)[:self._longreads_limit]

    def _get_similars_by_tags(self):
        """Получить похожие материалы по тегам"""

        from irk.news.models import News

        non_longread_type = News
        similars = [
            similar for similar in self._material.tags.similar_objects() if not isinstance(similar, non_longread_type)
        ]
        if not self._show_hidden:
            similars = filter(lambda x: not x.is_hidden, similars)

        similars = filter(lambda x: x.get_sorting_key() >= self.start_date, similars)

        return similars

    def _add_similars(self, materials, way):
        """
        Добавить похожие материалы.
        Материалам добавляется поле way, в котором хранится способ, с помощью которого они были найдены.

        :param materials: список материалов
        :param str way: текстовая метка, обозначающая способ
        """

        for material in materials:
            specific_material = material.cast() or material
            specific_material.way = way
            if specific_material not in self._similar_longreads:
                self._similar_longreads.append(specific_material)

    def _return_longreads(self):
        """Вернуть лонгриды"""

        return self._prepare_results(self._similar_longreads, self._longreads_limit)

    def _prepare_results(self, materials, limit, sorting=False):
        """
        Подготовить результы к выводу.

        :param list materials: список похожих материалов
        :param int limit: количество выводимых материалов
        :param bool sorting: сортировка материалов. По умолчанию выключена.
        """

        if sorting:
            materials.sort(key=lambda x: x.get_sorting_key(), reverse=True)

        return materials[:limit]

    @cached_property
    def start_date(self):
        """Дата, начиная с которой материал считается свежим"""

        return datetime.datetime.now() - datetime.timedelta(days=self.MAX_MATERIAL_AGE)


class NewsletterController(object):
    """Контроллер новостных рассылок"""

    def __init__(self, newsletter):
        self._newsletter = newsletter

    def distribute(self):
        """Разослать подписчикам"""

        from irk.news.models import Subscriber

        if not self._newsletter.has_materials() or self._newsletter.is_sent():
            return

        materials = self.get_materials()

        subscribers = Subscriber.objects.filter(is_active=True)
        sent_count = 0
        for subscriber in subscribers:
            try:
                tpl_notify(
                    u'Рассылка новостей IRK.ru', 'news/notif/distribution.html',
                    {'subscriber': subscriber, 'materials': grouper(materials, 2), 'newsletter': self._newsletter},
                    None,
                    [subscriber.email, ],
                    sender='Твой Иркутск <newsletter@irk.ru>',
                )
                sent_count += 1
            except smtplib.SMTPException:
                raven_capture()
                continue

        self._newsletter.update_status(sent_count)

    def get_materials(self):
        """Получить материалы для рассылки"""

        materials = self._newsletter.materials.select_subclasses()
        materials = self.prepare(materials)

        return materials

    def prepare(self, materials):
        """Подготовить материалы для отображения в рассылке"""

        from irk.experts.models import Expert
        from irk.news.models import News, Article, Photo, Video, Infographic

        result = []

        for material in materials:
            item = {
                'title': material.title,
                'url': material.get_absolute_url(),
            }

            if isinstance(material, News):
                self.prepare_news(material, item)
            elif isinstance(material, Article):
                self.prepare_article(material, item)
            elif isinstance(material, (Photo, Video, Infographic, Expert)):
                self.prepare_media(material, item)
            else:
                item.update({
                    'image': material.standard_image,
                })
                self.prepare_date(material, item)

            result.append(item)

        return result

    def prepare_news(self, material, item):
        """Подготовить данные для новости"""

        if material.standard_image:
            item.update({
                'image': material.standard_image,
            })
        else:
            item.update({
                'label': material.category.title if material.category else None,
                'caption': material.caption,
            })
        self.prepare_date(material, item)

    def prepare_article(self, material, item):
        """Подготовить данные для статьи"""

        image = material.standard_image
        if image:
            item.update({
                'image': image,
            })

        if material.source_site.slugs == 'news':
            self.prepare_date(material, item)
        else:
            item.update({
                'label': material.source_site.name,
                'caption': material.caption,
            })

    def prepare_media(self, material, item):
        """Подготовить данные для медиа материала (фотореп, видео, инфогрмафика, эксперт)"""

        image = material.standard_image
        if image:
            item.update({
                'image': image,
            })

        opts = material._meta

        item.update({
            'label': opts.verbose_name,
            'caption': material.caption,
        })

    def prepare_date(self, material, item):
        """Подготовить информацию о дате"""

        item.update({
            'stamp': material.stamp,
            'published_time': material.published_time,
        })
