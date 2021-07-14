# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.forms.models import inlineformset_factory

from irk.gallery import models
from irk.gallery import forms
from irk.gallery.checks import GalleryInlineModelAdminChecks
from irk.utils.files.admin import admin_media_static


class GalleryInline(GenericStackedInline):
    template = 'admin/edit_inline/gallery_inline.html'
    model = models.GalleryPicture
    extra = 1

    checks_class = GalleryInlineModelAdminChecks

    @admin_media_static
    class Media(object):
        js = (
            'gallery/js/swfobject.js',
            'gallery/js/jquery.uploadify.js',
            'gallery/js/admin.js',
        )

    def get_formset(self, request, obj=None, **kwargs):
        formset = forms.GalleryInlineFormset
        formset.user = request.user

        return inlineformset_factory(
            models.Gallery, models.GalleryPicture, formset=formset, form=forms.PictureForm, extra=0, fields='__all__',
        )


class GalleryBBCodeInline(GalleryInline):
    """Инлайны галерей, выводящие поле для BB кода [image 12345]"""

    template = 'admin/edit_inline/gallery_bbcode_inline.html'

    @admin_media_static
    class Media(object):
        css = {'all': ['css/notifications/style.css', ]}
        js = (
            'gallery/js/swfobject.js',
            'gallery/js/jquery.uploadify.js',
            'gallery/js/admin.js',
        )


admin.site.register(models.Gallery)
admin.site.register(models.Picture)
