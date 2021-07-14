# -*- coding: UTF-8 -*-

from django.db.models import Model
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType


def get_parent_content_type(essence):
    """
    Получить content type для модели с учетом наследования.
    Для моделей фирм, статей, объявлений возвращается content type базовой модели.
    Для остальных content type самой модели.

    :param essence: экземпляр модели или класс модели
    :type essence: Model or ModelBase
    :rtype: ContentType
    """

    from irk.phones.models import SectionFirm, Firms
    from irk.news.models import Article as NewsArticle
    from irk.obed.models import Article as ObedArticle, Review as ObedReview

    if isinstance(essence, Model):
        # сущность представляет собой экземпляр модели
        method = isinstance
    elif isinstance(essence, ModelBase):
        # сущность представляет собой класс модели
        method = issubclass
    else:
        raise ValueError('Param "essence" must be instance Model or class Model')

    # Для фирм-наследников базовой фирмы используем галерею от основной фирмы
    if method(essence, SectionFirm):
        content_type = ContentType.objects.get_for_model(Firms)
    # TODO: больше не актуально. Создан таск для рефакторинга.
    # Если сущность является рецензией, то возвращать контент-тайп от ObedArticle, а не от NewsArticle.
    # Потому, что при сохранении GalleryInlineFormset в админе Review родительским контент-тайпом является
    # ObedArticle, а не NewsArticle из-за того что Review - это наследование третьего уровня.
    # А GalleryInlineFormset расчитан только на объекты с наследованием максимум второго уровня.
    elif method(essence, ObedReview) or \
            (isinstance(essence, ObedArticle) and essence.is_review()):
        content_type = ContentType.objects.get_for_model(ObedArticle)
    elif method(essence, NewsArticle):
        content_type = ContentType.objects.get_for_model(NewsArticle)
    else:
        content_type = ContentType.objects.get_for_model(essence)

    return content_type
