# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist

from irk.utils.cache import invalidate_tags

__all__ = ('invalidate',)

__invalidate_cache = {}
EMPTY_OBJECT = object()


def invalidate(sender, **kwargs):
    """Вызов инвалидации кэша для привязанной модели"""

    from irk.polls.models import Poll, PollChoice, PollVote

    invalidate_tags(('polls',))

    instance = kwargs.get('instance')

    if isinstance(instance, PollVote):
        instance = instance.choice.poll
    elif isinstance(instance, PollChoice):
        instance = instance.poll

    try:
        if instance.target_ct:
            obj = instance.target_ct.get_object_for_this_type(pk=instance.target_id)
        else:
            return
    except (ObjectDoesNotExist, AttributeError):
        return

    invalidate_callback = __invalidate_cache.get(instance.target_ct.app_label)
    if invalidate_callback == EMPTY_OBJECT:
        return

    if not invalidate_callback:
        try:
            app_module = __import__('%s.cache' % instance.target_ct.app_label, fromlist=['invalidate'])
        except ImportError:
            return
        else:
            __invalidate_cache[instance.target_ct.app_label] = getattr(app_module, 'invalidate', EMPTY_OBJECT)

    if callable(__invalidate_cache[instance.target_ct.app_label]):
        __invalidate_cache[instance.target_ct.app_label](sender=Poll, instance=obj)
