# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from irk.utils.cache import invalidate_tags, model_cache_key


def invalidate(sender, **kwargs):
    """Инвалидация кэша фирм"""

    from irk.phones.models import Firms, Address, SectionFirm

    tags = ['phones', ]

    instance = kwargs.get('instance')
    if isinstance(instance, Firms):
        tags.append(model_cache_key(instance))
        from irk.phones.helpers import firms_library
        for model_cls in firms_library:
            ct = ContentType.objects.get_for_model(model_cls)
            tags.append('%s.%s.%s' % (ct.app_label, ct.model, instance.pk))

    elif isinstance(instance, Address):
        firm = instance.firm_id
        if isinstance(firm, SectionFirm):
            tags.append(model_cache_key(firm.firms_ptr))
        else:
            tags.append(model_cache_key(instance.firm_id))

    invalidate_tags(tags)
