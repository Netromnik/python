# -*- coding: utf-8 -*-

import re
import os.path

from django.conf import settings
from django.utils.text import Truncator

from irk.utils.grabber import proxy_requests

from irk.externals.models import InstagramTag

# Вырезаем 4-байтные символы из строк, которые могут попасться в текстах инстаграма,
# так как мы не можем сохранить их в mysql
try:
    # UCS-4
    highpoints = re.compile(u'[\U00010000-\U0010ffff]')
except re.error:
    # UCS-2
    highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')


def load_media_by_hashtag(name, latest_photo_id=None):
    """Загрузка последних изображений с указанным хэштегом

    Параметры::
        name : название хэштега
        latest_photo_id : идентификатор последнего загруженного изображения, чтобы загружать только новые картинки

    Примеры::
        >>> load_media_by_hashtag('#irkutsk')

        >>> load_media_by_hashtag('#irkutsk', latest_photo_id=123456)

    """

    name = name.strip().lstrip('#')

    # Проверка на ограничение по типу контента для тега
    try:
        instagram_tag = InstagramTag.objects.get(name=name)
    except InstagramTag.DoesNotExist:
        media_type = None
    else:
        if instagram_tag.type == InstagramTag.IMAGE:
            media_type = 'image'
        elif instagram_tag.type == InstagramTag.VIDEO:
            media_type = 'video'
        else:
            media_type = None

    params = {
        'client_id': settings.INSTAGRAM_CLIENT_ID
    }
    if latest_photo_id:
        params['next_max_tag_id'] = latest_photo_id

    url = u'https://api.instagram.com/v1/tags/{}/media/recent'.format(name)
    response = proxy_requests.get(url, params=params).json()

    for obj in response.get('data', []):
        if media_type and obj['type'] != media_type:
            continue

        yield obj
