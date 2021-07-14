# -*- coding: utf-8 -*-

"""
Модуль содержит классы для размещения записей в социальных сетях (ВКонтакте, Facebook, Twitter).
"""

import json
import logging
import facebook
import twitter
import vk
import requests
from odnoklassniki import Odnoklassniki

from django.conf import settings


logger = logging.getLogger(__name__)


class SocialPosterError(Exception):
    pass


class PostingResult(object):
    """
    Обертка для результата постинга

    Разные постеры возвращают ответ в разном формате. Этот класс дает возможность
    унифицировать получение URL на опубликованную запись из любого постера.

    См: _wrap_result в конкретном постере

    Например:
        result = TwitterPoster.post(material)
        result_tw.url()  # вернет http://twitter.com/xxxx

        result = FacebookPoster.post(material)
        result_fb.url()  # вернет http://fb.com/xxxx
    """
    def __init__(self, result):
        self.original_result = result

    def __repr__(self):
        return '{}(result={!r})'.format(self.__class__.__name__, self.original_result)

    def url(self):
        """Возвращает ссылку на опубликованный пост"""
        raise NotImplementedError

    def as_string(self):
        """Возвращает сериализованный ответ для сохранения в БД"""
        return json.dumps(self.original_result)


class SocialPoster(object):
    """Постер материалов в социальных сетях"""

    name = ''

    def __init__(self):
        self._init_api()

    def post(self, material, data=None):
        """Разместить ссылку на материал"""

        try:
            result = self._post(material, data)
        except Exception as err:
            # вот тут что плохо, что теряется traceback внутренней ошибки
            logger.exception('Exception while posting')
            raise SocialPosterError(u'{} api error: {}'.format(self.name, err))

        result = self._wrap_result(result)
        return result

    def link(self, material):
        """Сформировать ссылку"""
        return u'{}www.irk.ru{}'.format(settings.SITE_SCHEMA, material.get_absolute_url())

    def _wrap_result(self, result):
        """Заворачивает ответ от постера в экземпляр класса PostingResult"""

        raise NotImplementedError

    def refresh_cache(self, material):
        """Сбросить кэш социальной сети"""

        raise NotImplementedError

    def _init_api(self):
        """Получить доступ к api"""

        raise NotImplementedError

    def _post(self, material, data=None):
        """Разместить материал в социальной сети."""

        raise NotImplementedError


class VKontaktePoster(SocialPoster):
    """
    Постер в социальную сеть ВКонтакте

    Для работы постера требуется access_token с разрешениями offline,wall
    (см. https://vk.com/dev/permissions)
    """

    name = 'vkontakte'

    def _upload_photo(self):
        """Загружает фотографию в альбом стены и возвращает attachments для wall.post"""
        result = []

    def _post(self, material, data=None):
        if data:  # из соцпульта
            VK_GROUP_ID = settings.VK_GROUP_ID
            wall_params = {
                'owner_id': VK_GROUP_ID,
                'from_group': 1,
                'message': u'{}\n{}'.format(data['text'], data['link']),
                'attachments': [],
            }

            if 'images' in data and data['images']:
                # получаем адрес сервера для загрузки
                response = self._api.photos.getWallUploadServer(group_id=abs(VK_GROUP_ID))
                upload_url = response['upload_url']

                # загружаем
                image_path = data['images'][0]
                with open(image_path, 'rb') as f:
                    files = {'photo': f}
                    response = requests.post(upload_url, files=files).json()

                # сохраняем
                save_params = {
                    'group_id': abs(VK_GROUP_ID),  # в настройках группа с минусом хранится
                    'photo': response['photo'],
                    'server': response['server'],
                    'hash': response['hash'],
                    # 'caption': u'Какой-то кэпшн.',
                }
                response = self._api.photos.saveWallPhoto(**save_params)[0]

                wall_params['attachments'].append(
                    'photo{}_{}'.format(response['owner_id'], response['id'])
                )

            # ссылку не аттачим - с фото вместе стремно выглядит
            # wall_params['attachments'].append(data['link'])

            ','.join(wall_params['attachments'])
            response = self._api.wall.post(**wall_params)
            return response
        else:  # кнопка в админке
            # описание параметров метода https://vk.com/dev/wall.post
            result = self._api.wall.post(
                owner_id=settings.VK_GROUP_ID,
                from_group=1,
                attachments=u'{}www.irk.ru{}'.format(settings.SITE_SCHEMA, material.get_absolute_url())
            )

            return result

    def _init_api(self):
        session = vk.Session(settings.VK_ACCESS_TOKEN)
        self._api = vk.API(session, v='5.50')

    def refresh_cache(self, material):
        url = material.get_absolute_url_with_domain()
        self._api.pages.clearCache(url=url)

    def _wrap_result(self, result):
        return VkontaktePostingResult(result)


class VkontaktePostingResult(PostingResult):
    def url(self):
        return 'https://vk.com/wall{gid}_{pid}'.format(
            gid=settings.VK_GROUP_ID,
            pid=self.original_result['post_id']
        )
        return 'https://vk.com/{}'.format(self.original_result)

