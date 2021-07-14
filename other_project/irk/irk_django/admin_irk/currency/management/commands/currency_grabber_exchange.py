# -*- coding: utf-8 -*-

"""Граббер курсов обмена валют с сайта ЦБ

Заполняются данные обмена валют для WM
и обновляется информация курсов ЦБ РФ для доллара, евро и йены"""

import datetime
import logging
from xml.dom.minidom import parseString

from django.core.management.base import BaseCommand

from irk.utils.grabber import proxy_requests
from irk.utils.grabber.helpers import get_random_useragent

from irk.currency.models import ExchangeRate, CurrencyCbrf


RATE_DATA_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'


class Command(BaseCommand):

    def handle(self, *args, **options):
        headers = {
            'User-agent': get_random_useragent(),
            'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'deflate, identity, *;q=0',
        }

        try:
            dom = parseString(proxy_requests.get(RATE_DATA_URL, headers=headers).content)
        except proxy_requests.RequestException:
            logging.exception(u'URL "%s" is inaccessible' % RATE_DATA_URL)
            raise  # Заново выбрасываем исключение, чтобы перезапустить задачу граббера

        try:
            cbrf_rate = CurrencyCbrf.objects.get(stamp=datetime.date.today())
        except CurrencyCbrf.DoesNotExist:
            cbrf_rate = CurrencyCbrf(stamp=datetime.date.today(), visible=True)

        for element in dom.getElementsByTagName('Valute'):
            num_code = int(element.getElementsByTagName('NumCode')[0].firstChild.nodeValue)
            code = element.getElementsByTagName('CharCode')[0].firstChild.nodeValue
            name = element.getElementsByTagName('Name')[0].firstChild.nodeValue
            nominal = element.getElementsByTagName('Nominal')[0].firstChild.nodeValue
            value = float(element.getElementsByTagName('Value')[0].firstChild.nodeValue.replace(',', '.'))

            try:
                rate = ExchangeRate.objects.get(code=code)
            except ExchangeRate.DoesNotExist:
                rate = ExchangeRate(numeral_code=num_code, code=code, name=name)
            rate.nominal = nominal
            rate.value = value
            rate.save()

            code = code.lower()
            if code == 'usd':
                cbrf_rate.usd = value
            elif code == 'eur':
                cbrf_rate.euro = value
            elif code == 'cny':
                cbrf_rate.cny = value
        cbrf_rate.save()
