# -*- coding: utf-8 -*-

import hashlib

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User


class PasswordBackend(ModelBackend):
    """Авторизация по логину/паролю

    В отличие от стандартной схемы django, у нас нет соли для паролей, просто sha1
    """

    def authenticate(self, username=None, password=None, **kwargs):
        kwargs = {
            'email' if '@' in username else 'username': username
        }
        try:
            user = User.objects.get(**kwargs)
        except User.DoesNotExist:
            return None

        try:
            # Пробуем новые хэшеров паролей сначала
            if user.check_password(password):
                return user
        except:
            pass

        try:
            hash_ = hashlib.sha1(password)
        except UnicodeEncodeError:
            return None

        if hash_.hexdigest() == user.password:
            new_password = make_password(password)
            User.objects.filter(id=user.id).update(password=new_password)
            user.password = new_password

            return user


class AnonymousAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        return None
