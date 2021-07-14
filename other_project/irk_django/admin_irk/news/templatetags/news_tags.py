# -*- coding: utf-8 -*-

import calendar
import logging
import datetime
import re

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.db.models.query import QuerySet
from django.template import Node
from django.template.loader import render_to_string
from django.utils.html import mark_safe

from irk.contests.models import Contest
from irk.currency.models import CurrencyCbrf
from irk.experts.models import Expert
from irk.news import settings as app_settings
from irk.news.helpers import SimilarMaterialHelper
from irk.news.helpers import twitter_images as twitter_images_helper
from irk.news.models import (Article, BaseMaterial, Block, Flash, Infographic, Live, News, Photo,
                             Subject, Subscriber, Video)
from irk.news.permissions import is_moderator
from irk.news.urlresolvers import get_index_url
from irk.options.models import Site
from irk.polls.models import Poll
from irk.testing.models import Test
from irk.utils.cache import TagCache
from irk.utils.decorators import deprecated
from irk.utils.helpers import get_object_or_none
from irk.utils.templatetags import parse_arguments

register = template.Library()

DAY_START_TIME = datetime.time(0, 0, 0)
DAY_END_TIME = datetime.time(0, 0, 0)

log = logging.getLogger(__name__)


class TwitterImagesNode(template.Node):

    def __init__(self, text, variable):
        self.text = text
        self.variable = variable

    def render(self, context):
        text = template.Variable(self.text).resolve(context)
        context[self.variable] = twitter_images_helper(text)

        return ''


@register.tag
def twitter_images(parser, token):
    """Выбираем из текста все URL, если это ссылка на изображение сервиса
    публикации изображений, возвращаем список превьюшек

    {% twitter_images tweet.text as images %}"""

    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError(u'Tag `%s` receive 3 arguments' % bits[0])

    return TwitterImagesNode(bits[1], bits[3])


@register.inclusion_tag('news/snippets/entry_cool.html', takes_context=True)
def render_news_cool(context, news, related=None, show_date=False, **kwargs):
    """Рендер новости с фотогалереей и ссылками по теме (less-версия)"""

    ct = ContentType.objects.get_for_model(news)
    cache_key = '.'.join([str(x) for x in [ct.app_label, ct.model, news.id]])

    # Не показывать форму для подписки на рассылку тем, кто уже подписан
    if context['user'].is_authenticated:
        is_user_subscribed = Subscriber.objects.filter(email=context['user'].email, is_active=True).exists()
    else:
        is_user_subscribed = False

    # Не показывать тормозной баннер в онлайн-трансляциях
    try:
        is_live = news.live_set.exists()
    except AttributeError:
        is_live = False

    template_context = {
        'today': datetime.date.today(),
        'request': context['request'],
        'object': news,
        'type': ct.model,
        'related': related,
        'show_date': bool(show_date),
        'cache_key': cache_key,
        'previous_news': context.get('previous_news'),
        'continuation_news': context.get('continuation_news'),
        'is_user_subscribed': is_user_subscribed,
        'is_live': is_live,
    }

    template_context.update(kwargs)

    return template_context


@register.inclusion_tag('news-less/tags/sidebar-flash.html', takes_context=True)
def news_flash(context, amount=3):
    """Блок народных новостей в сайдбаре"""

    queryset = Flash.objects.filter(visible=True).order_by('-created')

    # В категории Транспорт выводим народные новости про дтп
    category_slug = context.get('category_slug')
    if category_slug == 'transport':
        queryset = queryset.filter(type=Flash.VK_DTP)

    return {'objects': queryset[:amount]}


@register.inclusion_tag('news/blogs/includes/author.html')
def blog_author(author):
    """Блок с информацией об авторе блога"""
    # TODO: перенести в blog_tags

    return {
        'author': author,
    }


