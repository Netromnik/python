# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime
import random
import logging
import itertools

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic.base import View

from irk.afisha.models import CurrentSession
from irk.externals.models import InstagramTag, InstagramMedia
from irk.news.models import Article, Photo
from irk.obed.models import Establishment
from irk.options.models import Site
from irk.utils.helpers import int_or_none
from irk.utils.http import JsonResponse
from irk.utils.views.mixins import PaginateMixin

from irk.newyear2014.forms import CongratulationForm, AnonymousCongratulationForm
from irk.newyear2014.helpers import generate_rotation_key
from irk.newyear2014.models import Horoscope, Infographic, TextContest, PhotoContest, Congratulation, Wallpaper, Offer
from irk.newyear2014.permissions import is_moderator

logger = logging.getLogger(__name__)


class IndexView(View):
    """Главная страница"""

    # Ключ сессии, в котором будет храниться позиция ротации для пользователя
    AFISHA_ROTATION_SESSION_KEY = 'newyear_home_afisha_rotation'

    # Количество событий, выводимых в блоке афиши
    AFISHA_ROTATION_FRAME_SIZE = 4

    def __init__(self, **kwargs):
        super(IndexView, self).__init__(**kwargs)

    def get(self, request):

        try:
            infographic = Infographic.objects.filter(sites=request.csite, is_hidden=False).order_by('-created')[0]
        except IndexError:
            infographic = None

        # wallpapers = Wallpaper.objects.all().order_by('-pk')[:5]

        context = {
            # 'afisha': self._afisha(request),
            'horoscope': self._horoscope(request),
            # 'infographic': infographic,
            # 'news': self._news(request),
            # 'contests': self._contests(),
            'congratulations': self._congratulations(request),
            # 'instagram': self._instagram(request),
            # 'wallpapers': wallpapers,
            # 'sms_form': SendSMSForm(request.user),
            'corporates': self._get_corporates(),
            'gifts': self._get_gifts(),
            'hostels': self._get_hostels(),
        }

        return render(request, 'newyear2014/index.html', context)

    def _congratulations(self, request):

        initial = {}

        if request.user.is_authenticated:
            fio = []
            if request.user.last_name:
                fio.append(request.user.last_name)
            if request.user.first_name:
                fio.append(request.user.first_name)
            if request.user.profile.mname:
                fio.append(request.user.profile.mname)
            if not fio:
                fio.append(request.user.username)
            initial['sign'] = ' '.join(fio)

        if request.user.is_authenticated:
            form = CongratulationForm(initial=initial)
        else:
            form = AnonymousCongratulationForm(initial=initial)

        congratulations = Congratulation.objects.filter(is_hidden=False).order_by('-created', '-id')[:2]

        return {
            'form': form,
            'objects': congratulations
        }

    def _news(self, request):
        moderator = is_moderator(request.user)

        articles = Article.material_objects.filter(sites=request.csite).order_by('-stamp',
                                                                        '-pk').extra(select={'model': '"article"'})
        if not moderator:
            articles = articles.filter(is_hidden=False)
        articles = list(articles[:4])

        photos = Photo.material_objects.filter(sites=request.csite).order_by('-stamp', '-pk').extra(select={'model': '"photo"'})
        if not moderator:
            photos = photos.filter(is_hidden=False)
        photos = list(photos[:4])

        items = sorted(itertools.chain(articles, photos), key=lambda x: x.stamp, reverse=True)[:4]
        if not any(isinstance(x, Photo) for x in items) and photos:
            # Заменяем последнюю статью на фоторепортаж
            items.pop()
            items.append(photos[0])

        return {
            'articles_and_photos': items,
        }

    def _afisha(self, request):
        """Афиша"""

        # Выбираем все текущие анонсы
        announcements_ids = []
        events_ids = []

        # Зачем нужна сортировка по полю `date`: `afisha.models.Event.get_absolute_url` использует данные ближайшего сеанса,
        # чтобы сформировать ссылку (см. ниже код `event.schedule.append(session)`), поэтому нам нужно здесь выбрать
        # ближайший сеанс.
        announcements = CurrentSession.objects.filter(real_date__gt=datetime.datetime.now(),
            event__is_newyear_home_announcement=True).values_list('id', 'event_id').order_by('date', 'event')

        # Выбираем из них только уникальные события
        for announcement_id, event_id in announcements:
            if not event_id in events_ids:
                events_ids.append(event_id)
                announcements_ids.append(announcement_id)

        # Делаем цикличную ротацию между всеми получившимися событиями
        try:
            position_id = int(request.session[self.AFISHA_ROTATION_SESSION_KEY])
            if position_id >= len(announcements_ids):
                raise OverflowError()
            logger.debug('Got a afisha rotation position from session: %s' % position_id)
        except (TypeError, ValueError, KeyError):
            position_id = random.randint(0, len(announcements_ids))
            logger.debug('Generating random afisha rotation pos: %s' % position_id)
        except OverflowError:
            position_id = 0

        request.session[self.AFISHA_ROTATION_SESSION_KEY] = position_id + 1
        request.session.save()

        start = position_id
        end = position_id + self.AFISHA_ROTATION_FRAME_SIZE

        current_announcements = announcements_ids[start:end]
        if end > len(announcements_ids):
            current_announcements += announcements_ids[:self.AFISHA_ROTATION_FRAME_SIZE-len(current_announcements)]

        announcements = list(CurrentSession.objects.filter(id__in=current_announcements).select_related('event'))
        # Кэшируем информацию о ближайшем сеансе у каждого события
        announce_events = set([s.event for s in announcements])
        for event in announce_events:
            for session in announcements:
                if session.event_id == event.id:
                    event.schedule.append(session)
                    break

        # Сортируем в нужной нам последовательности
        announcements = sorted(announcements, key=lambda x: current_announcements.index(x.id))

        return {
            'announcements': announcements,
        }

    def _horoscope(self, request):

        horoscopes = Horoscope.objects.all().order_by('-position')

        return {
            'horoscopes': horoscopes,
        }

    def _contests(self):
        today = datetime.date.today()
        text = list(TextContest.objects.filter(date_start__lte=today,
                                               date_end__gte=today).extra(select={'model': '"text"'}))
        photo = list(PhotoContest.objects.filter(date_start__lte=today,
                                                 date_end__gte=today).extra(select={'model': '"photo"'}))

        contests = list(itertools.chain(text, photo))
        random.shuffle(contests)

        return contests

    def _instagram(self, request):
        try:
            tags = InstagramTag.objects.filter(site=Site.objects.get(slugs='newyear2014'), is_visible=True)
        except InstagramTag.DoesNotExist:
            tags = ()

        images = InstagramMedia.objects.filter(is_visible=True, tags__in=tags).order_by('-id')[:6]

        return {
            'images': images,
            'tags': tags,
        }

    def _get_corporates(self):
        """Корпоративы"""

        queryset = Establishment.objects \
            .filter(is_active=True, visible=True, corporative=True) \
            .exclude(corporative_description__isnull=True).exclude(corporative_description__exact='') \
            .order_by('name')

        establishments = list(queryset)
        random.shuffle(establishments)

        return establishments

    def _get_gifts(self):
        """Подарки"""

        queryset = Offer.objects.show().visible().filter(category__slug='gift')

        offers = list(queryset)
        random.shuffle(offers)

        return offers

    def _get_hostels(self):
        """Турбазы"""

        queryset = Offer.objects.show().visible().filter(category__slug='hostel')

        offers = list(queryset)
        random.shuffle(offers)

        return offers


