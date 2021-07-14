# -*- coding: utf-8 -*-

import collections
import hashlib
import logging

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import pylibmc as memcache
except ImportError:
    import memcache

from django import template
from django.utils.http import urlquote
from django.db.models.query import QuerySet

from irk.utils.cache import model_cache_key, is_cacheable, TagCache


register = template.Library()
logger = logging.getLogger(__name__)


class CacheNode(template.Node):
    def __init__(self, nodelist, expire, key, vary_on, tags, disable):
        self.nodelist = nodelist
        self.expire = template.Variable(expire)
        self.key = key
        self.vary_on = vary_on
        self.tags = tags
        self.disable = disable

    def render(self, context):
        try:
            expire = int(self.expire.resolve(context))
        except template.VariableDoesNotExist:
            raise template.TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.expire.var)
        except (ValueError, TypeError):
            raise template.TemplateSyntaxError('"cache" tag got a non-integer timeout value: %r' % self.expire.var)

        # Build a unicode key for this fragment and all vary-on's.
        args = []
        for var in self.vary_on:
            try:
                args.append(urlquote(template.Variable(var).resolve(context)))
            except template.VariableDoesNotExist:
                # Если переменной нет в контексте, добавляем пустую строку,
                args.append(u'')
        args = hashlib.md5(u':'.join(args))

        tags = []
        for tag in self.tags:
            try:
                # Пытаемся достать из шаблона значение переменной
                obj = template.Variable(tag).resolve(context)
                if not isinstance(obj, collections.Hashable) or isinstance(obj, (dict, list, tuple, QuerySet,)):
                    # В шаблонах имена тегов могут совпадать с переменными, находящимися в шаблонах
                    # Чтобы исключить возможность попадания не hashable объектов в теги, делаем эту проверку
                    raise ValueError()

                # Объект не должен попадать в кэш, рендерим HTML
                if not is_cacheable(obj):
                    logger.debug(u'Object is non cacheable. Rendering HTML.')
                    return self.nodelist.render(context)
                tags.append(model_cache_key(obj))
            except (template.VariableDoesNotExist, ValueError):
                # Иначе это просто текст
                tags.append(tag)

        # Базовый ключ кэша может быть переменной
        try:
            key = template.Variable(self.key).resolve(context)
        except template.VariableDoesNotExist:
            key = self.key

        # Параметр отключения кэша
        if self.disable:
            disable = template.Variable(self.disable).resolve(context)
            if disable:
                return unicode(self.nodelist.render(context))

        cache_key = 'template.cache.%s.%s' % (key, args.hexdigest())

        with TagCache(cache_key, expire, tags) as tag_cache:
            value = tag_cache.value
            if value is tag_cache.EMPTY:
                value = unicode(self.nodelist.render(context))
                tag_cache.value = value

            return value


@register.tag('cache')
def do_cache(parser, token):
    """Кэширование части шаблона

    Использование::

        {% load cache_tags %}
        {% cache expire_time key_name %}
            .. some expensive processing ..
        {% endcache %}

    Дополнительные параметры:

    vary - формирование уникального ключа на основе переменных контекста::

        {% load cache_tags %}
        {% cache expire_time key vary="request.csite.site.pk,site_index,site_inner" %}
            .. some expensive processing ..
        {% endcache %}

    tags - формирование кэша, который инвалидируется при изменении определенных объектов::
    
        {% load cache_tags %}
        {% cache expire_time key tags="news,event" %}
            .. some expensive processing ..
        {% endcache %}
    
        При сохранении любого из этих элементов, кэш, имеющий соотвествующий тег будет считаться невалидным.

    disable (bool) - принудительное отключения кэша::

        {% load cache_tags %}
        {% cache expire_time key disable=True %}
            .. some expensive processing ..
        {% endcache %}

    Остальные параметры работают как и в стандартном теге cache, но желательно их не использовать!
    """

    nodelist = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    expire, key = tokens[1:3]
    tokens = tokens[3:]
    vary = []
    tags = []
    disable = False
    for token in tokens:
        if token.startswith('tags='):
            # Список тегов
            tags += [x.strip() for x in token[5:].strip('"').strip("'").split(',')]
        elif token.startswith('vary='):
            # Новый формат записи переменных контекста
            vary += [x.strip() for x in token[5:].strip('"').strip("'").split(',')]
        elif token.startswith('disable='):
            disable = token[8:]
        else:
            # Совместимость с оригинальным шаблонным тегом cache
            vary.append(token)

    return CacheNode(nodelist, expire, key, vary, tags, disable)
