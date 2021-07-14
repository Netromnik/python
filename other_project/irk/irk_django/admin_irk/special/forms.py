# -*- coding: utf-8 -*-

"""Формы для админки спецпроектов"""

from django import forms

from irk.utils.fields.file import AdminImagePreviewWidget

from irk.special.models import Project
from irk.special.fields import PlaceAutocompleteField


class ProjectAdminForm(forms.ModelForm):
    """Форма редактирования спецпроекта в админке"""

    image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Широкоформатная фотография',
        help_text=u'Размер: 940х445 пикселей'
    )
    branding_top = PlaceAutocompleteField(label=u'Позиция брендирования вверху страницы', required=False)
    branding_bottom = PlaceAutocompleteField(label=u'Позиция брендирования внизу страницы', required=False)
    banner_right = PlaceAutocompleteField(label=u'Позиция баннера в правой колонке статей', required=False)

    class Meta:
        fields = '__all__'
        model = Project
