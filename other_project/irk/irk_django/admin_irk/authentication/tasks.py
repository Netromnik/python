# -*- coding: utf-8 -*-

import logging
import os

from django.core.files.base import ContentFile
from social_django.models import UserSocialAuth

from irk.profiles.models import Profile
from irk.utils.grabber import proxy_requests
from irk.utils.tasks.helpers import task

logger = logging.getLogger(__name__)


@task(ignore_result=False)
def load_user_avatar(user_id, avatar_url):
    """Загрузка аватара для пользователя

    Параметры::
        user_id : идентификатор пользователя
        avatar_url : адрес изображения с аватаром
    """

    profile = Profile.objects.get(user_id=user_id)
    if UserSocialAuth.objects.filter(user=profile.user).count() > 1:
        # Нам нужно загружать аватарку только в том случае, если пользователь впервые привязывает соцсеть
        # К этому моменту одна запись в UserSocialAuth уже есть
        logger.debug('Skip avatar loading for user #{0}, cause he is already have it'.format(user_id))
        return

    if profile.image and os.path.exists(profile.image.path):
        os.remove(profile.image.path)

    response = proxy_requests.get(avatar_url)
    try:
        response.raise_for_status()
    except proxy_requests.HTTPError:
        logger.exception('Cant load avatar from URL {0} for user #{1}'.format(avatar_url, user_id))

    profile.image.save('{0}.jpg'.format(profile.user_id), ContentFile(response.content))

    logger.debug('Saved avatar from URL {0} for user #{1}'.format(avatar_url, user_id))
