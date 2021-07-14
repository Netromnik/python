from django.contrib import admin

from .forms import SiteAdminForm
from .models import Site


class SiteAdmin(admin.ModelAdmin):
    list_display = ('link_name', 'title', 'is_hidden', 'in_menu', 'mark_in_menu', 'highlight', 'position')
    list_editable = ('position',)
    form = SiteAdminForm
    ordering = ('position',)

    def link_name(self, obj):
        return obj.name or u'Главная страница'
    link_name.short_description = u'Название'

admin.site.register(Site, SiteAdmin)