@register.inclusion_tag('news/snippets/live.html')
def related_live_news(entry):
    """Связанная live трансляция

    Параметры::
        entry - объект модели `news.models.News'
    """

    if not entry or not isinstance(entry, News):
        return {}

    try:
        live = Live.objects.filter(news=entry)[0]
    except IndexError:
        return {}

    if live.is_finished:
        order = ('date', 'created')
    else:
        order = ('-date', '-created')

    return {
        'news': entry,
        'live': live,
        'entries': live.entries.all().order_by(*order),
    }


class SidebarBlockNode(template.Node):
    # Заголовки блока в зависимости от типа контента
    headings = {
        'news': u'Новости',
        'article': u'Статьи',
        'photo': u'Фоторепортажи',
        'video': u'Видео',
        'infographic': u'Наглядно',
    }

    # Маппинг названий моделей
    models = {
        'news': News,
        'article': Article,
        'photo': Photo,
        'video': Video,
        'infographic': Infographic,
    }

    # Дополнительные фильтры для каждой модели
    model_filters = {
        'news': {'is_payed': False},
    }

    def __init__(self, model, limit, **kwargs):
        self.model = model
        self.limit = limit
        self.exclude = kwargs.pop('exclude', None)
        self.template = kwargs.pop('template', None)
        self.image_size = kwargs.pop('image_size', None)
        self.title = kwargs.pop('title', None)

    def render(self, context):
        request = context['request']

        model_name = self.model.resolve(context)
        model = self.models[model_name]
        limit = self.limit.resolve(context) if self.limit else 3
        moderator = is_moderator(request.user)

        exclude = None
        if self.exclude is not None:
            exclude = self.exclude.resolve(context)

        if self.image_size is not None:
            image_size = self.image_size.resolve(context)
        else:
            image_size = '140x120'

        cache_key = 'news.tags.sidebar_block.%s' % '.'.join([
            str(request.csite.id),
            model_name,
            str(limit),
            str(exclude.id) if exclude else '',
            str(int(moderator)),
            image_size,
        ])

        with TagCache(cache_key, 86400, tags=(model_name,)) as cache:
            value = cache.value
            if value is cache.EMPTY:

                queryset = model.objects.for_site(request.csite.site) \
                    .order_by('-stamp', '-pk').prefetch_related('source_site')
                if not moderator:
                    queryset = queryset.filter(is_hidden=False)

                if model_name in self.model_filters:
                    queryset = queryset.filter(**self.model_filters[model_name])

                if isinstance(exclude, models.Model):
                    queryset = queryset.exclude(pk=exclude.pk)
                elif isinstance(exclude, (list, tuple, QuerySet)):
                    raise NotImplementedError()
                    # queryset = queryset.exclude(pk__in=exclude)

                if issubclass(model, Article):
                    queryset = queryset.select_related('type')

                if issubclass(model, Video):
                    queryset = queryset.exclude(stamp__lt=datetime.date.today() - datetime.timedelta(7))

                queryset = queryset[:limit]

                if not request.csite.slugs:
                    raise ImproperlyConfigured(u'У раздела %s нет алиаса' % request.csite.name)

                objects = []
                for obj in queryset:
                    obj.title_url = get_index_url(obj.source_site, obj)
                    objects.append(obj)

                template_context = {
                    'objects': objects,
                    'title': self.title.resolve(context) if self.title else self.headings[model_name],
                    'image_size': image_size,
                    'show_header': request.csite.slugs != 'news',
                }

                templates = (
                    '%s/tags/%s-block.html' % (request.csite.slugs, model_name),
                    'news-less/tags/%s-block.html' % model_name,
                    'news-less/tags/sidebar-block.html',
                )

                value = render_to_string(templates, template_context)
                cache.value = value

            return value


