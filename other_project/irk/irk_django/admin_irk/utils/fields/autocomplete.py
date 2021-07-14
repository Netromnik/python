# -*- coding: utf-8 -*-
import numbers

from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist


class AutocompleteModelChoiceField(forms.ModelChoiceField):
    """
    Поле выбора экземляра определенной модели с автозаполнением.
    Работа с моделью может происходить не через первичный ключ, а через поле передаваемое в параметре `to_field_name`.
    """

    def __init__(self, queryset, data_url, to_field_name=None, *args, **kwargs):
        """
        :param queryset: QuerySet конкретной модели
        :param data_url: url для получения вариантов автозаполнения
        :type data_url: str
        :param to_field_name: Название поля для связи с моделью. Используется вместо первичного ключа.
        :type to_field_name: str
        """
        kwargs['widget'] = forms.TextInput(attrs={'class': 'j-autocomplete', 'data-autocomplete-url': data_url})
        kwargs['to_field_name'] = to_field_name
        super(AutocompleteModelChoiceField, self).__init__(queryset, *args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        key = self.to_field_name or 'pk'
        value = self.queryset.filter(**{key: value}).first()
        if value is None:
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')

        return value

    def prepare_value(self, value):
        """Подготовить значение к отображению. Используется в BoundField при получении значения поля."""
        # Нужно: Когда форма редактируется отображать в виджете значение поля модели переданного через параметр
        # `to_field_name`, а не первичный ключ. Поэтому, если value целое число, считаем что это id модели.
        if isinstance(value, numbers.Integral):
            try:
                value = self.queryset.get(id=value)
            except ObjectDoesNotExist:
                pass

        return super(AutocompleteModelChoiceField, self).prepare_value(value)