class TwitterPoster(SocialPoster):
    """Постер в сервис микроблогов Twitter"""

    name = 'twitter'

    def _post(self, material, data=None):
        logger.info('Twitter post Data: %r', data)

        if data:  # из соцпульта
            status = u'{}\n{}'.format(data['text'], data['link'])
            images = data['images']
        else:  # кнопка в админке материала
            status = u'{}\n{}'.format(material.title, self.link(material))
            images = material.social_card.file

        result = self._api.PostUpdate(status, media=images)
        class resultdumb:
            id_str = 'SOMEURL'

        return result

    def _wrap_result(self, result):
        return TwitterPostingResult(result)

    def _init_api(self):
        self._api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

class TwitterPostingResult(PostingResult):
    def url(self):
        return 'https://twitter.com/tvoyirkutsk/status/{}'.format(self.original_result.id_str)

    def as_string(self):
        """
        Библиотека python-twitter возвращает модель Status в качестве ответа. Ее
        нельзя сериализовать в джейсон, поэтому она хратися в базе как строка repr().
        Этого достаточно для логирования.
        """
        return repr(self.original_result)


class FacebookPoster(SocialPoster):
    """Постер в социальную сеть Facebook"""

    name = 'facebook'

    def _post(self, material, data=None):
        logger.info("Facebook posting data: %r" % data)
        if data['image_urls']:  # через соцпульт с фоткой
            kwargs = {
                'link': data['link'],
                'message': u'{}'.format(data['text']),
                'picture': data['image_urls'][0],
            }
            result = self._api.put_object(settings.FACEBOOK_PAGE_ID, 'feed', **kwargs)
        elif  data:  # без фотки
            kwargs = {
                'message': u'{}\n{}'.format(data['text'],data['link']),
            }
            result = self._api.put_object(settings.FACEBOOK_PAGE_ID, 'feed', **kwargs)
        else:  # вручную
            result = self._api.put_wall_post(
                profile_id=settings.FB_PROFILE_ID,
                message='',
                attachment={
                    'link': u'{}www.irk.ru{}'.format(settings.SITE_SCHEMA, material.get_absolute_url()).encode('utf-8')
                },
            )

        return result

    def _wrap_result(self, result):
        return FacebookPostingResult(result)

    def _init_api(self):
        self._api = facebook.GraphAPI(access_token=settings.FACEBOOK_PAGE_ACCESS_TOKEN, version='3.1')

    def refresh_cache(self, material):
        params = {
            'scrape': True,
            'id': material.get_absolute_url_with_domain(),
        }
        self._api.request('', args=params, method='POST')


class FacebookPostingResult(PostingResult):
    def url(self):
        return 'https://fb.com/{}'.format(self.original_result['id'])


class OdnoklassnikiPoster(SocialPoster):
    """Постер социальной сети Одноклассники"""

    name = 'odnoklassniki'

    def _init_api(self):
        key = settings.ODNOKLASSNIKI_APPLICATION_KEY
        secret = settings.ODNOKLASSNIKI_APPLICATION_SECRET
        token = settings.ODNOKLASSNIKI_TOKEN

        self._api = Odnoklassniki(key, secret, token)

    def _post(self, material, data):

        logger.info('Start posting to ok.ru. Data: %r', data)

        # текстовая составляющая
        post_data = {
            'media': [
                {
                    'type': 'text',
                    'text': u'{}\n{}'.format(data['text'], data['link']),
                },
            ]
        }

        # картинка
        if data.get('images'):
            media_photo = {
                'type': 'photo',
                'list': [],
            }

            response = self._api.photosV2.getUploadUrl(gid=settings.ODNOKLASSNIKI_GROUP_ID)
            upload_url = response['upload_url']

            with open(data['images'][0],'rb') as f:
                response = requests.post(upload_url, files={'pic1': f})

            for details in response.json()['photos'].values():
                media_photo['list'].append({
                    'id': details['token']
                })


            if media_photo['list']:
                post_data['media'].append(media_photo)

        # создаем сообщение
        result = self._api.mediatopic.post(type='GROUP_THEME', gid=settings.ODNOKLASSNIKI_GROUP_ID,
                                           attachment=json.dumps(post_data))
        return result

    def _wrap_result(self, result):
        return OdnoklassnikiPostingResult(result)


class OdnoklassnikiPostingResult(PostingResult):
    def url(self):
        return 'https://ok.ru/group/{gid}/topic/{tid}'.format(
            gid=settings.ODNOKLASSNIKI_GROUP_ID,
            tid=self.original_result
        )


POSTER_MAP = {
    'vk': VKontaktePoster,
    'vkontakte': VKontaktePoster,
    'facebook': FacebookPoster,
    'twitter': TwitterPoster,
    'odnoklassniki': OdnoklassnikiPoster,
}


def get_poster_by_name(alias):
    """Получить постер по имени"""

    poster_class = POSTER_MAP.get(alias)
    if not poster_class:
        raise SocialPosterError('Not found poster {}'.format(alias))

    return poster_class()
