
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin

from .models import BusinessAccount
from .forms import BusinessAccountAdminForm
from utils.files.admin import admin_media_static


@admin.register(BusinessAccount)
class BusinessAccountAdmin(admin.ModelAdmin):
    """Админ бизнес аккаунтов"""

    form = BusinessAccountAdminForm

    @admin_media_static
    class Media(object):
        css = {
            'all': ('css/admin.css', 'news/css/admin.css'),
        }
        js = (
            'news/js/admin.js', 'js/apps-js/admin.js',
        )
