# -*- coding: utf-8 -*-

from django import forms

from admin import GalleryInlineFormset
from irk.gallery import models
import fields


class SiteGalleryInlineFormset(GalleryInlineFormset):
    def add_fields(self, form, index):
        """A hook for adding extra fields on to each form instance."""
        super(SiteGalleryInlineFormset, self).add_fields(form, index)
        if self.can_delete:
            form.fields['DELETE'] = forms.BooleanField(
                widget=forms.HiddenInput(attrs={'class': 'delete_input'}),
                required=False
            )


class PictureForm(forms.ModelForm):
    picture = fields.Picture(
        label=u'Изображение', required=False,
        template='widgets/picture_block.html')

    main = forms.BooleanField(
        widget=forms.HiddenInput(attrs={'class': 'main_input'}),
        required=False)

    best = forms.BooleanField(
        widget=forms.HiddenInput(attrs={'class': 'best_input'}),
        required=False)

    def __init__(self, *args, **kwargs):
        super(PictureForm, self).__init__(*args, **kwargs)

    class Meta:
        models = models.GalleryPicture
        exclude = ('position', )


gallery_formset = forms.models.inlineformset_factory(
    models.Gallery,
    models.GalleryPicture,
    formset=SiteGalleryInlineFormset,
    form=PictureForm,
    extra=48,
    max_num=48,
    fields='__all__',
)
