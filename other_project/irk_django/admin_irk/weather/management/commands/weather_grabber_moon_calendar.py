# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
from lxml.html import fromstring

from django.core.management.base import BaseCommand

from irk.utils.grabber import proxy_requests
from irk.utils.helpers import first_or_none

from irk.weather.models import MoonDay

logger = logging.getLogger(__name__)


def clear(string):
    """Очистить строку от лишних символов в начале и в конце"""

    return string.strip(' .-\n')


class Command(BaseCommand):
    help = 'Граббинг лунного календаря'

    source_url = 'https://www.life-moon.pp.ru/moon-days/{}/'
    # соответствие класса иконки с влиянием полю в модели MoonDay
    icons_map = {
        'icon-c-undertakings': 'for_undertaking',
        'icon-c-money': 'for_money',
        'icon-c-dreams': 'for_dream',
        'icon-c-housework': 'for_housework',
        'icon-c-hair': 'for_haircut',
        'icon-c-eating': 'for_drink',
    }

    def handle(self, **options):
        logger.debug('Start grabbing moon calendar')

        MoonDay.objects.all().delete()

        for i in xrange(1, 31):
            self._grab(i)

        logger.debug('Finish grabbing moon calendar')

    def _grab(self, number):
        """Получить и сохранить информацию"""

        url = self.source_url.format(number)

        try:
            response = proxy_requests.get(url, timeout=10)
            response.raise_for_status()
        except proxy_requests.RequestException:
            logger.error('Fail load data from {}'.format(url))
            return

        html = fromstring(response.content)
        article = first_or_none(html.cssselect('.content section article'))
        if not article:
            logger.error(u'Not article into {}'.format(url))
            return

        title = self._get_title(article)
        symbol = self._get_symbol(article)
        stones = self._get_stones(article)
        content = self._get_content(article)
        affects = self._get_affects(article)

        MoonDay.objects.create(number=number, title=title, symbol=symbol, stones=stones, content=content, **affects)
        logger.debug('Success create {} moon day'.format(number))

    def _get_title(self, article):
        """Получить заголовок"""

        tag = first_or_none(article.xpath('.//h1[1]'))
        if tag is not None:
            return clear(tag.text.lower())

        return ''

    def _get_symbol(self, article):
        """Получить символ"""

        tag = first_or_none(article.xpath('./div[@class="l-box"][3]/p/strong'))
        if tag is not None and tag.text.lower() == 'символ':
            return clear(tag.tail)

        return ''

    def _get_stones(self, article):
        """Получить камни"""

        tag = first_or_none(article.xpath('./div[@class="l-box"][3]/p/strong[2]'))
        if tag is not None and tag.text.lower() == 'камни':
            return clear(tag.tail)

        return ''

    def _get_content(self, article):
        """Получить описание"""

        content = []
        tags = article.xpath('./div[@class="l-box"][3]/p')[1:]
        for tag in tags:
            content.append(tag.text_content())

        return '\n\n'.join(content)

    def _get_affects(self, article):
        """Получить информацию о влиянии на сферы жизни"""

        affects_map = {v: k for k, v in MoonDay.AFFECTS}

        affects = {}
        tags = article.xpath('./table/tr')
        for tag in tags:
            icon_class = first_or_none(tag.xpath('.//i/@class'))
            if icon_class not in self.icons_map:
                continue

            value = first_or_none(tag.xpath('./td[3]/text()'))
            value = clear(value).lower()
            if value not in affects_map:
                continue

            affects[self.icons_map[icon_class]] = affects_map[value]

        return affects
