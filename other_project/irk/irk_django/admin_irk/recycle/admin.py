# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from irk.recycle.forms import CatForm, DotForm
from irk.recycle.models import Category, Dot, RelatedArticle


@admin.register(Dot)
class DotAdmin(admin.ModelAdmin):
    form = DotForm
    change_form_template = 'admin/change_form_dot.html'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CatForm
    change_list_template = 'admin/cat_sort.html'

@admin.register(RelatedArticle)
class RelatedArticleAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # у нас собственный интерфейс добавления связанных статей
        return False
