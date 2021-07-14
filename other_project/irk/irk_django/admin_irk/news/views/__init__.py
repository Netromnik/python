# -*- coding: utf-8 -*-

import calendar
import datetime
import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.db.models import F
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import View
from pytils.dt import ru_strftime

from irk.adwords.models import AdWord, CompanyNews
from irk.map.models import Cities as City
from irk.news.feeds import NewsFeed, YandexFeed
from irk.news.forms import SubscriptionAnonymousForm
from irk.news.helpers import MaterialController, NewsletterController, news_date_url
from irk.news.models import (
    Article, BaseMaterial, Block, Category, DailyNewsletter, Infographic, News, Photo, Subscriber,
    UrgentNews, Video, WeeklyNewsletter
)
from irk.news.permissions import is_moderator
from irk.news.search import BaseMaterialSearch
from irk.news.views.base import SectionNewsBaseView
from irk.news.views.base.date import NewsDateBaseView
from irk.news.views.base.list import NewsListBaseView
from irk.news.views.base.read import NewsReadBaseView
from irk.options.models import Site
from irk.utils.cache import TagCache
from irk.utils.decorators import nginx_cached
from irk.utils.helpers import get_object_or_none, grouper, int_or_none
from irk.utils.http import ajax_request, json_response
from irk.utils.notifications import tpl_notify
from irk.utils.search import ElasticSearchQuerySet

logger = logging.getLogger(__name__)


@nginx_cached(60 * 5)
def last_news(request):
    """Виджет с последней новостью"""

    city = City.objects.get(alias='irkutsk')
    news_site = Site.objects.get(slugs='news')

    news_list = News.objects.filter(city=city, stamp__gte=datetime.date.today()-datetime.timedelta(days=21),
        sites=news_site, is_payed=False, is_hidden=False).order_by('-stamp', '-pk')[:3]

    context = {
        'news_list': news_list,
        'city': city,
    }

    return render(request, 'yandex/last_news.html', context)


class IndexView(View):
    """Главная страница новостей (Лента)"""

    template = 'news-less/index.html'
    ajax_template = 'news-less/ajax_material_list.html'

    def get(self, request, *args, **kwargs):
        self._initialize()
        self.request = request

        if request.is_ajax():
            return self._render_ajax_response()

        context = self.get_context_data()

        return render(request, self.template, context)

    def _initialize(self):
        """Инициализация и установка необходимых параметров."""

        # Показывать скрытые материалы.
        self.show_hidden = is_moderator(self.request.user)
        self.date = datetime.date.today()

        self.material_controller = MaterialController(show_hidden=self.show_hidden)
        self.page = int_or_none(self.request.GET.get('page')) or 1

    @json_response
    def _render_ajax_response(self):
        """Подгрузка материалов через Ajax"""

        materials = self._get_ribbon_materials()
        context = {
            'ribbon_materials': materials,
            'last_material_date': self.request.GET.get('last_material_date'),
        }

        response = {
            'html': render_to_string(self.ajax_template, context),
            'last_material_date': '{:%Y-%m-%d}'.format(materials[-1].stamp) if len(materials) else '',
        }

        if isinstance(self, ArchiveView):
            # добавить в ответ данные для пейджинации по дате
            response.update(self._get_dates())

        return response

    def get_context_data(self):
        """Получить контекст для ответа"""

        context = {
            'ribbon_materials': self._get_ribbon_materials(),
            'is_moderator': self.show_hidden,
            'super_material': self._get_super_material(),
            'important_materials': self._get_important_materials(),
            'sidebar_materials': self._get_sidebar_materials(),
            'urgent_news': self._get_urgent_news(),
            'show_calendar': True,
            'date_pagination': False,
            'mobile_bottom_materials': self._get_mobile_bottom_materials(),
            'today': datetime.date.today(),
        }

        return context

    def _get_ribbon_materials(self):
        """
        Получить материалы для ленты
        """

        materials = self.material_controller.get_ribbon_materials(self.page)

        return materials

    def _get_super_material(self):
        """Получить супер-материал"""

        queryset = BaseMaterial.material_objects.filter(is_super=True)
        if not self.show_hidden:
            queryset = queryset.filter(is_hidden=False)

        material = queryset.first()

        if material and not material.is_specific():
            material = material.content_object

        return material

    def _get_important_materials(self):
        """Получить материалы для блока «Главное/Важное»"""

        materials = self.material_controller.get_important_materials()

        return materials

    def _get_sidebar_materials(self):
        """Получить закрепленные материалы для правой колонки"""

        block = get_object_or_none(Block, slug='news_index_sidebar')
        if not block:
            return []

        materials = []
        for position in block.positions.all():
            if not position.material:
                continue
            if not self.show_hidden and position.material.is_hidden:
                continue
            materials.append(position.material)

        return materials

    def _get_mobile_bottom_materials(self):
        """
        Материалы для блока под лентой в мобилке
        Получаются объединением правой колонки и пяти историй.
        """

        if not self.request.user_agent.is_gadget:
            return []

        materials = []
        blocks = Block.objects.filter(slug__in=['news_index_sidebar', 'news_five_stories'])

        for block in blocks:
            for position in block.positions.all():
                if not position.material:
                    continue
                if not self.show_hidden and position.material.is_hidden:
                    continue
                materials.append(position.material)

        return materials

    def _get_urgent_news(self):
        """Срочная новость"""

        urgent = UrgentNews.objects.filter(is_visible=True).order_by('-id').first()
        return urgent

    def _get_dates(self):
        """
        Получить информацию по датам, на которые есть новости.

        Эта информация добавляется в аяксовые ответы и в шаблон ArchiveView - туда,
        где пейджинация идет по дате, а не по числу записей.

        :return: словарь с датами и url для них
        """

        previous_date = News.objects\
            .filter(stamp__lt=self.date).order_by('-stamp').values_list('stamp', flat=True).first()
        if previous_date:
            previous_date_url = reverse('news:news:date', args=u'{:%Y %m %d}'.format(previous_date).split())
        else:
            previous_date_url = None

        next_date = News.objects.filter(stamp__gt=self.date).order_by('stamp').values_list('stamp', flat=True).first()

        # Исключаем даты из будущего
        if next_date and next_date <= datetime.date.today():
            next_date_url = reverse('news:news:date', args=u'{:%Y %m %d}'.format(next_date).split())
        else:
            next_date = None
            next_date_url = None

        return {
            'date': self.date,
            'today': datetime.date.today(),
            'previous_date': previous_date,
            'previous_date_url': previous_date_url,
            'previous_date_human': ru_strftime(u'%a, %d %B', previous_date),
            'next_date': next_date,
            'next_date_url': next_date_url,
        }