@register.tag
def news_sidebar_block(parser, token):
    """Блок материалов в сайдбаре

    Параметры::
        model: тип выводимых материалов, см. наследники от модели `news.models.BaseMaterial'
        limit: количество выводимых объектов
        size: размер изображения

    Примеры использования::

        {% news_sidebar_block 'news' %}
        {% news_sidebar_block 'foto' limit=2 %}
        {% news_sidebar_block 'article' limit=5 %}
        {% news_sidebar_block 'foto' image_size='140x140' %}
    """

    args, kwargs = parse_arguments(parser, token.split_contents()[1:])

    model = args[0]

    try:
        limit = args[1]
    except IndexError:
        limit = kwargs.pop('limit', None)

    return SidebarBlockNode(model, limit, **kwargs)


RUBRICATOR_URLS = [
    (reverse_lazy('news:index'), u'Лента'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'crime'}), u'Происшествия'),
    # (reverse_lazy('news.podcast.index'), u'Подкасты'),
    (reverse_lazy('news:article:index'), u'Статьи'),
    (reverse_lazy('news:flash:index'), u'Народные'),
    (reverse_lazy('news:photo:index'), u'Фото'),
    (reverse_lazy('news:experts:index'), u'Эксперт'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'finance'}), u'Финансы'),
    # Подпункты раздела "Еще"
    (reverse_lazy('news:news_type', kwargs={'slug': 'transport'}), u'Транспорт'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'ecology'}), u'Экология'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'sport'}), u'Спорт'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'culture'}), u'Культура'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'society'}), u'Общество'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'politics'}), u'Власть'),
    (reverse_lazy('news:news_type', kwargs={'slug': 'video'}), u'Видео'),
    (reverse_lazy('news:blogs:index'), u'Блоги'),
    (reverse_lazy('news:infographic:index'), u'Наглядно'),
]


# TODO: найти все места использования шаблонного тега и провести рефакторинг
@register.inclusion_tag('news-less/tags/news-top-rubrics.html', takes_context=True)
def news_rubricator(context, obj=None):
    """Рубрикатор между типами публикаций в центральной колонке"""

    # Если есть объект и у него задана категория, то выделяем пункт соответствующий категории
    if obj and getattr(obj, 'category', None):
        path = obj.category.get_absolute_url()
    # Иначе определяем выбранный пункт по текущему url
    else:
        request = context['request']
        path = request.get_full_path()

    rubrics = []
    marked_idx = None
    for idx, (url, title) in enumerate(RUBRICATOR_URLS):
        # Если есть объект, пункт не может быть текущим
        is_current = (path == url) if not obj else False
        # Подсвечиваем пункт меню
        show_marker = path.startswith(str(url)) if idx != 0 else is_current

        if show_marker:
            marked_idx = idx
        rubrics.append([url, title, is_current, show_marker])

    # Индекс позиции куда подставляется текущая рубрика, если она больше этого значения.
    # Сейчас соответствует индексу рубрики "Эксперт"
    custom_idx = 6
    if marked_idx > custom_idx:
        rubrics[custom_idx], rubrics[marked_idx] = rubrics[marked_idx], rubrics[custom_idx]

    return {
        'rubrics': rubrics,
    }


@register.inclusion_tag('news-less/tags/calendar-block.html')
def news_calendar(date=None, highlight=None, highlight_is_link=False):
    """Блок с календарем новостей

    Параметры:
        date: дата, которая будет показана на календаре
        highlight: дата, которая будет подсвечена
    """

    if date is None:
        date = datetime.date.today()

    if highlight is None:
        try:
            highlight = News.objects.filter(is_hidden=False).order_by('-stamp').values_list('stamp', flat=True)[0]
        except IndexError:
            highlight = None

    archive_url = reverse_lazy('news:news:date', args=u'{:%Y %m %d}'.format(date).split()) if date else ''

    return {
        'date': date,
        'archive_url': archive_url,
        'today': datetime.date.today(),
        'highlight': highlight,
        'link': bool(highlight_is_link),
    }


