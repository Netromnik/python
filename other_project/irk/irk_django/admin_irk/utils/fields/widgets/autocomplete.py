# -*- coding: utf-8 -*-

from django_select2.widgets import AutoHeavySelect2Widget, AutoHeavySelect2TagWidget


class ClearableAutoHeavySelect2Widget(AutoHeavySelect2Widget):
    def init_options(self):
        super(ClearableAutoHeavySelect2Widget, self).init_options()

        self.options['allowClear'] = True
        self.options['placeholder'] = u'Введите название'


class AutoSelect2TagsWidget(AutoHeavySelect2TagWidget):
    """
    Виджет для ввода тегов.
    Используется для тегов из приложения Taggit.
    """

    def init_options(self):
        super(AutoSelect2TagsWidget, self).init_options()

        self.options['tokenSeparators'] = [","]