index = IndexView.as_view()


class ArchiveView(IndexView):
    """Архив материалов на конкретную дату"""

    def _initialize(self):
        super(ArchiveView, self)._initialize()

        try:
            self.date = datetime.date(int(self.kwargs['year']), int(self.kwargs['month']), int(self.kwargs['day']))
        except ValueError:
            raise Http404(u'Неверная дата')

    def get_context_data(self):

        context = {
            'ribbon_materials': self._get_ribbon_materials(),
            'important_materials': self._get_important_materials(),
            'is_moderator': is_moderator(self.request.user),
            'sidebar_materials': self._get_sidebar_materials(),
            'show_calendar': True,
            'date_pagination': True,
        }
        context.update(self._get_dates())

        return context

    def _get_ribbon_materials(self, **kwargs):
        """Лента материалов по дате"""

        materials = self.material_controller.get_ribbon_materials_for_date(self.date)

        return materials


archive = ArchiveView.as_view()


class RubricView(IndexView):
    """Материалы конкретной рубрики"""

    def _initialize(self):
        super(RubricView, self)._initialize()

        self.slug = self.kwargs.get('slug')
        if not Category.objects.filter(slug=self.slug).exists():
            raise Http404()

    def get_context_data(self):
        context = super(RubricView, self).get_context_data()

        context['show_calendar'] = False
        context['date_pagination'] = False
        context['category_slug'] = self.slug

        return context

    def _get_ribbon_materials(self, **kwargs):
        """Лента материалов по категории"""

        materials = self.material_controller.get_ribbon_materials_for_category(self.slug, self.page)

        return materials

    def _get_sidebar_materials(self):
        """Получить 4 последних лонгрида для рубрики."""

        materials = self.material_controller.get_last_longrid_materials_for_category(self.slug)

        return materials


news_type = RubricView.as_view()


class NewsReadView(NewsReadBaseView):
    template = 'news-less/news/read.html'

    def extra_context(self, request, obj, extra_params=None):
        context = super(NewsReadView, self).extra_context(request, obj, extra_params)

        previous_news, continuation_news = self._get_related_news(obj)

        context.update({
            'previous_news': previous_news,
            'continuation_news': continuation_news,
        })

        return context

    def _get_related_news(self, obj):
        previous = obj.bunch
        continuation = obj.news_bunch.first()

        # Не отображаем зависимые новости, если они скрыты (модераторов не касается)
        if not self.show_hidden(self.request):
            if previous and previous.is_hidden:
                previous = None
            if continuation and continuation.is_hidden:
                continuation = None

        return previous, continuation


