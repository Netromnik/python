# -*- coding: utf-8 -*-

import hashlib
import logging
import string

import redis
from PIL import Image, ImageDraw
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.encoding import smart_str
from redis_sessions.session import SessionStore
from social_django.models import UserSocialAuth

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

logger = logging.getLogger(__name__)


def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').

    Так как в django>=1.4 убран этот метод, копируем его себе, чтобы поддерживать старый механизм авторизации.
    Раньше метод находился в `django.contrib.auth.models`
    """

    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return hashlib.md5(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def hash_password(raw_password):
    """Хэширование пароля пользователя

    Для хэширования паролей у нас используется sha1 без соли"""

    return str(get_hexdigest('sha1', '', raw_password))


def is_social_user(user):
    """Проверка, зарегистрирован пользователь через социальные сети или нет"""

    if user.is_anonymous:
        return False

    if not hasattr(user, 'is_social_user'):
        result = UserSocialAuth.objects.filter(user=user).exists()
        user.is_social_user = result

    return user.is_social_user


IDENTICON_COLORS = (
    '#78D676',
    '#67C6C0',
    '#C4E491',
    '#DE6CDE',
    '#D882A7',
    '#455ED5',
    '#9CC4DD',
    '#E2B795',
    '#6E56C8',
    '#D4BC4E',
    '#CBA662',
    '#60C579',
    '#8296DB',
    '#CA96E9',
    '#60C579',
    '#61402B',
)


def generate_identicon(user_id, size=(100, 100), offset=5):
    hash_ = hashlib.md5(str(user_id)).digest()
    letter = hex(ord(hash_[15].lower()))[-1]
    color = IDENTICON_COLORS[string.hexdigits[:16].index(letter)]
    bits = [ord(x) % 2 == 1 for x in hash_[:15]]
    matrix = [bits[i:i + 3] for i in range(0, len(bits), 3)]

    for i in matrix:
        i.append(i[1])
        i.append(i[0])

    width, height = size
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    bg_color = '#ECECEC'
    draw.rectangle([0, 0, width, height], bg_color)

    step = (width - offset * 2) / 5  # Размер каждого "пикселя" на аватаре
    x0, y0 = offset, offset

    for y, axis in enumerate(matrix):
        for x, value in enumerate(axis):
            draw.rectangle([x0 + x * step, y0 + y * step, x0 + x * step + step - 1, y0 + y * step + step - 1],
                           color if value else bg_color)

    out = StringIO()
    image.save(out, format='png')

    return out


def avatar_resize(tempfile):
    """
    Превращает фото в квадрат и уменьшет до размера 50x50 пикселей

    Параметры::
        image : fp
    """

    width, height = tempfile.size

    # Если фото горизонтальное - берем квадрат из центра
    if width > height:
        diff = width - height
        tempfile = tempfile.crop((int(diff / 2), 0, int(diff / 2) + height, height))
    # Если фото вертикальное - берем квадрат из верхней части
    elif width < height:
        tempfile = tempfile.crop((0, 0, width, width))

    tempfile = tempfile.resize((100, 100), Image.ANTIALIAS)
    tempfile_io = StringIO()
    tempfile.save(tempfile_io, format='JPEG')
    tempfile_io.seek(0, 2)
    size = tempfile_io.tell()
    return InMemoryUploadedFile(tempfile_io, None, 'temp.jpg', 'image/jpeg', size, None)


def deauth_users(user_ids):
    """
    Деавторизация пользователей.

    Для деавторизации просто удаляется сессия.
    """

    if settings.SESSION_ENGINE != 'redis_sessions.session':
        logger.error('deauth_users works only with redis_sessions backend')
        return

    user_ids = [int(x) for x in user_ids]
    connection = redis.StrictRedis(
        host=getattr(settings, 'SESSION_REDIS_HOST', 'localhost'),
        db=getattr(settings, 'SESSION_REDIS_DB', 0),
    )

    decoder = SessionStore()
    for key in connection.scan_iter():
        if len(key) != 32:
            continue

        user_id = decoder.decode(connection.get(key)).get('_auth_user_id')
        if user_id and user_id in user_ids:
            connection.delete(key)
            logger.debug('Removing session for user {0}'.format(user_id))
