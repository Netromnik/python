# -*- coding: utf-8 -*-
import os

from django.conf import settings as global_settings

# Время жизни тега в memcached
CACHE_TAG_LIFETIME = getattr(global_settings, 'CACHE_TAG_LIFETIME', 60 * 60 * 24 * 31)  # Один месяц

# Префикс для всех тегов кэша
CACHE_TAG_PREFIX = 'tags:%s'

# TODO: docstring
SEARCH_ENGINES_USERAGENTS = (
    # Яндекс
    'YandexBot',
    'YandexImages',
    'YandexVideo',
    'YandexMedia',
    'YandexBlogs',
    'YandexAddurl',
    'YandexFavicons',
    'YandexDirect',
    'YandexMetrika',
    'YandexCatalog',
    'YandexNews',
    'YandexImageResizer',

    # Google
    'Googlebot',
    'Mediapartners-Google',
    'gsa-crawler',
    'AdsBot-Google',

    # Rambler
    'StackRambler',

    # Yahoo
    'Yahoo! Slurp',
    'Yahoo-MMCrawler',
    'Yahoo-Blogs',

    # Aport
    'Aport', # поисковый робот Апорта
    'AportCatalogRobot', # робот Апорт каталога.

    # MSN
    'msnbot',

    # Alexa
    'ia_archiver',
)

# TODO: docstring
SHARE_BUTTONS_SHOW = getattr(global_settings, 'SHARE_BUTTONS_SHOW', True)

# Варианты 404-й страницы
TEMPLATES_404 = (
    '404/gagarin.html',
    '404/ezhik.html',
    '404/irk_panorama.html',
)

LESS_ROOT = os.path.join(global_settings.STATIC_ROOT, 'less')

LESS_OUTPUT_DIR = os.path.join(global_settings.STATIC_ROOT, 'css', 'compiled')

# без префикса `settings.STATIC_URL`
LESS_OUTPUT_URL = 'css/compiled'

RAVENJS_SETTINGS = {
    'whitelist_urls': [
        'www.irk.ru', 'static.irk.ru',
    ],
    'ignore_urls': [
        'connect.facebook.net',
        'graph.facebook.com',
        'vkontakte.ru',
        'vk.com',
        'connect.ok.ru',
        'stats.g.doubleclick.net',
        'cluster.adultadworld.com',
        'syndication.twitter.com',
        'mc.yandex.ru'
    ],
    'ignore_errors': [
        'top.GLOBALS',
        'chrome/RendererExtensionBindings',
        'miscellaneous_bindings',
        'fb_xd_fragment',
    ],
}

# Путь до программы для удаления exif тегов exiv2
EXIV2_PATH = '/usr/bin/exiv2'

# Дни недели
WEEKDAY_MON = 0
WEEKDAY_TUE = 1
WEEKDAY_WEN = 2
WEEKDAY_THU = 3
WEEKDAY_FRI = 4
WEEKDAY_SAT = 5
WEEKDAY_SUN = 6

WEEKDAYS = {
    WEEKDAY_MON: u'Понедельник',
    WEEKDAY_TUE: u'Вторник',
    WEEKDAY_WEN: u'Среда',
    WEEKDAY_THU: u'Четверг',
    WEEKDAY_FRI: u'Пятница',
    WEEKDAY_SAT: u'Суббота',
    WEEKDAY_SUN: u'Воскресенье',
}