news_read = NewsReadView.as_view()


SEARCH_LABELS = {
    Photo: {'title': u'фоторепортажи', 'slug': 'photo'},
    Video: {'title': u'видео', 'slug': 'video'},
    Article: {'title': u'статьи', 'slug': 'article'},
    Infographic: {'title': u'инфографика', 'slug': 'infographic'},
}


def search(request):
    """Поиск по новостям"""

    query = request.GET.get('q', '').strip()
    type_ = request.GET.get('type', 'news')
    sorting = request.GET.get('sorting', 'relevance')

    if type_ not in ('news', 'blogs'):
        type_ = 'news'

    blogs = ()

    query_body = {
        "size": 100,
        "query": {
            "function_score": {
                "boost_mode": "multiply",

                "query": {
                    "multi_match": {
                        "query": query,
                        "type": "best_fields",
                        "minimum_should_match": "70%",
                        "operator": "and",
                        "fields": ["{}^{}".format(k, v) for k, v in BaseMaterialSearch.boost.items()]
                    }
                },

                "functions": [
                    {
                        "gauss": {
                            "stamp": {
                                "offset": "60d",
                                "scale": "180d",
                                "decay": 0.7
                            }
                        }
                    }
                ],
                "score_mode": "multiply",
            }
        }
    }

    if sorting == 'date':
        query_body['sort'] = [
            {"stamp": {"order": "desc"}}
        ]

    if type_ == 'news':
        queryset = ElasticSearchQuerySet(
            [News, Photo, Article, Video, Infographic]
        ).raw(query_body)
    else:
        raise NotImplementedError()

    paginator = Paginator(queryset, 20)

    try:
        page = request.GET.get('page')
    except (TypeError, ValueError):
        page = 1

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(1)

    for obj in objects.object_list:
        for model, label in SEARCH_LABELS.items():
            if isinstance(obj, model):
                setattr(obj, 'search_label', label)
                break

    context = {
        'objects': objects,
        'blogs': blogs,
        'type': type_,
        'page': page,
        'q': query,
        'today': datetime.date.today(),
        'sorting': sorting,
    }

    if request.is_ajax():
        template = 'news-less/search/snippets/entries.html'
    else:
        template = 'news-less/search.html'

    return render(request, template, context)


def calendar_block(request):
    try:
        date = datetime.datetime.strptime(request.GET.get('date'), '%Y%m%d').date()
    except (TypeError, ValueError):
        date = datetime.date.today()

    try:
        highlight = datetime.datetime.strptime(request.GET.get('highlight'), '%Y%m%d').date()
    except (TypeError, ValueError):
        highlight = object()

    highlight_link = request.GET.get('link') == 'true'

    current_month_first_day = datetime.date.today().replace(day=1)

    first_weekday, days_in_month = calendar.monthrange(date.year, date.month)

    month_first_day = date.replace(day=1)
    month_last_day = date.replace(day=days_in_month)

    cache_key = 'news.calendar.%s.%s.%s' % (month_first_day.isoformat(), str(highlight), str(highlight_link))

    _default_object = object()
    if date < current_month_first_day:
        expires = 86400
    else:
        expires = 600

    value = cache.get(cache_key, _default_object)
    if value is _default_object:

        # Выбираем все даты месяца, за которые есть новости
        dates = list(News.objects.filter(is_hidden=False, is_payed=False,
            stamp__range=(month_first_day, month_last_day)).dates('stamp', 'day'))

        weeks = []
        week = []

        # Дополняем первую неделю спереди пустыми ячейками, чтобы месяц начинался с нужного дня недели
        for i in range(1, first_weekday+1):
            week.append([None, None, None]) # у нас дальше цикл

        # Генерируем таблицу с датами
        for idx in range(1+first_weekday, days_in_month+1+first_weekday):

            offset = idx-first_weekday
            if 1 <= offset <= days_in_month:
                stamp = date.replace(day=offset)
            else:
                stamp = None

            is_exists = stamp in dates
            url = None
            if is_exists:
                url = reverse('news:news:date', args=('%04d' % stamp.year, '%02d' % stamp.month, '%02d' % stamp.day))
            week.append([stamp, is_exists, url])

            if idx % 7 == 0:
                weeks.append(week[:])
                week = []

        weeks.append(week)

        # Выясняем дату для ссылки на предыдущий месяц
        previous_month_last_day = month_first_day - datetime.timedelta(days=1)
        previous_month_first_day = previous_month_last_day.replace(day=1)

        try:
            previous_month = News.objects.filter(is_hidden=False, is_payed=False,
                stamp__range=(previous_month_first_day, previous_month_last_day)).order_by('-stamp').values_list('stamp', flat=True)[0]
            previous_month_url = reverse('news:news:date', args=('%04d' % previous_month.year,
                '%02d' % previous_month.month, '%02d' % previous_month.day))
        except IndexError:
            previous_month = None
            previous_month_url = None

        # Дата для ссылки на следующий месяц
        next_month_first_day = month_last_day + datetime.timedelta(days=1)
        next_month_days = calendar.monthrange(next_month_first_day.year, next_month_first_day.month)[1]
        next_month_last_day = next_month_first_day.replace(day=next_month_days)

        try:
            next_month = News.objects.filter(is_hidden=False, is_payed=False,
                stamp__range=(next_month_first_day, next_month_last_day)).order_by('stamp').values_list('stamp', flat=True)[0]
            next_month_url = reverse('news:news:date', args=('%04d' % next_month.year,
                '%02d' % next_month.month, '%02d' % next_month.day))
        except IndexError:
            next_month = None
            next_month_url = None

        context = {
            'weeks': weeks,
            'previous_month': previous_month,
            'previous_month_url': previous_month_url,
            'next_month': next_month,
            'next_month_url': next_month_url,
            'month': date,
            'highlight': highlight,
            'highlight_link': highlight_link,
        }

        value = render_to_string('news-less/tags/calendar.html', context)
        cache.set(cache_key, value, expires)

    return HttpResponse(value)