class SiteRelatedLastNewsEntry(template.Node):
    """Последние статьи/фоторепортажи, привязанные к определенному разделу сайта"""

    def __init__(self, amount, sub_type, variable):
        self.amount = amount
        self.sub_type = sub_type
        self.variable = variable

    def render(self, context):
        request = context['request']
        model = SidebarBlockNode.models[self.sub_type]

        try:
            news = News.objects.filter(sites=request.csite.site, is_payed=False,
                                       is_hidden=False).order_by('-stamp', '-pk').select_related('source_site')
            news = news[:self.amount]
            if self.amount == 1:
                news = news[0]
                news.source_site = Site.objects.get_by_pk(news.source_site_id)
                context[self.variable] = news
            else:
                for entry in news:
                    entry.source_site = Site.objects.get_by_pk(entry.source_site_id)
                context[self.variable] = news
        except IndexError:
            context[self.variable] = None
        return ''


@register.inclusion_tag('news-less/tags/news-bunch.html')
def news_bunch(instance=None):
    """ Если у новость связана с другими то:
        для первой из связанных новостей возвращает предыдущую
        для остальных возвращает первую"""

    if not isinstance(instance, News):
        return None

    def get_later_news(result_news):
        """ Получить из связки новости, новее текущей"""
        current_news = result_news[-1:][0]
        try:
            master_bunch = current_news.news_bunch.all()[0]
        except IndexError:
            master_bunch = None

        if master_bunch:
            result_news.append(master_bunch)
            return get_later_news(result_news)
        else:
            return result_news[1:]

    def get_older_news(result_news):
        """ Получить из связки новости, старее текущей"""
        current_news = result_news[-1:][0]

        if current_news.bunch:
            result_news.append(current_news.bunch)
            return get_older_news(result_news)
        else:
            return result_news[1:][::-1]

    bunch = get_older_news([instance, ]) + [instance, ] + get_later_news([instance, ])

    bunch = [x for x in bunch if not x.is_hidden or x == instance]

    # Выбор нужной новости
    if len(bunch) > 1:
        if bunch[-1] == instance:
            type_ = 'prev'
            news = bunch[-2]
        else:
            type_ = 'next'
            news = bunch[-1]
    else:
        news = None
        type_ = None

    return {
        'type': type_,
        'bunch': news,
    }


@register.simple_tag(takes_context=True)
def news_extra_materials(context, **kwargs):
    """Блок материлов: «5 историй, которые нельзя пропустить»"""

    # По умолчанию отображается первая страница с объектами. Остальные подгружаются через ajax.

    request = context.get('request')
    if not request:
        return {}

    block = get_object_or_none(Block, slug='news_five_stories', )
    if not block:
        return {}

    params = []
    for key, value in kwargs.iteritems():
        params.append('{}={}'.format(key, value))

    cache_key = '.'.join(['news_five_stories', str(request.csite.id)] + params)

    with TagCache(cache_key, 3600, tags=('block',)) as cache:
        value = cache.value
        if value is cache.EMPTY:
            materials = []
            for position in block.positions.all():
                if not position.material:
                    continue
                materials.append(position.material.cast())

            context = {
                'materials': materials,
                'block': block,
                'request': request,
            }
            context.update(kwargs)

            value = render_to_string('news-less/tags/news_extra_materials.html', context)
            cache.value = value

        return value


@register.inclusion_tag('news-less/tags/news-hot-discussion.html')
def hot_discussion(current_object=None, limit=3, **kwargs):
    """
    Блок «Горячие обсуждения»

    Список самых обсуждаемых материалов за последние 3 дня.
    Пока решили искать только по Новостям.
    """

    end_day = datetime.date.today()
    start_day = end_day - datetime.timedelta(days=2)

    materials = BaseMaterial.material_objects.filter(stamp__range=[start_day, end_day],
                                                     disable_comments=False).order_by(
        '-comments_cnt').select_subclasses()
    if current_object:
        materials = materials.exclude(pk=current_object.pk)

    result = {
        'materials': materials[:limit]
    }
    result.update(kwargs)
    return result


