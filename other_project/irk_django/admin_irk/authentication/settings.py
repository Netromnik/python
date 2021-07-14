# -*- coding: utf-8 -*-

import re

# Регулярное выражение для валидиции логина пользователя
USERNAME_REGEXP = re.compile(ur'^(?:[\.\s\w-]*[\w]+[\.\s\w-]*){3,}$', re.UNICODE)

# Список слов (или частей слов), использование которых запрещено в логине при регистрации
DISALLOWED_USERNAME_PARTS = (
    'admin',
    'administrator',
    'irkru',
    'irk_ru',
    'redactor',
    'redaktor',
    'moderator',
)

# Время в днях, за которое можно успеть подтвердить изменение пароля
CONFIRM_PERIOD = 2

# Названия ключей, хранящих данные в сессии
CONFIRM_SESSION_KEY = '_auth_details'
PHONE_SESSION_KEY = '_auth_phone'
SOCIAL_SESSION_KEY = '_auth_social'
AVATAR_LOADING_TASK_SESSION_KEY = '_auth_avatar_task'
