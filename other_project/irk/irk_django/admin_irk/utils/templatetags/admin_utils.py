# -*- coding: utf-8 -*-

"""Перегрузка тегов админки"""

from django.contrib.admin.templatetags.admin_list import items_for_result, result_headers, result_hidden_fields, \
    ResultList
from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.safestring import mark_safe

from irk.news.permissions import is_site_news_moderator

register = Library()


def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            result_list = ResultList(form, items_for_result(cl, res, form))
            if hasattr(res, 'pk'):
                result_list.append(mark_safe(u'<td><a href="%s/delete/">Удалить</a></td>' % res.pk))
            yield result_list
    else:
        for res in cl.result_list:
            result_list = ResultList(None, items_for_result(cl, res, None))
            if hasattr(res, 'pk'):
                result_list.append(mark_safe(u'<td><a href="%s/delete/">Удалить</a></td>' % res.pk))
            yield result_list


@register.inclusion_tag("admin/change_list_results.html")
def deletable_result_list(cl):
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h['sortable'] and h['sorted']:
            num_sorted_fields += 1
    return {
        'cl': cl,
        'result_hidden_fields': list(result_hidden_fields(cl)),
        'result_headers': headers,
        'num_sorted_fields': num_sorted_fields,
        'results': list(results(cl))
    }


prepopulated_fields_js = register.inclusion_tag('admin/prepopulated_fields_js.html', takes_context=True)(
    prepopulated_fields_js)


@register.filter
def inline_admin_formset_model_name(value):
    return value.model_admin.model.__name__


@register.inclusion_tag('utils/tags/edit_button.html', takes_context=True)
def get_object_admin_link(context, obj):
    """Ссылка на админ объекта"""

    request = context.get('request')
    url = ''
    if is_site_news_moderator(request):
        url = reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name), args=[obj.id])
    return {
        'url': url
    }
