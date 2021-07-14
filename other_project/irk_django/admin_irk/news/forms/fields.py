# -*- coding: utf-8 -*-

import json

from django_select2.fields import AutoModelSelect2Field, AutoModelSelect2MultipleField, AutoSelect2Field, \
    AutoHeavySelect2Widget, AutoModelSelect2TagField, AutoHeavySelect2MultipleWidget
from sorl.thumbnail.main import DjangoThumbnail
from sorl.thumbnail.base import ThumbnailException
from taggit.models import Tag

from irk.news.models import BaseMaterial, Subject, News
from irk.utils.fields.widgets.autocomplete import AutoSelect2TagsWidget, ClearableAutoHeavySelect2Widget


class SubjectAutocompleteField(AutoModelSelect2Field):
    """Автокомплит сюжетов для форм"""

    queryset = Subject.objects
    search_fields = ('title__icontains',)
    widget = ClearableAutoHeavySelect2Widget


class NewsAutocompleteMultipleWidget(AutoHeavySelect2MultipleWidget):

    def init_options(self):
        super(NewsAutocompleteMultipleWidget, self).init_options()
        self.options['containerCssClass'] = 'select-news'


class NewsAutocompleteMultipleField(AutoModelSelect2MultipleField):
    queryset = News.objects
    search_fields = ('title__icontains',)
    widget = NewsAutocompleteMultipleWidget


class NewsAutocompleteField(AutoModelSelect2Field):
    """Автокомплит новостей для форм"""

    queryset = News.objects
    search_fields = ('title__icontains',)
    widget = ClearableAutoHeavySelect2Widget


class MaterialAutocompleteWidget(AutoHeavySelect2Widget):
    def render_texts(self, selected_choices, choices):
        return json.dumps(selected_choices)

    def init_options(self):
        super(MaterialAutocompleteWidget, self).init_options()
        self.options['formatSelection'] = '*START*autocomplete_material_set_content_type*END*'


class MaterialAutocompleteField(AutoSelect2Field):
    """Текстовое поле с автодополнением по материалам"""

    widget = MaterialAutocompleteWidget

    model_objects = BaseMaterial.objects

    def get_results(self, request, term, page, context):
        """Подготовка результатов автодополнения."""

        materials = self.model_objects.filter(title__icontains=term.encode("utf8")).order_by('-stamp', '-id') \
                        .select_subclasses()[:10]
        choices = []
        for material in materials:
            choices.append([
                material.pk, material.title_with_type(), {'ct_id': material.content_type.pk}
            ])
        return 'nil', False, choices


class LongreadAutocompleteField(MaterialAutocompleteField):
    """Текстовое поле с автодополнением по лонгридам (материалы кроме новостей)"""

    model_objects = BaseMaterial.longread_objects


class TagsAutocompleteField(AutoModelSelect2TagField):
    """Поле с автодополнением для тегов"""

    queryset = Tag.objects
    search_fields = ['name__icontains', ]
    widget = AutoSelect2TagsWidget

    def get_model_field_values(self, value):
        """Поле модели, которому будет присвоено значение введеное пользователем, когда такого объекта нет в БД"""

        return {'name': value}

    def create_new_value(self, value):
        """Создание объекта, если таковой не найден в БД."""

        # HACK: в MySQL поле с ключом unique регистронезависимо и выдается ошибка Duplicate error, если сохраняется тег
        # с названием отличающимся регистром. Пока решено делать это тут, но вообще лучше объединять теги с одинаковым
        # названием, но в разном регистре на фронтенде.
        obj, _ = self.queryset.get_or_create(**self.get_model_field_values(value))
        return getattr(obj, self.to_field_name or 'pk')