@register.simple_tag
def similar_materials(material, limit=3):
    """
    Похожие материалы

    :param news.models.BaseMaterial material: исходный материал, для которого ищутся связанные.
    :param int limit: количество похожих материалов
    """

    smh = SimilarMaterialHelper(material)
    smh.set_longreads_limit(limit)
    try:
        similar_longreads = smh.get_similar_longreads()
    except AttributeError:
        # часто внутри что-то не так работает из-за контент-тайпов удаленных
        # разделов или еще не созданных из другой ветки
        log.exception('Can not get similar materials')
        return []

    return similar_longreads


@register.inclusion_tag('news-less/tags/news-last-news.html', takes_context=True)
def last_news(context, exclude=None, limit=4):
    """
    Блок «Последние новости».

    :param dict context: контекст шаблона
    :param exclude: новости которые нужно исключить из списка
    :type exclude: News or None
    :param int limit: количество отображаемых новостей
    """

    # Выбираем новости за 4 последних дня, чтобы оптимизировать SQL запрос
    boundary_date = datetime.date.today() - datetime.timedelta(days=3)

    news_list = News.objects.filter(is_hidden=False, stamp__gte=boundary_date)\
        .order_by('-stamp', '-published_time').defer('content', 'caption')

    if exclude:
        news_list = news_list.exclude(pk=exclude.pk)

    return {
        'news_list': news_list[:limit]
    }


@register.filter
def time_to_read(value):
    """
    Расчитывает среднее время на чтение в минутах.
    Минимальное время чтения 1 минута.
    """

    minutes = int(round(len(value) / float(app_settings.AVERAGE_READ_SPEED)))

    return max(1, minutes)


@register.tag
def material_card(parser, token):
    """
    Карточка материала

    Параметры:
        material - материал, наследник news.BaseMaterial
        is_double - супер карточка материала
        is_home - карточка материала для главной страницы
        metrika_goal - цель для Яндекс.Метрики
        is_lazyload - ленивая загрузка изображений
        is_orange - оранжевое оформление

        другие именнованные параметры просто передаются в шаблон

    """

    bits = token.split_contents()
    args, kwargs = parse_arguments(parser, bits[1:])

    return MaterialCardNode(*args, **kwargs)


class MaterialCardNode(template.Node):
    """Нода для карточки материала"""

    def __init__(self, material, **kwargs):
        self._material = material
        self._kwargs = kwargs

    def render(self, context):
        material = self._material.resolve(context)
        if not material:
            return ''

        kwargs = {key: value.resolve(context) for key, value in self._kwargs.items()}

        label_text, label_class = self._get_label(material)
        is_big_image = kwargs.get('is_big_image')

        material_image = material.wide_image if not is_big_image else material.standard_image
        if not material_image:
            material_image = material.standard_image

        image_size, image_size_gadget = self._get_image_sizes(is_big_image)

        template_context = {
            'material': material,
            'material_url': material.get_absolute_url(),
            'material_image': material_image,
            'label_text': label_text,
            'label_class': label_class,
            'is_expert': isinstance(material, Expert),
            'is_video': isinstance(material, Video),
            'is_photo': isinstance(material, Photo),
            'is_contest': isinstance(material, Contest),
            'is_test': isinstance(material, Test),
            'image_size': image_size,
            'image_size_gadget': image_size_gadget,
            'request': context.get('request'),
        }
        template_context.update(kwargs)

        if kwargs.get('is_double') and kwargs.get('is_light'):
            return render_to_string('news-less/tags/material_card/double_light.html', template_context)

        if kwargs.get('is_double'):
            return render_to_string('news-less/tags/material_card/double.html', template_context)

        if kwargs.get('is_mobile'):
            return render_to_string('news-less/tags/material_card/mobile.html', template_context)

        if kwargs.get('is_light'):
            return render_to_string('news-less/tags/material_card/light.html', template_context)

        if kwargs.get('is_big'):
            return render_to_string('news-less/tags/material_card/big.html', template_context)

        return render_to_string('news-less/tags/material_card/simple.html', template_context)

    def _get_label(self, material):
        """Получить метку и ее css-класс для карточки"""

        if isinstance(material, Photo):
            pictures = material.gallery.main_gallery_pictures()
            label_text = u'{} фото'.format(pictures.count()) if pictures else u''
            label_class = 'photos'
        elif isinstance(material, Poll):
            label_text = u'Голосование'
            label_class = 'poll'
        elif isinstance(material, Expert):
            label_text = u'эксперт'
            label_class = 'expert'
        elif isinstance(material, Contest):
            label_text = u'конкурс'
            label_class = 'contests'
        elif isinstance(material, Test):
            if material.is_survey():
                label_text = u'опрос'
            else:
                label_text = u'тест'
            label_class = 'test'
        else:
            label_text, label_class = None, None

        return label_text, label_class

    def _get_image_sizes(self, is_big_image):
        """Получить размеры картинок"""

        if is_big_image:
            return '300x210', '340x260'

        return '300x200', '340x200'


