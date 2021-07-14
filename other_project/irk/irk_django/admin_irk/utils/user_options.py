# -*- coding: utf-8 -*-

import pickle

from django.db.models import Model
from django.core.exceptions import ObjectDoesNotExist

from irk.profiles.options import Option
from irk.map import models
from irk.options.models import Site


#@todo: Перенести!!!!!!!!!
class City(Option):
    """Город пользователя для афиши и карты"""

    cookie_key = 'ct'
    template = 'snippets/city_selector.html'
    multiple = False

    def __init__(self, *args, **kwargs):
        self.afisha_site = Site.objects.get_by_alias('afisha')
        super(City, self).__init__(*args, **kwargs)

    @property
    def choices(self):
        return self.afisha_site.cities_set.all()

    @property
    def default(self):
        try:
            return self.choices.order_by('order')[0]
        except IndexError:
            return models.Cities.objects.get(alias='irkutsk')

    def load_value_from_cookie(self, value):
        try:
            return models.Cities.objects.get(pk=int(value))
        except models.Cities.DoesNotExist:
            return self.default
        
    def prepare_value_for_cookie(self, value):
        if isinstance(value, Model):
            return value.pk
        return value

    def load_value_from_db(self, value):
        try:
            return pickle.loads(str(value)) # Для старых данных в базе
        except (pickle.UnpicklingError, KeyError, TypeError, IndexError):
            try:
                return self.choices.get(pk=value)
            except ObjectDoesNotExist:
                return self.default

    def prepare_value_for_db(self, value):
        if isinstance(value, Model):
            return value.pk
        return value

    class Meta:
        verbose_name = u'Показывать каналы'
