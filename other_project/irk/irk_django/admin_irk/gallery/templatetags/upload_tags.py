# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from irk.gallery.helpers import get_parent_content_type


register = template.Library()


@register.inclusion_tag('gallery/admin_multiupload.html', takes_context=True)
def admin_multiupload(context, obj, inline_admin_formset):
    """
    Поле multiupload`а галлереи для объекта.

    :param obj: объект модели редактируемый в админке. None - если объект еще не создан.
    :type obj: django.db.models.Model or None
    :param inline_admin_formset: обертка для inline formsets в админке
    :type inline_admin_formset: django.contrib.admin.helpers.InlineAdminFormSet
    """

    if obj:
        ct_id = get_parent_content_type(obj).pk
        object_id = obj.pk
    else:
        # Объект модели еще не создан, определяем content_type создаваемого объекта.
        model_class = inline_admin_formset.model_admin.model
        ct_id = get_parent_content_type(model_class).pk
        object_id = None

    return {
        'content_type_id': ct_id,
        'object_id': object_id,
        'prefix': inline_admin_formset.formset.prefix,
        'MEDIA_URL': settings.MEDIA_URL,
    }
