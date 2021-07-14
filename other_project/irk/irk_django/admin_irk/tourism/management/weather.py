# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
import logging
import os

import yaml
from django.conf import settings

from irk.utils.files.helpers import static_link

WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
WEATHER_FOLDER_DEF = "%s/tmp/places_weather/" % settings.BASE_PATH
WEATHER_FOLDER = getattr(settings, 'PLACES_WEATHER_FOLDER', WEATHER_FOLDER_DEF)

logger = logging.getLogger(__name__)
weather_config = yaml.safe_load(open(os.path.join(settings.BASE_PATH, 'weather_config.yaml')))


def load(pk, weather_code):
    try:
        forecast = json.load(file("%splace_id_%s" % (WEATHER_FOLDER, pk)))
        if forecast.has_key('error'):
            forecast = False
    except Exception:
        logger.exception('Failed to load weather for place {}'.format(pk))
        forecast = False

    if forecast and 'code' in forecast:
        forecast['image'] = static_link('img/weather/new/%s.png' % weather_config['yahoo_images'][forecast['code']])

    logger.debug('Loaded weather forecast for place {}'.format(pk))

    return forecast