@nginx_cached(60*5)
def rss(request):
    """RSS новостей"""

    with TagCache('news.rss', 60 * 10, tags=('news',)) as cache:
        value = cache.value
        if value is cache.EMPTY:
            value = NewsFeed().writeString('utf-8')
            cache.value = value

    return HttpResponse(value, content_type='application/rss+xml')


def yandex_rss(request):
    """RSS для Яндекса"""

    with TagCache('news.rss.yandex', 60 * 10, tags=('news',)) as cache:
        value = cache.value
        if value is cache.EMPTY:
            value = YandexFeed().writeString('utf-8')
            cache.value = value

    return HttpResponse(value, content_type='application/rss+xml')


@nginx_cached(60*60)
def opensearch_description(request):
    """Описание сервиса OpenSearch для новостей
    Suggest для новостей бесполезен: заголовок новости не влазит в поле некоторых браузеров, и поиск слабо релевантен"""

    return render(request, 'news/opensearch/description.xml', {})


def subscription(request):
    """Подписка на новости"""

    email = None

    if request.user.is_authenticated:
        try:
            subscriber = Subscriber.objects.filter(user=request.user)[0]
            return render(request, 'news-less/subscription/unsubscribe_form.html', {'subscriber': subscriber})
        except IndexError:
            pass

    if request.POST:
        if request.user.is_authenticated:
            subscriber = Subscriber(is_active=True, user=request.user, email=request.user.email,
                                    hash_stamp=datetime.datetime.now())
            subscriber.generate_hash()
            request.user.profile.subscribe = True
            request.user.profile.save()
            return render(request, 'news-less/subscription/success.html', {})
        else:
            form = SubscriptionAnonymousForm(request.POST)
            if form.is_valid():
                instance = form.cleaned_data

                subscriber = Subscriber(email=instance['email'], hash_stamp=datetime.datetime.now(), is_active=False)
                subscriber.generate_hash()

                if not request.user.is_authenticated:
                    tpl_notify(u'Подтверждение на рассылку новостей Ирк.ру', 'news/notif/subscription_confirm.html',
                               {'subscriber': subscriber}, request, (instance['email'], ))

                return render(request, 'news-less/subscription/confirm.html', {'email': subscriber.email})
    else:
        email = ''
        if request.user.is_authenticated:
            email = request.user.email
            form = None
        else:
            form = SubscriptionAnonymousForm()

    stamp = datetime.datetime.now()

    adwords = AdWord.objects.filter(periods__start__lte=stamp, periods__end__gte=stamp).distinct()[:3]
    company_news = CompanyNews.objects.filter(period__start=stamp).distinct().order_by('-id').distinct()[:3]

    news = News.material_objects.filter(is_hidden=False, is_payed=False).exclude(sites__slugs='elections').\
        order_by('-stamp', '-pk')

    distribution_news = []
    for s in Site.objects.all().exclude(slugs__in=['elections']).order_by('position'):
        _news = news.filter(source_site=s)[:3]
        if _news.exists():
            distribution_news.append((s, _news))

    article_list = Article.material_objects.filter(is_hidden=False).exclude(sites__slugs='elections').\
        order_by('-stamp', '-pk')[:3]

    foto_list = Photo.material_objects.filter(is_hidden=False).exclude(sites__slugs='elections').order_by('-stamp', '-pk')[:3]

    if distribution_news:
        distribution_message = render_to_string('news/notif/distribution_message.html', {
            'distribution_news': distribution_news,
            'adwords': adwords,
            'article_list': article_list,
            'foto_list': foto_list,
            'company_news': company_news,
        })
    else:
        distribution_message = ''

    context = {
        'email': email,
        'form': form,
        'distribution_message': distribution_message,
    }

    return render(request, 'news-less/subscription/add.html', context)


