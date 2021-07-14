# -*- coding: utf-8 -*-


from django_select2 import AutoSelect2Field
from django.contrib.contenttypes.models import ContentType

from irk.polls.forms.widgets import TargetClearableAutoHeavySelect2Widget


class TargetAutocompleteField(AutoSelect2Field):
    """Автокомплит для объектов голосований"""

    widget = TargetClearableAutoHeavySelect2Widget

    def get_results(self, request, term, page, context):
        choices = []

        target_ct_id = request.GET.get('id_target_ct')

        if target_ct_id:
            ct = ContentType.objects.get_for_id(target_ct_id)
            items = ct.model_class().objects.filter(title__icontains=term)[:25]
            for item in items:
                choices.append([item.pk, item.title])

        return 'nil', False, choices
