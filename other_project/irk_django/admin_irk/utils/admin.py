# -*- coding: utf-8 -*-

from django.contrib import admin


class ReadOnlyAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(ReadOnlyAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields or self.fields


class HiddenModelAdminMixin(admin.ModelAdmin):
    """Примесь для сокрытия названия модели в списке моделей приложения"""

    def get_model_perms(self, *args, **kwargs):
        # Скрываем название модели в списке
        perms = super(HiddenModelAdminMixin, self).get_model_perms(*args, **kwargs)
        perms['list_hide'] = True

        return perms
