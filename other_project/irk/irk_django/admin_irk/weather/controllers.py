# -*- coding: utf-8 -*-

from collections import deque

from irk.externals.models import InstagramMedia, InstagramTag
from irk.utils.views.mixins import PaginateMixin

from irk.weather.models import WishForDay, WishForConditions
from irk.weather import settings as app_settings


class WeatherInstagramController(PaginateMixin, object):
    """Контроллер постов инстаграмма про погоду"""

    page_limit_default = 5

    def get_posts(self, start, limit):
        """Получить посты"""

        weather_tags = list(InstagramTag.objects.filter(site__slugs='weather').values_list('id', flat=True))
        posts = InstagramMedia.objects \
            .filter(tags__in=weather_tags, is_visible=True) \
            .order_by('-created', '-id') \
            .distinct()

        self.start_index = start
        self.page_limit = limit
        objects, page_info = self._paginate(posts)

        return objects, page_info


class WishController(object):
    """Контроллер пожеланий на главной странице погоды"""

    def __init__(self, forecast, meteocentre):
        """
        :param ForecastCurrent forecast: прогноз погоды
        :param MeteoCentre meteocentre: информация от ГидроМетеоЦентра
        """

        self._city = forecast.city
        self._forecast = forecast
        self._timestamp = forecast.stamp
        self._meteocentre = meteocentre

    def get_wish(self):
        """Получить пожелание"""

        wish = self._wish_for_day()
        if wish:
            wish.origin = 'wish_for_day'
            return wish

        wish = self._wish_for_storm()
        if wish:
            wish.origin = 'wish_for_storm'
            return wish

        wish = self._wish_for_strong_wind()
        if wish:
            wish.origin = 'wish_for_strong_wind'
            return wish

        wish = self._wish_for_conditions()
        if wish:
            wish.origin = 'wish_for_conditions'
            return wish

        return self._wish_default()

    def _wish_for_day(self):
        """Пожелание на день"""

        wish = WishForDay.objects.filter(date=self._timestamp.date()).first()

        return wish

    def _wish_for_storm(self):
        """Пожелание для штормового предупреждения"""

        if self._meteocentre and self._meteocentre.is_storm():
            return WishForConditions.conditions.active().by_month(self._timestamp.month).filter(is_storm=True).first()

        return None

    def _wish_for_strong_wind(self):
        """Пожелание для сильного ветра"""

        if self._forecast.wind.speed >= app_settings.STRONG_WIND_SPEED:
            return WishForConditions.conditions \
                .active() \
                .by_month(self._timestamp.month) \
                .filter(is_strong_wind=True) \
                .first()

        return None

    def _wish_for_conditions(self):
        """Пожелание по погодным условиям"""

        conditions = {
            'is_storm': False,
            'is_strong_wind': False,
        }

        if self._forecast.temp_day is not None:
            conditions.update({
                't_min__lte': self._forecast.temp_day, 't_max__gte': self._forecast.temp_day,
            })

        if self._forecast.sky:
            if self._forecast.sky.nebulosity_code == 'cloudy':
                conditions['is_cloudy'] = True
                conditions['is_variable'] = False
            elif self._forecast.sky.nebulosity_code == 'variable':
                conditions['is_variable'] = True
                conditions['is_cloudy'] = False
            else:
                conditions['is_cloudy'] = conditions['is_variable'] = False

            if self._forecast.sky.precipitation_code != 'lack':
                conditions['is_precipitation'] = True
            else:
                conditions['is_precipitation'] = False

        wishes = WishForConditions.conditions.active().by_month(self._timestamp.month).filter(**conditions)

        return self._choose(wishes)

    def _choose(self, wishes):
        """
        Выбрать пожелания из списка.

        Может существовать несколько пожеланий для одних и тех же погодных условий.
        Такие пожелания ротируются, чтобы на соседние дни отображались разные пожелания.
        """
        wishes_count = wishes.count()
        if wishes_count == 0:
            return

        if wishes_count == 1:
            return wishes.first()

        wishes_ids = deque(wishes.values_list('id', flat=True))
        wishes_ids.rotate(self._timestamp.day)
        wish_id = wishes_ids[0]

        return wishes.get(id=wish_id)

    def _wish_default(self):
        """Пожелание по умолчанию"""

        # Пожелание по умолчанию, это такое пожелание у которого нет никаких условий
        conditions = {
            'months__isnull': True,
            't_min__isnull': True,
            't_max__isnull': True,
            'is_storm': False,
            'is_strong_wind': False,
            'is_cloudy': False,
            'is_precipitation': False,
            'is_variable': False,
        }

        wish = WishForConditions.conditions.active().filter(**conditions).first()
        if wish:
            wish.origin = 'wish_default'

        return wish
