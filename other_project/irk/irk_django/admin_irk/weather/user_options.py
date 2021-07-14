# -*- coding: utf-8 -*-

import datetime

from irk.profiles.options import Option
from irk.options.models import Site
from irk.map import models

from irk.weather.forecasts import ForecastForCities


class WeatherFavoriteCity(Option):
    """Любимый город погоды"""

    cookie_key = 'wl'
    template = 'weather/snippets/favourite_city_selector.html'
    multiple = False

    def __init__(self, *args, **kwargs):
        self.weather_site = Site.objects.get_by_alias('weather')
        self._choices_cache = None
        super(WeatherFavoriteCity, self).__init__(*args, **kwargs)

    @property
    def choices(self):
        if self._choices_cache is None:
            cities = self.weather_site.cities_set.order_by('region', 'order').prefetch_related('region')
            cities = self._add_forecasts(cities)
            self._choices_cache = cities
        return self._choices_cache

    @property
    def default(self):
        return self.choices.first() or models.Cities.objects.get(slugs='irkutsk')

    def load_value_from_cookie(self, value):
        try:
            value = int(value)
            return self.choices.get(pk=value)
        except (TypeError, ValueError, models.Cities.DoesNotExist):
            return self.default

    def prepare_value_for_cookie(self, value):
        if isinstance(value, models.Cities):
            return value.pk
        return value

    def load_value_from_db(self, value):
        return self.load_value_from_cookie(value)

    def prepare_value_for_db(self, value):
        return self.prepare_value_for_cookie(value)

    def _add_forecasts(self, cities):
        """Добавить к городам прогноз погоды"""

        stamp = datetime.datetime.now()
        fc = ForecastForCities(stamp)
        cities = fc.add_forecasts(cities)

        return cities

    class Meta:
        verbose_name = u'Город для погоды'

