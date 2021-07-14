# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist


def invalidate(sender, **kwargs):
    """Протухание кэша связанных объектов при изменении рейтинга"""

    from irk.ratings.models import Rate

    instance = kwargs.get('instance')

    try:
        obj = instance.obj.content_type.get_object_for_this_type(pk=instance.obj.object_pk)
    except ObjectDoesNotExist:
        return

    try:
        app_module = __import__('%s.cache' % instance.obj.content_type.app_label, fromlist=['invalidate'])
    except ImportError:
        return
    else:
        if hasattr(app_module, 'invalidate'):
            app_module.invalidate(sender=Rate, instance=obj)