class CorporateList(PaginateMixin, View):
    """Корпоративы"""

    model = Establishment
    template = 'newyear2014/corporates/index.html'
    ajax_template = 'newyear2014/corporates/list.html'
    # Количество объектов на странице
    page_limit_default = 40
    # Максимальное количество объектов на странице
    page_limit_max = page_limit_default

    def get(self, request, *args, **kwargs):
        self._parse_params()

        establishments = self._get_establishments()
        object_list, page_info = self._paginate(establishments)

        context = {
            'corporates': object_list,
        }

        if self.request.is_ajax():
            return self._render_ajax_response(context, page_info)

        context.update(page_info)
        return render(request, self.template, context)

    def _parse_params(self):
        """Разобрать параметры переданные в url и в строке запроса"""

        self._category = None
        # класса Category больше нет, код ниже не работает
        # if self.kwargs.get('category_slug'):
        #     self._category = get_object_or_404(Category, slug=self.kwargs['category_slug'])

        # Параметры пагинации
        start_index = int_or_none(self.request.GET.get('start')) or 0
        self.start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self.page_limit = min(page_limit, self.page_limit_max)

    def _get_establishments(self):
        """Получить обычные предложения"""

        establishments = list(self._get_queryset())

        # Ротация предложений с сохранением порядка для каждого пользователя
        key = generate_rotation_key(self.request)
        random.seed(key)
        random.shuffle(establishments)

        return establishments

    def _get_queryset(self, **kwargs):
        """Вернуть queryset с предложениями"""

        queryset = self.model.objects \
            .filter(is_active=True, visible=True, corporative=True) \
            .exclude(corporative_description__isnull=True).exclude(corporative_description__exact='') \
            .order_by('name')

        if kwargs:
            queryset = queryset.filter(**kwargs)

        return queryset

    def _render_ajax_response(self, context, page_info):
        """
        Отправить ответ на Ajax запрос

        :param dict context: контекст шаблона
        :param dict page_info: информация о странице
        """

        return JsonResponse(dict(
            html=render_to_string(self.ajax_template, context),
            **page_info
        ))


index = IndexView.as_view()
corporates = CorporateList.as_view()
