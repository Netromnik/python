# -*- coding: utf-8 -*-

"""Конфигурация ссылок для новостей

Потому что логика очень сложная
"""

import logging

from django.core.urlresolvers import reverse, NoReverseMatch


logger = logging.getLogger(__name__)


def afisha_article(obj):
    """Ссылки заголовков в статье афиши"""

    if obj.type.slug == 'review':
        # Рецензии афиши остаются в афише
        return reverse('afisha:review:index')

    return reverse('news:article:index')

# Заголовки тега {% news_sidebar_block %} могут вести на какие-нибудь другие разделы.
# Задаем здесь, откуда и куда должны вести заголовки
# Формат ключа: `site_slug.model_name`, например `afisha.article`
# Формат значения: ссылка, например `news:article:index`
# Это значит, что заголовок статьи в Афише будет вести на статьи в Новостях
# Значение может быть callable, ему передается объект, для которого создается ссылка
SIDEBAR_TITLE_URL_MAPPINGS = {
    'afisha.article': afisha_article,
}


def get_index_url(site, obj):
    """Ссылка на список объектов, например на индекс статей в Обеде

    Параметры::
        site: Текущий раздел сайта, обычно берется `request.csite`
        obj: Объект, на основе которого генерируется ссылка, наследник от `news.BaseMaterial`
    """

    model_name = obj._meta.object_name.lower()
    title_url_key = ('%s:%s' % (site.slugs, model_name)).lower()

    resolver = SIDEBAR_TITLE_URL_MAPPINGS.get(title_url_key)

    url = None
    if callable(resolver):
        url = resolver(obj)
    else:
        choices = (
            '%s:%s:index' % (site.slugs, model_name),
            '%s:news:index' % site.slugs,
            'news:%s:index' % model_name
        )
        for choice in choices:
            try:
                url = reverse(choice)
            except NoReverseMatch:
                continue
            else:
                break

    if url is None:
        raise NoReverseMatch('Reverse for %s %r at %s site failed' % (model_name, obj.pk, site.slugs))

    logger.debug('Index url for %s %r at %s site is %s' % (model_name, obj.pk, site.slugs, url))

    return url
