# -*- coding: utf-8 -*-

import datetime
import logging
import random

from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic.base import View

from irk.afisha.models import Announcement, Event
from irk.blogs.models import BlogEntry
from irk.home import settings as app_settings
from irk.home.controllers import MaterialController
from irk.magazine.models import Magazine
from irk.map.models import Cities
from irk.news.models import (BaseMaterial, News, Photo, Postmeta, Subject,
                             UrgentNews)
from irk.news.permissions import is_moderator as is_news_moderator
from irk.options.models import Site
from irk.testing.models import Test
from irk.utils.helpers import first_or_none, int_or_none
from irk.utils.http import JsonResponse
from irk.utils.lazy import LazyDict, LazyList
from irk.utils.metrics import newrelic_record_timing

EMPTY_OBJECT = object()

logger = logging.getLogger(__name__)


class HomeView(View):
    """Главная страница"""

    # Ключ сессии, в котором будет храниться позиция ротации для пользователя
    AFISHA_ROTATION_SESSION_KEY = 'home_afisha_rotation'

    # Алиасы разделов, которые будут выбраны
    sites_aliases = ('home', 'news', 'tourism', 'obed', 'afisha')

    ajax_template = 'home/snippets/entries.html'
    defer_fields = ('content',)

    def __init__(self, **kwargs):
        super(HomeView, self).__init__(**kwargs)

        self._now = datetime.datetime.now()
        self._site_news = Site.objects.get(slugs='news')
        self._site_home = Site.objects.get(slugs='home')
        self.is_moderator = False

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax_get(request)

        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request):

        self.is_moderator = is_news_moderator(request.user)

        context = {
            'materials': self._materials(),  # lazy
            'photo': self._photo(),  # lazy
            'news': self._news(),
            'subject': self._subject(),
            'magazine': self._magazine(),
            'afisha': self._afisha(request),
            'blogs': self._blogs(),
            'tests': self._tests(),
            'today': datetime.date.today(),
            'covid_cases': self._covid_cases(),
        }
        return render(request, 'home/index.html', context)

    def ajax_get(self, request):
        """Аяксовая подгрузка новостей"""

        news = self._news_queryset()

        start = int_or_none(request.GET.get('start')) or 0
        start = max(start, 0)
        limit = int_or_none(request.GET.get('limit')) or app_settings.HOME_NEWS_MORE
        limit = min(limit, app_settings.HOME_NEWS_MORE)

        news, page_info = self._paginate(news, start, limit)

        context = {
            'news': news,
        }
        context.update(page_info)

        return JsonResponse({
            'html': render_to_string(self.ajax_template, context),
            'has_next': context['has_next'],
            'next_limit': context['next_limit'],
            'next_start_index': context['next_start_index'],
        })

    def _paginate(self, queryset, start, limit):
        """Пейджинация для аяксовой кнопки догрузки новостей"""

        total = queryset.count()

        end = min(start + limit, total)
        object_list = queryset[start:end]

        page_info = {
            'has_next': total > end,
            'next_start_index': end,
            'next_limit': min(app_settings.HOME_NEWS_MORE, total - end)
        }

        return object_list, page_info

    @newrelic_record_timing('Custom/Home/Materials')
    def _materials(self):
        """
        Материалы для главной (не новости)
        Lazy лист позволяет не дергать базу, когда шаблоны главной закешированы.
        """
        def load():
            return MaterialController(show_hidden=self.is_moderator).get_materials()

        return LazyList(load)

    @newrelic_record_timing('Custom/Home/Photo')
    def _photo(self):
        """
        Фоторепортаж
        Не обращается к базе данных, если шаблон на фронтенде закеширован.
        """
        return LazyDict({'photos': self._photo_data})

    def _photo_data(self):
        """Фоторепортаж - данные"""

        filters = {}
        if not self.is_moderator:
            filters['is_hidden'] = False

        photos = Photo.material_objects.filter(**filters).select_subclasses().order_by('-stamp', '-pk')[:30]

        # Из последних 30 фоторепов выбираем те у которых есть лучшие фотки
        photos_best = []
        for item in photos:
            if item.gallery.has_best_image():
                photos_best.append(item)
                if len(photos_best) >= app_settings.HOME_PHOTOS_COUNT:
                    break

        return photos_best

    @newrelic_record_timing('Custom/Home/News')
    def _news(self):
        """Новости"""

        news = self._news_queryset()
        news = list(news[:app_settings.HOME_NEWS_COUNT])
        main_news = first_or_none(news)
        last_news = news[1:]

        # срочная новость
        urgent = UrgentNews.objects.filter(is_visible=True).order_by('-id').first()

        return {
            'is_moderator': self.is_moderator,
            'main': main_news,
            'last': last_news,
            'urgent': urgent,
            'next_start_index': app_settings.HOME_NEWS_COUNT,
        }

    def _news_queryset(self):
        # увеличение дней сильно ухудшает производительность
        two_weeks_ago = self._now - datetime.timedelta(days=14)

        # Новости, без фоторепортажей и статей, только для Иркутска.
        news = News.material_objects.for_site(self._site_news) \
            .filter(stamp__gte=two_weeks_ago, is_payed=False) \
            .defer(*self.defer_fields) \
            .order_by('-stamp', '-published_time')

        if not self.is_moderator:
            news = news.filter(is_hidden=False)
        else:
            news = news.exclude_future_drafts(**app_settings.HOME_NEWS_FUTURE_WINDOW)

        return news

    @newrelic_record_timing('Custom/Home/Subject')
    def _subject(self):
        """Сюжет"""

        ordering = ('-stamp', '-id')

        # Новости, без фоторепортажей и статей, только для Иркутска.
        subject = Subject.objects.filter(show_on_home=True, is_visible=True).order_by('-id').first()

        if not subject:
            return []

        # Материалы
        materials = BaseMaterial.longread_objects.filter(subject=subject) \
            .prefetch_related('source_site', 'content_type') \
            .order_by(*ordering).select_subclasses()

        if not self.is_moderator:
            materials = materials.filter(is_hidden=False)

        # Новости
        news = News.material_objects.filter(subject=subject).defer(*self.defer_fields).order_by(*ordering)

        if not self.is_moderator:
            news = news.filter(is_hidden=False)

        return {
            'subject': subject,
            'materials': materials[:2],
            'news': news[:3],
        }

    @newrelic_record_timing('Custom/Home/Afisha')
    def _afisha(self, request):
        """Блок Афиша: Интересное"""

        event_ids = Announcement.objects \
            .for_place(Announcement.PLACE_HOME_SLIDER) \
            .active() \
            .filter(event__is_hidden=False) \
            .distinct() \
            .values_list('event', flat=True)

        event_ids = list(event_ids)
        event_count = len(event_ids)

        # Делаем цикличную ротацию между всеми получившимися событиями
        try:
            position_id = int(request.session[self.AFISHA_ROTATION_SESSION_KEY])
            if position_id >= event_count:
                position_id = 0
            logger.debug('Got a afisha rotation position from session: %s' % position_id)
        except (TypeError, ValueError, KeyError):
            position_id = random.randint(0, event_count)
            logger.debug('Generating random afisha rotation pos: %s' % position_id)

        request.session[self.AFISHA_ROTATION_SESSION_KEY] = position_id + 1
        request.session.save()

        start = position_id
        end = position_id + event_count
        selected_events_ids = event_ids[start:end]
        if end > event_count:
            selected_events_ids += event_ids[:event_count - len(selected_events_ids)]

        events = Event.objects.filter(id__in=selected_events_ids)
        for event in events:
            cs = event.currentsession_set.order_by('date').first()
            if not cs:
                event.date = None
                continue
            event.date = cs.date
            event.schedule.append(cs)
        return {
            'events': sorted(events, key=lambda e: selected_events_ids.index(e.id)),
        }

    @newrelic_record_timing('Custom/Home/Blogs')
    def _blogs(self):
        """Блоги"""

        entries = BlogEntry.objects \
                      .filter(type=BlogEntry.TYPE_BLOG, author__is_visible=True, visible=True) \
                      .order_by('-id') \
                      .select_related('author') \
                      .defer('content')[:4]

        return {
            'entries': entries
        }

    @newrelic_record_timing('Custom/Home/Tests')
    def _tests(self):
        """Тесты"""

        tests = Test.material_objects.for_site(self._site_home).order_by('-id').defer('content')

        if not self.is_moderator:
            tests = tests.filter(is_hidden=False)

        return tests[:4]

    @newrelic_record_timing('Custom/Home/Magazine')
    def _magazine(self):
        """Журнал"""

        magazines = Magazine.objects.filter(show_on_home=True)

        if not self.is_moderator:
            magazines = magazines.filter(visible=True)

        return {
            'magazine': magazines.first(),
        }

    def _covid_cases(self):
        """
        Число зараженных вирусом для мобильной плашки
        """
        # постмета от лендиг-страницы со слагом main
        query = Postmeta.objects.filter(landings_covidpage__slug='main', key='irk_cases').values('value')
        try:
            return query[0]['value']
        except IndexError:
            logger.info('Covid info not found')
            return None


index = HomeView.as_view()
