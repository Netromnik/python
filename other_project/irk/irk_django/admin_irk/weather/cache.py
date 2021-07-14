# -*- coding: utf-8 -*-

from irk.utils.cache import invalidate_tags


def invalidate(sender, **kwargs):
    """Протухание кэша погоды"""

    from irk.weather import models

    instance = kwargs.get('instance')
    tags = []

    if isinstance(instance, models.WeatherFact):
        tags.append('forecast_current')
        tags.append('forecast')

    if isinstance(instance, models.WeatherCities):
        tags.append('forecast_day')
        tags.append('forecast')

    if isinstance(instance, models.WeatherDetailed):
        tags.append('forecast_detailed')
        tags.append('forecast')

    if isinstance(instance, models.MeteoCentre):
        tags.append('meteocentre_model')

    if isinstance(instance, models.WeatherSigns):
        tags.append('sign_model')

    if isinstance(instance, models.WishBase):
        tags.append('wish_model')

    invalidate_tags(tags)
