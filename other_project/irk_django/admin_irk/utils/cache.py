# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time
import logging

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import pylibmc as memcache
except ImportError:
    import memcache

from django.apps import apps
from django.db.models import Model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache as core_cache
from django.utils.encoding import smart_str

from utils.settings import CACHE_TAG_LIFETIME, CACHE_TAG_PREFIX


logger = logging.getLogger(__name__)

# Словарь колбэков, импортируемых в `is_cacheable`
__cacheable_callbacks = {}


def model_cache_key(instance):
    """Ключ кэширования для объекта модели"""

    if isinstance(instance, Model):
        from irk.news.models import BaseMaterial
        try:
            if issubclass(instance.__class__, BaseMaterial):
                ct = ContentType.objects.get_for_model(BaseMaterial)
            else:
                ct = ContentType.objects.get_for_model(instance)
            return '%s.%s.%s' % (ct.app_label, ct.model, instance.pk)
        except ContentType.DoesNotExist:
            return instance

    return instance


def invalidate_tags(tags=()):
    """Инвалидация тегов"""

    value = time.time()
    for tag in tags:
        key = CACHE_TAG_PREFIX % tag
        logger.debug('Updating cache tag %s value to %s' % (key, value))
        core_cache.set(key, value, CACHE_TAG_LIFETIME)


def is_cacheable(obj):
    """Объект можно помещать в кэш"""

    if isinstance(obj, Model):
        try:
            ct = ContentType.objects.get_for_model(obj)
        except ContentType.DoesNotExist:
            return True

        if not ct.app_label in __cacheable_callbacks:

            try:
                app_module = __import__('%s.cache' % ct.app_label, fromlist=['validate'])
            except ImportError:
                __cacheable_callbacks[ct.app_label] = None
            else:
                __cacheable_callbacks[ct.app_label] = getattr(app_module, 'validate', None)

        callback = __cacheable_callbacks[ct.app_label]
        if callback is not None:
            return callback(obj)

    return True


class TagCache(object):
    """Кэш объектов Python с использованием тегов для инвалидации значения

    Пример использования::
        with TagCache('cache-key', 3600, tags=('news', 'afisha')) as tag_cache:
            value = tag_cache.value
            if value is tag_cache.EMPTY:
                value = News.objects.all()
                tag_cache.value = value

        print value
    """

    EMPTY = object()

    def __init__(self, key, expire, tags=()):
        self.key = key
        self.expire = expire
        self.tags = [CACHE_TAG_PREFIX % tag for tag in tags]

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def _get_value(self):
        """Получаем значение ключа и инвалидируем его с помощью тегов"""

        value = core_cache.get(self.key, self.EMPTY)
        if value is self.EMPTY:
            logger.debug('Cache have no value for key "%s"' % self.key)
            return self.EMPTY

        try:
            # надо бы при случае заменить pickle на json, как более безопасный
            value, tags = pickle.loads(smart_str(value))
        except pickle.UnpicklingError:
            msg = 'Can not unpickle key "%s", data length is %d'
            logger.exception(msg, self.key, len(value))
            return self.EMPTY

        tag_values = {}
        for tag in tags.keys():
            v = core_cache.get(tag)
            if v is not None:
                tag_values[tag] = v

        for tag in self.tags:
            if not tag in tag_values:
                logger.debug('Non-existing tag: %s. Returning empty value' % tag)
                return self.EMPTY

            if tags.get(tag, 0) < tag_values.get(tag, 1):
                logger.debug('Tag "%s" version had expired' % tag)
                return self.EMPTY

        return value

    def _set_value(self, value):
        tags = {}
        for tag in self.tags:
            version = core_cache.get(tag)
            if version is None:
                version = time.time()
                core_cache.set(tag, version, CACHE_TAG_LIFETIME)
            tags[tag] = version

        try:
            logger.debug(
                'Updating cache for key "%s", expires in %ss, tags "%s"' %
                (self.key, self.expire, ', '.join([str(x) for x in self.tags]))
            )
            core_cache.set(self.key, pickle.dumps((smart_str(value), tags)), self.expire)
        except memcache.Error as e:
            if 'ITEM TOO BIG' not in e.message:
                raise

    value = property(_get_value, _set_value)


# Кэш инвалидаторов кэша для каждого приложения.
# Импортируется `app_name.cache.invalidate` и сохраняется здесь
# Ключ - название приложения, строка
# Значение - функция-инвалидатор
_APP_CACHE_INVALIDATORS = {}

# Список наследников-моделей для каждой из моделей
# Ключ - идентификатор ContentType модели
# Значение - список с классами моделей-наследников
_APP_MODEL_SUCCESSORS = {}


def invalidate_cache_for_object(obj):
    """Вызов инвалидации кэша из приложения, в котором находится модель `obj`
    Кроме этого, будут вызваны инвалидаторы кэша из приложений, в которых находятся наследники от модели.

    Пример использования::
        >>> from irk.phones.models import Firms
        >>> firm = Firms.objects.get(id=1)
        >>> invalidate_cache_for_object(firm)

        Будет вызвана функция `phones.cache.invalidate`, которой будет передан объект `firm`.
    """

    # Список приложений, для которых будет вызвана инвалидация кэша
    app_labels = []

    ct = ContentType.objects.get_for_model(obj)
    model_cls = ct.model_class()
    app_labels.append(ct.app_label)

    if not ct.id in _APP_MODEL_SUCCESSORS:
        logger.debug('Loading model successors for model %s.%s' % (ct.app_label, ct.model))

        # TODO: нормальная инвалидация кэша для моделей-наследников
        if ct.app_label == 'phones' and ct.model == 'firms':
            from irk.phones.helpers import firms_library

            _APP_MODEL_SUCCESSORS[ct.id] = firms_library.copy()

        else:
            model_successors = []
            for model in apps.get_models():
                if issubclass(model_cls, model) and model_cls != model:
                    logger.debug('Got an model successor for model %s.%s: %s' % (ct.app_label, ct.model, model))
                    model_successors.append(model)

            _APP_MODEL_SUCCESSORS[ct.id] = set(model_successors)

    for model_cls in _APP_MODEL_SUCCESSORS[ct.id]:
        model_ct = ContentType.objects.get_for_model(model_cls)
        app_labels.append(model_ct.app_label)

    logger.debug('Invalidating cache for those irk: %s' % ', '.join(app_labels))

    for app in app_labels:
        if app not in _APP_CACHE_INVALIDATORS:
            logger.debug('Importing cache invalidator for app `%s`' % app)
            try:
                app_module = __import__('%s.cache' % app, fromlist=['invalidate'])
            except ImportError:
                _APP_CACHE_INVALIDATORS[app] = None
                return
            else:
                if hasattr(app_module, 'invalidate'):
                    _APP_CACHE_INVALIDATORS[app] = app_module.invalidate

        invalidator = _APP_CACHE_INVALIDATORS.get(app)
        if invalidator is not None:
            logger.debug('Invalidating cache for model %s.%s' % (app, ct.model))
            invalidator(sender=model_cls, instance=obj)
        else:
            logger.debug('Cache validator for app %s is unavailable' % app)
