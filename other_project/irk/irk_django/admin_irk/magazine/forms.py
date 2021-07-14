# -*- coding: utf-8 -*-

from django import forms

from irk.magazine.models import Magazine
from irk.magazine.fields import PlaceAutocompleteField


class MagazineAdminForm(forms.ModelForm):
    """Форма редактирования журнала в админке"""

    branding_bottom = PlaceAutocompleteField(label=u'Позиция брендирования внизу страницы', required=False)
    banner_right = PlaceAutocompleteField(label=u'Позиция баннера в правой колонке', required=False)
    banner_comment = PlaceAutocompleteField(label=u'Позиция между текстом и комментами', required=False)

    class Meta:
        fields = '__all__'
        model = Magazine
