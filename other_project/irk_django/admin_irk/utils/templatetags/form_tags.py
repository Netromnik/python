# -*- coding: utf-8 -*-

"""Хелперы для отрисовки полей формы в шаблоне

Предназначены для табличной верстки"""

# TODO: выяснить, какие из них используются

from django import template

register = template.Library()


# TODO: Выяснить, нужен ли context в шаблоне
@register.inclusion_tag('form/address_set.html', takes_context=True)
def address_set(context, address_form):
    """Рисует блок адресов с кнопочкой добавить ещё"""

    context['address_form'] = address_form

    return context

# TODO: Выяснить, нужен ли context в шаблоне
@register.inclusion_tag('form/obed_address_set.html', takes_context=True)
def obed_address_set(context, address_form):
    """Рисует блок адресов с кнопочкой добавить ещё"""

    context['address_form'] = address_form

    return context

@register.inclusion_tag('form/currency_address_set.html')
def currency_address_set(address_form):
    """Рисует блок адресов для валюты"""

    return {
        'address_form': address_form
    }

@register.inclusion_tag('form/tr_field.html')
def tr_field(field, class_name=None):
    """Отдаёт блок <tr><td>{ ЛЕЙБЛ }</td><td>{ ПОЛЕ }</td></tr>"""

    return {
        'field': field,
        'class_name': class_name,
    }


@register.inclusion_tag('form/tr_field_image.html')
def tr_field_image(field, class_name=None):
    """Отдаёт блок <tr><td>{ ЛЕЙБЛ }</td><td>{ КАРТИНКА }</td></tr>"""

    return {
        'field': field,
        'class_name': class_name
    }


@register.inclusion_tag('form/tr_field_file.html')
def tr_field_file(field, class_name=None):
    """Отдаёт блок <tr><td>{ ЛЕЙБЛ }</td><td>{ ФАЙЛ }</td></tr>"""

    return {
        'field': field,
        'class_name': class_name,
    }


@register.inclusion_tag('form/new/sections.html', takes_context=True)
def form_field_sections(context, field, class_name=None):
    return {
        'field': field,
        'class_name': class_name,
    }


@register.inclusion_tag('form/new/table_row.html')
def form_table_row(field, class_name=''):
    """Рендеринг поля формы в новой верстке"""

    return {
        'field': field,
        'class_name': class_name,
    }


@register.inclusion_tag('form/new/table_row_with_err.html')
def form_table_row_with_err(field, class_name=''):
    """Рендеринг поля формы в новой верстке"""

    return {
        'field': field,
        'class_name': class_name,
    }


@register.inclusion_tag('form/new/table_image_row.html')
def form_table_image_row(field):
    """Рендеринг поля изображения с полем «удалить»"""

    return {
        'field': field,
    }


@register.inclusion_tag('form/new/tr_field_contests.html')
def tr_field_contests(field, class_name=None, title=None):
    """Отдаёт блок <tr><td>{ ЛЕЙБЛ }</td><td>{ ПОЛЕ }</td></tr>"""

    if title:
        field.label = title

    return {
        'field': field,
        'class_name': class_name,
    }


@register.inclusion_tag('form/new/inline_field.html')
def form_field(field, class_name=''):
    """Рендеринг поля формы в новой верстке"""

    return {
        'field': field,
        'class_name': class_name,
    }
