# -*- coding: utf-8 -*-

"""Граббер карт с температурой, циклонами и землетрясениями"""

import os
import logging
import datetime
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from requests.auth import HTTPBasicAuth
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles.finders import find

from irk.utils.grabber import proxy_requests

from irk.weather import settings as app_settings


logging.basicConfig(level=settings.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, **options):
        logger.info(u'Weather maps grabber started at %s' % datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))

        self._seismicity()
        # self._ice()
        # self._water()
        # self._baikal_level()

        logger.info(u'Weather maps grabber stopped at %s' % datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))

    def _temperature(self):
        """Температура"""

        logger.debug(u'Загрузка карты температур')

        now = datetime.datetime.now()
        if now.hour < 20:
            now -= datetime.timedelta(days=1)

        url = 'http://data.mapmakers.ru/clients/irkru/%s%02d%02d200000.RIRKRU.TTWP.png' % (now.year, now.month, now.day)

        try:
            response = proxy_requests.get(
                url, auth=HTTPBasicAuth(app_settings.WEATHER_MAPMAKERS_LOGIN, app_settings.WEATHER_MAPMAKERS_PASSWORD)
            )
            image = Image.open(StringIO.StringIO(response.content))
        except proxy_requests.RequestException:
            # HTTP 404
            return

        image = image.crop((56, 1, 586, 465))
        image.load()

        self._save(image, 1)

    def _ciclones(self):
        """Атмосферные фронты"""

        logger.debug(u'Загрузка карты атмосферных фронтов')

        now = datetime.datetime.now()
        if now.hour < 20:
            now -= datetime.timedelta(days=1)

        url = 'http://data.mapmakers.ru/clients/irkru/%s%02d%02d200000.RIRKRU.TCLFR.png' % (now.year, now.month, now.day)

        try:
            response = proxy_requests.get(
                url, auth=HTTPBasicAuth(app_settings.WEATHER_MAPMAKERS_LOGIN, app_settings.WEATHER_MAPMAKERS_PASSWORD)
            )
            image = Image.open(StringIO.StringIO(response.content))
        except proxy_requests.RequestException:
            # HTTP 404
            return

        image = image.crop((56, 1, 586, 465))
        image.load()

        self._save(image, 2)

    def _nebulosity(self):
        """Карта облачности"""

        logger.debug(u'Загрузка карты облачности')

        url1 = 'http://meteo.ucoz.ru/obl.gif'
        url2 = 'http://meteo.ucoz.ru/obl.jpg'

        try:
            image = Image.open(StringIO.StringIO(proxy_requests.get(url1).content))
        except proxy_requests.RequestException:
            try:
                image = Image.open(StringIO.StringIO(proxy_requests.get(url2).content))
            except proxy_requests.RequestException:
                logger.exception(u'Nebulosity map is not available')

                return False

        if image.mode == 'P':
            # gif в jpg
            image = image.convert('RGB')

        image = image.crop((0, 100, 620, 590))
        image.load()

        self._save(image, 3)

    def _seismicity(self):
        """Карта сеймичности"""

        logger.debug(u'Загрузка карты сейсмообстановки')

        url = 'http://www.seis-bykl.ru/pic.php'
        cookies = {
            'CHECK': '0',
        }

        try:
            image = Image.open(
                StringIO.StringIO(proxy_requests.get(url, cookies=cookies).content)
            )
        except (IOError, proxy_requests.RequestException) as e:
            logger.error(u'Seismicity loading error: %s' % e)
            return
        image = image.crop((45, 35, 667, 522))
        image.load()

        self._save(image, 4)

    def _ice(self):
        """Ледовая обстановка"""

        logger.debug(u'Загрузка карты ледовой обстановки')

        now = datetime.datetime.now()

        try:
            image = proxy_requests.get(now.strftime('http://www.geol.irk.ru/dzz/bpt/ice/%y%m%d/%y%m%d.jpg'))
            image.raise_for_status()
        except proxy_requests.RequestException:
            now -= datetime.timedelta(days=1)
            try:
                image = proxy_requests.get(now.strftime('http://www.geol.irk.ru/dzz/bpt/ice/%y%m%d/%y%m%d.jpg'))
                image.raise_for_status()
            except proxy_requests.RequestException:
                logger.debug(u'Нет карты ледовой обстановки')
                return

        try:
            image = Image.open(StringIO.StringIO(image.content))
        except IOError:
            logger.exception(u"Can't open image")
            return
        image = image.crop((460, 510, 2130, 2570))
        image.load()
        image.thumbnail((550, 678), Image.ANTIALIAS)

        self._save(image, 5)

    def _water(self):
        """Температура воды Байкала"""

        logger.debug(u'Загрузка температуры воды Байкала')

        content = StringIO.StringIO(proxy_requests.get('http://sputnik.irk.ru/alt/irk.ru/baikal_temp.tif').content)
        image = Image.open(content).convert('RGB')

        # Градиент для температуры воды, от холодного к теплому
        colors = [(42, 42, 64), (42, 48, 68), (43, 54, 73), (44, 62, 79), (45, 68, 84), (46, 75, 90), (46, 82, 95),
                  (47, 88, 100), (48, 96, 106), (49, 102, 110), (50, 109, 116), (51, 116, 121), (51, 122, 126),
                  (52, 130, 132), (53, 136, 137), (54, 143, 143), (55, 150, 148), (55, 156, 152), (56, 164, 158),
                  (57, 170, 163), (58, 177, 169), (59, 184, 174), (60, 190, 179), (61, 198, 185), (61, 204, 190),
                  (62, 211, 195), (63, 218, 200), (64, 224, 205), (65, 232, 211), (65, 238, 216), (66, 245, 222),
                  (67, 247, 223), (67, 247, 223), (67, 247, 223), (67, 247, 223), (67, 247, 223), (67, 247, 223),
                  (67, 247, 223), (67, 247, 223), (67, 247, 223)]

        image_data = image.getdata(0)
        used_values = set()
        data = []

        # У исходного изображения могут быть большие пустые поля по краям, делаем черно-белую копию изображения,
        # находим границы белых пикселей и обрезаем по их координатам с небольшим отступом
        diff = ImageChops.constant(image, '#000000')
        diff_data = [0 if r > 100 else 255 for r in image_data]
        diff.putdata(diff_data)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            offset = 50
            bbox = [
                bbox[0] - offset,
                bbox[1] - offset,
                bbox[2] + offset,
                bbox[3] + offset,
            ]
            image = image.crop(bbox)
            image.load()
            image_data = image.getdata(0)

        new = Image.new('RGB', image.size)

        land_color = (18, 23, 18)
        clouds_color = (239, 249, 250)
        for r in image_data:
            if r in (0, 100, 101):  # Суша и отсутствующие данные
                data.append(land_color)
            elif r in (102, 103):  # Облака
                data.append(clouds_color)
            elif r < 100:  # Вода
                try:
                    data.append(colors[r])
                    used_values.add(r)
                except IndexError:
                    data.append(colors[-1])
            else:
                data.append(land_color)

        new.putdata(data)

        new = new.filter(ImageFilter.SMOOTH_MORE)
        new.thumbnail((550, 678), Image.ANTIALIAS)

        legend = sorted(used_values, reverse=True)
        font = ImageFont.truetype(find('font/Roboto-Regular.ttf'), size=12)

        grouper = 7  # В легенде блоки группируются по 7 градусов

        draw = ImageDraw.Draw(new)
        height = (len(legend) / grouper + 5) * 20 + 15
        draw.rectangle((10, 10, 150, height), fill='#ffffff')

        for idx, i in enumerate(range(0, len(legend), grouper)):
            bits = sorted(legend[i:i +grouper])
            text = u'{}–{}°'.format(bits[0], bits[-1])
            color = colors[bits[-1]]
            top_left = 10 + 10 + (idx * 30)
            draw.rectangle((20, top_left, 60, top_left + 20), fill=color, outline='#737373')
            draw.text((75, top_left + 4), text, fill='#191919', font=font)

        top_left = 10 + 40 + ((len(legend) / grouper) * 30)
        draw.rectangle((20, top_left, 60, top_left + 20), fill='#ffffff', outline='#737373')
        draw.text((75, top_left + 4), u'облака', fill='#191919', font=font)

        self._save(new, 6)

    def _baikal_level(self):
        logger.debug(u'Загрузка графика уровня Байкала')

        try:
            image = proxy_requests.get('http://hydro.lin.irk.ru/php/files/rrd_image/rrd_listv_level_month.png')
            image = Image.open(StringIO.StringIO(image.content))
            image.thumbnail((740, 740), Image.ANTIALIAS)
            self._save(image, 7)
        except proxy_requests.RequestException:
            return

    def _save(self, image, id_):
        """Сохранение изображения и создание превью"""

        width = 90
        height = 70

        w = image.size[0]
        h = height*w/width

        thumb = image.copy()
        thumb.crop((0, image.size[1]/2 - h/2, w, h))
        thumb.thumbnail((width, height), Image.ANTIALIAS)

        # Рисуем черную рамку вокруг превью
        draw = ImageDraw.Draw(thumb)
        draw.rectangle((0, 0, thumb.size[0]-1, thumb.size[1]-1), outline='#000000', fill=None)
        del draw

        directory = os.path.join(settings.MEDIA_ROOT, 'img/weather/temp/')
        if not os.path.isdir(directory):
            os.makedirs(directory)

        image.save(os.path.join(directory, 'map_%s.jpg' % id_), 'jpeg')
        logger.debug('Image %s saved successfully' % id_)
        thumb.save(os.path.join(directory, 'map_%s_prev.jpg' % id_), 'jpeg')
        logger.debug('Image %s preview saved successfully' % id_)
