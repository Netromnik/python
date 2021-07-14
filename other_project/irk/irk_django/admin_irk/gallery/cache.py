# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.cache import cache


def invalidate(sender, **kwargs):
    """Вызов инвалидации кэша для привязанной модели"""

    from irk.gallery.models import Gallery, Picture, GalleryPicture

    instance = kwargs.get('instance')
    if isinstance(instance, GalleryPicture):
        instance = instance.gallery
    elif isinstance(instance, Picture):
        try:
            instance = GalleryPicture.objects.get(picture=instance).gallery
        except(ObjectDoesNotExist, MultipleObjectsReturned):  # TODO: Перехват только необходимых исключений
            return

    cache.delete('gallery:main_picture:%s' % instance.pk)

    try:
        obj = instance.content_type.get_object_for_this_type(pk=instance.object_id)
    except (ObjectDoesNotExist, AttributeError, ):
        return

    cache.delete(':'.join(['gallery', 'main', instance.content_type.app_label,
                           instance.content_type.model, str(obj.pk)]))
    cache.delete(':'.join(['gallery', 'best', instance.content_type.app_label,
                           instance.content_type.model, str(obj.pk)]))

    try:
        app_module = __import__('%s.cache' % instance.content_type.app_label, fromlist=['invalidate'])
    except ImportError:
        return
    else:
        if hasattr(app_module, 'invalidate'):
            app_module.invalidate(sender=Gallery, instance=obj)
