# -*- coding: utf-8 -*-

from irk.utils.fields.widgets.autocomplete import ClearableAutoHeavySelect2Widget


class TargetClearableAutoHeavySelect2Widget(ClearableAutoHeavySelect2Widget):
    def init_options(self):
        super(TargetClearableAutoHeavySelect2Widget, self).init_options()

        self.options['ajax'] = {
            'dataType': 'json',
            'quietMillis': 100,
            'data': '*START*django_select2.runInContextHelper(target_url_param_generator, selector)*END*',
            'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
        }
