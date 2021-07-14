# -*- coding: utf-8 -*-

import os
import re
import zlib
from urllib.parse import parse_qs, urlparse

# import hexagonit.swfheader
from django.conf import settings
from requests.models import PreparedRequest

from adv.models import Banner, File
from utils.files import generate_file_name

IMAGE_FIELDS = ('main', 'dummy', 'bgimage', 'bgimage2')


def debug_places(place):
    """Рендер блоков для отображения отладочной информации о баннерах"""

    from adv.models import Place
    def size(text):
        match = re.findall(r'(\d+)[xXхХ](\d+)', text)
        if match:
            return match[0]
        else:
            return None

    content = '<div class="banner-debug-block" style="clear:both;text-align:center">'
    if not isinstance(place, Place):
        try:
            place = Place.objects.get(pk=place)
        except Place.DoesNotExist:
            return u'Нет баннерного места %s' % place

    place_size = size(place.name)
    if place_size:
        content += u'<div style="display:inline-block;width:%(width)spx;height:%(height)spx;border:3px dashed #ccc;margin:0 auto;text-align:center;vertical-align:middle;line-height:%(height)spx;font-size:16px;color:#999;font-weight:bold;opacity:0.5">%(content)s</div>' % \
                   {'width': int(place_size[0]) - 6, 'height': int(place_size[1]) - 6, 'content': place.pk}
    else:
        content += u'<div style="display:inline-block;padding:5px;border:3px dashed #ccc;margin:0 auto;text-align:center;vertical-align:middle;font-size:16px;color:#999;font-weight:bold;opacity:0.5">%s</div>' % place.pk

    content += '</div>'

    return content


def copy_file(item):
    if item[0] not in IMAGE_FIELDS or not item[1]:
        return item

    file_path = "%s/%s" % (settings.MEDIA_ROOT, item[1])
    if os.path.exists(file_path):
        file = open(file_path)
        file_data = item[1].split("/")
        new_name = generate_file_name(None, file_data.pop())
        new_name = "%s/%s" % ("/".join(file_data), new_name)
        new_file = open("%s/%s" % (settings.MEDIA_ROOT, new_name), "w+")
        new_file.write(file.read())
        new_file.close()
        file.close()
        return (item[0], new_name)
    return (item[0], None)


def models_attrs(item):
    """Фильтруем ненужные поля модели"""
    return item[0] != 'id' and not item[0].startswith('_')


def banner_duplicate(banner):
    data = dict(filter(models_attrs, banner.__dict__.copy().items()))
    new_banner = Banner.objects.create(**data)
    # Файлы баннера
    files = [dict(filter(models_attrs, location.__dict__.copy().items())) for location in banner.file_set.all()]
    map(lambda x: x.update({'banner_id': new_banner.id}), files)
    files = map(lambda x: dict(map(copy_file, x.items())), files)
    files = filter(lambda f:
                   filter(lambda i: i[0] in IMAGE_FIELDS and i[1], f.items())
                   , files)
    map(lambda x: File.objects.create(**dict(map(copy_file, x.items()))), files)
    # Места баннера
    map(lambda x: new_banner.places.add(x), banner.places.all())
    return new_banner


def file_get_info(file):
    """Возвращает все возможную информацию про баннер"""

    info = {}
    #  !TODO: Нужен ли flash ?
    # if file.content_type == 'application/x-shockwave-flash':
    #     try:
    #         info = hexagonit.swfheader.parse(file)
    #     except (zlib.error, ValueError):
    #         return {'error': u'Ошибка в файле'}

        # info['type'] = 'Flash v%s' % info['version']
    # else:
    #     return {'name': u'Проверка только для flash файлов'}

    # info['kb'] = "%.2f" % (float(file.size) / 1024)
    #
    # info['name'] = file.name

    return info


def add_utm(url, banner, content=''):
    """Добавляет UTM-метки к адресу баннера"""
    if 'utm_source' in url:
        return url

    params = {
        'utm_source': 'irkru',
        'utm_medium': 'banner',
    }

    if banner and banner.id:
        params['utm_campaign'] = 'banner-{}'.format(banner.id)

    if content:
        params['utm_content'] = content

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)

    req = PreparedRequest()

    req.prepare_url(url, dict(params.items() + query.items()))
    return req.url
