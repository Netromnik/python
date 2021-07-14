# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from reversion.admin import VersionAdmin

from irk.pages.forms import PageAdminForm
from irk.pages.models import Page, File
from irk.pages.settings import FLATPAGE_TEMPLATES
from irk.utils.files.admin import admin_media_static

# Обратная совместимость со старыми формами
TEMPLATES = FLATPAGE_TEMPLATES


class MetaInline(admin.StackedInline):
    model = File
    template = 'admin/edit_inline/stacked_for_file.html'
    extra = 1


class PageAdmin(VersionAdmin):
    form = PageAdminForm
    list_display = ('position', 'url', 'title', 'site')
    list_display_links = ('url', 'title')
    list_editable = ('position',)
    list_filter = ('site',)
    search_fields = ('url', 'title')
    inlines = (MetaInline,)
    ordering = ('-id',)

    @admin_media_static
    class Media(object):
        css = {'all': ('css/admin.css',)}
        js = (
            'js/apps-js/admin.js',
            "js/lib/jquery-ui.js",
            "js/apps-js/plugins.js",
        )

    def get_queryset(self, request):
        qs = super(PageAdmin, self).get_queryset(request)
        if not self._can_add(request.user):
            return qs.filter(editors__in=request.user.groups.all())
        return qs

    def changelist_view(self, request, extra_context=None):
        if not self._can_add(request.user):
            if not extra_context:
                extra_context = {}
            extra_context['has_add_permission'] = False

        return super(PageAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, form_url='.', extra_context=None):
        if not self._can_add(request.user):
            raise PermissionDenied(u'Добавлять страницы могут только редакторы текстовых страниц')
        return super(PageAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='.', extra_context=None):
        if not self._can_add(request.user):
            self.exclude = ('site', 'editors')
        return super(PageAdmin, self).change_view(request, object_id, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        if not self._can_add(request.user):
            raise PermissionDenied(u'Добавлять страницы могут только редакторы текстовых страниц')
        return super(PageAdmin, self).delete_view(request, object_id, extra_context)

    def _can_add(self, user):
        if user.is_superuser:
            return True

        ct = ContentType.objects.get_for_model(Page)
        perm = Permission.objects.get(codename='change_page', content_type=ct)

        return user in User.objects.filter(Q(user_permissions=perm) | Q(groups__permissions=perm),
                                           is_staff=True).distinct()


admin.site.register(Page, PageAdmin)
