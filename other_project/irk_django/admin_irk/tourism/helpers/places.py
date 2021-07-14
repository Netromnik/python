# -*- coding: utf-8 -*-

import redis
from xml.dom.minidom import parseString

from django.core.cache import cache
from django.conf import settings

from irk.utils.grabber import proxy_requests

from irk.tourism import settings as app_settings


class TonkostiRuClient(object):
    """Клиент доступа к экспорту данных tonkosti.ru"""

    def __init__(self, client_id):
        self._client_id = client_id
        self._url = 'http://tonkosti.ru/service/kxml.php'

    def countries(self):
        """Список стран"""
        
        key = 'tourism:tonkosti:countries'
        data = cache.get(key)
        if data:
            return data

        data = self._request({'getc': 1})
        if not data:
            return ()

        try:
            dom = parseString(data)
        except Exception:
            return ()

        countries = []
        for country in dom.getElementsByTagName('country'):
            countries.append({
                'id': int(country.getAttribute('id')),
                'title': country.firstChild.nodeValue.strip()
            })

        cache.set(key, countries, 3600)

        return countries

    def regions(self, country_id):
        """Список регионов страны"""
        
        key = 'tourism:tonkosti:regions:%s' % country_id
        data = cache.get(key)
        if data:
            return data

        data = self._request({'getr': 1, 'c': country_id})
        if not data:
            return ()

        try:
            dom = parseString(data)
        except Exception:
            return ()

        regions = []
        for region in dom.getElementsByTagName('region'):
            regions.append({
                'id': int(region.getAttribute('id')),
                'title': region.firstChild.nodeValue.strip()
            })

        cache.set(key, regions, 3600)

        return regions

    def country(self, country_id):
        """Информация о стране"""

        key = 'tourism:tonkosti:country:%s' % country_id
        data = cache.get(key)
        if data:
            return data

        data = self._request({'c': country_id})
        if not data:
            return ()

        try:
            dom = parseString(data)
        except Exception:
            return ()


        info = {}
        for element in dom.getElementsByTagName('typeinfo')[0].getElementsByTagName('info'):
            info[element.getAttribute('name')] = {
                'title': element.getAttribute('rusname'),
                'content': element.firstChild.nodeValue.strip()
            }

        cache.set(key, info, 3600)

        return info

    def region(self, region_id):
        """Информация о регионе"""

        key = 'tourism:tonkosti:region:%s' % region_id
        data = cache.get(key)
        if data:
            return data
    
        data = self._request({'c': region_id})
        if not data:
            return ()

        try:
            dom = parseString(data)
        except Exception:
            return ()

        info = {}
        for element in dom.getElementsByTagName('typeinfo')[0].getElementsByTagName('info'):
            info[element.getAttribute('name')] = {
                'title': element.getAttribute('rusname'),
                'content': element.firstChild.nodeValue.strip()
            }

        cache.set(key, info, 3600)

        return info

    def _request(self, params):
        """Запрос к сервису"""
        
        params.update({'cl': self._client_id})
        
        try:
            return proxy_requests.get(self._url, params=params).content
        except proxy_requests.RequestException:
            return None


def show_panorama():
    connection = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])

    return not connection.exists(app_settings.BAIKAL360_AVAILABILITY_KEY)
