# -*- coding: utf-8 -*-

from taggit.managers import TaggableManager as BaseTaggableManager

from django.contrib.contenttypes.models import ContentType
from django.db import models


class GenericRelationsManager(models.Manager):
    """
    Менеджер упрощающий работу с обобщенными связями (Generic Relations).

    Применяется в моделях имеющих поле GenericForeignKey.
    """

    def for_object(self, obj):
        """
        Фильтрует queryset по связи с объектом.

        :param models.Model obj: объект обобщенной связи
        :rtype: models.query.QuerySet
        """

        ct = ContentType.objects.get_for_model(obj)

        return self.get_queryset().filter(content_type=ct, object_id=obj.pk)


class TaggableManager(BaseTaggableManager):
    """
    Менеджер для тегов из приложения Taggit. Следует использовать его, вместо стандартного в случае, если требуется
    автодополнение поля в админке.

    Переопределение потребовалось из-за того, что в админке в модельную форму передаются объекты TaggedItem,
    а ожидаются объекты Tag (происходит это в методе BaseModelForm.__init__ в функции model_to_dict).
    """

    def value_from_object(self, instance):
        if instance.pk:
            return [
                tagged_item.tag
                for tagged_item in self.through.objects.filter(**self.through.lookup_kwargs(instance))
            ]
        return self.through.objects.none()