@ajax_request
def subscription_ajax(request):
    """
    Подписка на новости через Ajax

    Используется в формах подписки на страницах материалов.
    """

    email = request.json.get('email')
    if not email:
        return {'ok': False, 'msg': u'Не указан email'}

    try:
        validate_email(email)
    except ValidationError as e:
        return {'ok': False, 'msg': u'Неправильный email', 'errors': {'email': e.messages}}

    subscriber = Subscriber(email=email, hash_stamp=datetime.datetime.now(), is_active=False)
    subscriber.generate_hash()
    tpl_notify(
        u'Подтверждение на рассылку новостей Ирк.ру',
        'news/notif/subscription_confirm.html',
        {'subscriber': subscriber},
        request,
        [email]
    )

    return {'ok': True, 'msg': u'Подписка успешно оформлена'}


def subscription_confirm(request):
    """Подтверждение подписки"""

    hash_ = request.GET.get('hash')
    if not hash_:
        raise Http404()

    try:
        subscriber = Subscriber.objects.get(hash=hash_, hash_stamp__gte=datetime.datetime.now() - datetime.timedelta(2))
    except Subscriber.DoesNotExist:
        try:
            Subscriber.objects.get(hash=hash_)
            return render(request, 'news-less/subscription/expired.html')
        except Subscriber.DoesNotExist:
            raise Http404()

    subscriber.is_active = True
    subscriber.save()

    return render(request, 'news-less/subscription/success.html', {})


def subscription_unsubscribe(request):
    """Отмена подписки"""

    hash_ = request.GET.get('hash') or request.POST.get('hash')
    email = request.GET.get('mail') or request.POST.get('mail')

    try:
        subscriber = Subscriber.objects.get(email=email, hash=hash_)
    except Subscriber.DoesNotExist:
        raise Http404()

    if request.POST and request.POST.get('remove'):
        if subscriber.user:
            subscriber.user.profile.subscribe = False
            subscriber.user.profile.save()
        subscriber.delete()
        return render(request, 'news-less/subscription/unsubscribe_ok.html', {'email': email})
    return render(request, 'news-less/subscription/unsubscribe_confirm.html', {'hash': hash_, 'email': email})

@require_POST
def share_click(request, pk, slug):
    """Счетчик кликов на соц. кнопки материалов

    :param django.http.HttpRequest request:
    :param int pk: id материала
    :param str slug: алиас соц. сети из набора ('vk', 'fb', 'tw', 'ok')
    """

    if not request.is_ajax():
        raise Http404()

    if slug not in ('vk', 'fb', 'tw', 'ok'):
        logger.warning('Illegal slug for share_click {}'.format(slug))
        raise Http404()

    field_name = '{}_share_cnt'.format(slug)
    params = {
        field_name: F(field_name) + 1
    }

    material = get_object_or_404(BaseMaterial, pk=pk)
    BaseMaterial.objects.filter(pk=pk).update(**params)

    logger.debug('+1 {} share click for material with id {}'.format(slug, material.pk))

    return HttpResponse('')


def newsletter_materials(request, period):
    """Список рассылки материалов"""

    newsletter_map = {
        'daily': DailyNewsletter,
        'weekly': WeeklyNewsletter,
    }

    newsletter_class = newsletter_map.get(period)
    if not newsletter_class:
        raise Http404

    newsletter = newsletter_class.get_current()
    controller = NewsletterController(newsletter)

    materials = controller.get_materials()
    context = {
        'subscriber': None,
        'materials': grouper(materials, 2),
        'newsletter': newsletter,
    }

    return render(request, 'news/notif/distribution.html', context)
