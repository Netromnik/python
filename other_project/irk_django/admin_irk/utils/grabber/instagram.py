# -*- coding: utf-8 -*-

import os.path

from django.conf import settings
from django.utils.text import Truncator

from irk.externals.management.grabbers.instagram import highpoints
from irk.utils.grabber import proxy_requests


def load_media_by_hashtag(name, latest_photo_id=None, text_truncate_size=None):
    """Загрузка последних изображений с указанным хэштегом

    Параметры::
        name : название хэштега
        latest_photo_id : идентификатор последнего загруженного изображения, чтобы загружать только новые картинки
        text_truncate_size : сколько символов оставить у описания изображения. Если не указан, текст не обрезается

    Примеры::
        >>> load_media_by_hashtag('#irkutsk')

        >>> load_media_by_hashtag('#irkutsk', latest_photo_id=123456)

        # Например, описание сохраняется в VARCHAR(255)
        >>> load_media_by_hashtag('#irkutsk', text_truncate_size=255)

    """

    name = name.strip().lstrip('#')

    params = {
        'client_id': settings.INSTAGRAM_CLIENT_ID
    }
    if latest_photo_id:
        params['max_id'] = latest_photo_id

    url = u'https://api.instagram.com/v1/tags/{}/media/recent'.format(name)
    response = proxy_requests.get(url, params=params).json()

    for obj in response.get('data', []):
        if obj['type'] != 'image':
            continue  # Пропускаем видео

        image_url = obj['images']['standard_resolution']['url']
        id = obj['id']
        username = obj['user']['username']
        if obj['caption']:
            title = highpoints.sub(u'\u25FD', obj['caption']['text'])
            if text_truncate_size:
                truncator = Truncator(title)
                title = truncator.chars(text_truncate_size)
            else:
                title = obj['caption']
        else:
            title = ''

        image = proxy_requests.get(image_url).content

        yield {
            'id': id,
            'username': username,
            'title': title,
            'image': {
                'content': image,
                'name': os.path.basename(image_url),
            },
        }