@register.inclusion_tag('news-less/tags/currency_calculator.html', takes_context=True)
def currency_calculator(context):
    date = CurrencyCbrf.objects.all().order_by('-stamp').values_list('stamp', flat=True).first()
    if not date:
        return {}
    rates = CurrencyCbrf.objects.filter(stamp__in=(date, date - datetime.timedelta(days=1))).order_by('stamp')
    if len(rates) == 2:
        context['today'] = rates[1]
        context['yesterday'] = rates[0]
        context['difference'] = {
            'usd': rates[1].usd - rates[0].usd,
            'euro': rates[1].euro - rates[0].euro,
            'cny': rates[1].cny - rates[0].cny,
        }
    else:
        context['today'] = rates[0]
        context['yesterday'] = None
        context['difference'] = {}

    return context


@register.simple_tag
def cards_menu(content):
    """Меню карточек материалов"""

    result = ''

    if '[cards' in content:

        cards_re = re.compile(ur'\[cards\s(\d+)\](.*?)\[/cards\]', re.S)
        title_re = re.compile(ur'\[h2\](.*?)\[/h2\]')

        card_matches = cards_re.findall(content)

        cards = []

        for card in card_matches:
            match = title_re.search(card[1])
            title = match.groups()[0] if match else ''
            cards.append({'number': card[0], 'title': title})

        result = render_to_string('news-less/tags/cards-menu.html', {'cards': cards})

    return result


@register.simple_tag
def tilda_scripts(article):
    return mark_safe(article.prepare_scripts())


@register.simple_tag
def tilda_styles(article):
    return mark_safe(article.prepare_styles())


@register.simple_tag
def tilda_content(article):
    return mark_safe(article.prepare_content())


class TildaContentNode(Node):
    def __init__(self, nodelist, tilda_root):
        self.nodelist = nodelist
        self.tilda_root = tilda_root

    def render(self, context):
        content = self.nodelist.render(context)
        tilda_root = self.tilda_root

        result = content.replace('="images/', '="{}images/'.format(tilda_root))
        result = result.replace("='images/", "='{}images/".format(tilda_root))
        result = result.replace("url('images/", "url('{}images/".format(tilda_root))
        result = result.replace('url("images/', 'url("{}images/'.format(tilda_root))

        return result

@register.tag('tildacontent')
def do_tildacontent(parser, token):
    """
    Пример использования:
    {% tildacontent base='%media%/site/special/buildingtime/' %}<img src="images/xx.jpg">{% endtildacontent %}

    Если папка images лежит в buildingtime, то тег заменит адрес изображения на правильный URL.
    """

    bits = token.split_contents()
    _, val = bits[1].split('=')
    tilda_url = val.strip("'")

    # можно указать %static% и %media%
    tilda_url = tilda_url.replace(r'%static%/', settings.STATIC_URL)
    tilda_url = tilda_url.replace(r'%media%/', settings.MEDIA_URL)

    nodelist = parser.parse(('endtildacontent',))
    parser.delete_first_token()
    return TildaContentNode(nodelist, tilda_url)

