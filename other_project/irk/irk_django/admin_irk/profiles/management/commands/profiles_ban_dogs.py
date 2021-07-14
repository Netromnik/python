# -*- coding: utf-8 -*-

# Команда для блокировки профилей пользователей у которых удалены/закрыты все социальные профили.
# Facebook может возвращать 404 код для некоторых профилей если запрос идет от неавторизованного пользователя

from __future__ import unicode_literals

import logging
import threading
from Queue import Queue

from django.core.management.base import BaseCommand

from irk.authentication.helpers import deauth_users
from irk.utils.grabber import proxy_requests

from irk.profiles.models import Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = u'Блокировка аккаунтов по социальным профилям'

    def __init__(self):
        super(Command, self).__init__()

        self._queue = Queue(150)
        self._checkers = []
        self._concurrency = 100
        self._timeout = 5
        self._closed_users = set()
        self._lock = threading.Lock()

    def handle(self, **options):
        logger.debug('Start ban profiles by social profile')

        logger.debug('Running checkers')
        self._run_checkers()

        profiles = self._get_profiles()

        for profile in profiles:
            self._queue.put(profile)

        self._queue.join()

        deauth_users(self._closed_users)

        logger.info('Closed {} profiles'.format(len(self._closed_users)))
        logger.debug('Finish ban profiles by social profile')

    def _run_checkers(self):
        """Запустить пул чекеров"""

        for i in range(self._concurrency):
            t = threading.Thread(target=self._checker)
            t.daemon = True
            t.start()
            self._checkers.append(t)

    def _checker(self):
        """
        Метод-чекер профилей. Данные получает из очереди self._queue.

        У пользователя может быть несколько привязок к социальным сетям. Если все они закрыты/заблокированны, то
        пользователь блокируется.
        """

        while True:
            profile = self._queue.get()

            for social_profile in profile['social_profiles']:
                url = social_profile['url']
                logger.debug('Check {}'.format(url))
                try:
                    response = proxy_requests.get(url, timeout=self._timeout)
                except proxy_requests.RequestException as err:
                    logger.error('Request error: {}'.format(err))
                    continue

                logger.debug('{} for {}'.format(response.status_code, url))

                if response.status_code == 404:
                    social_profile['is_closed'] = True

            # Профиль закрывается, только если все социальные профили закрыты
            if all(sp['is_closed'] for sp in profile['social_profiles']):
                self._close(profile['user_id'])

            self._queue.task_done()

    def _get_profiles(self):
        """
        Генератор профилей для чекера.

        Каждый элемент содержит user_id и список с информацией о социальных профилях
        """

        profiles = Profile.objects \
            .filter(phone='', is_closed=False, is_banned=False, user__social_auth__isnull=False) \
            .select_related('user') \
            .distinct()

        for profile in profiles:
            # Для facebook пока есть ложные срабатывания, поэтому пропускаем профили у которых есть привязка к facebook
            if profile.user.social_auth.filter(provider='facebook').exists():
                continue

            user_id = profile.user_id
            social_profiles = []
            for social_profile in profile.user.social_auth.all():
                url = social_profile.extra_data.get('profile_url')
                if not url:
                    continue

                social_profiles.append({
                    'url': url,
                    'provider': social_profile.provider,
                    'is_closed': False,
                })

            if not social_profiles:
                continue

            yield {
                'user_id': user_id,
                'social_profiles': social_profiles,
            }

    def _close(self, user_id):
        """Закрыть профиль пользователя"""

        profile = Profile.objects.filter(user_id=user_id).select_related('user').first()
        if not profile:
            logger.error('Not found profile for user {}'.format(user_id))

        profile.is_closed = True
        profile.save(update_fields=['is_closed'])
        profile.user.is_active = False
        profile.user.save(update_fields=['is_active'])

        with self._lock:
            self._closed_users.add(user_id)

        logger.info('Closed profile for user {}'.format(user_id))
