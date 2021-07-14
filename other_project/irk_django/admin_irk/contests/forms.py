# -*- coding: utf-8 -*-

from django import forms

from irk.news.forms import BaseMaterialAdminForm
from irk.utils.fields.file import AdminImagePreviewWidget

from irk.contests.models import Contest, Participant


class ParticipantForm(forms.ModelForm):
    """Форма добавления участника конкурса"""

    phone = forms.CharField(label=u'Телефон', max_length=20, required=True)

    class Meta:
        model = Participant
        fields = ('title', 'description', 'full_name', 'phone')


class ContestAdminForm(BaseMaterialAdminForm):
    """Форма для конкурса в админке"""

    w_image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Широкоформатная фотография',
        help_text=u'Размер: 940х445 пикселей'
    )
    image = forms.ImageField(
        widget=AdminImagePreviewWidget(), required=False, label=u'Стандартная фотография',
        help_text=u'Формат фотографии 3:2'
    )

    def clean(self):
        data = super(ContestAdminForm, self).clean()

        is_hidden = data.get('is_hidden')
        w_image = data.get('w_image')
        image = data.get('image')

        if not is_hidden and (not w_image or not image):
            raise forms.ValidationError(u'Для открытия конкурса необходимо заполнить поля с фотографиями')
        return data

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')

        if Contest.objects.filter(slug=slug).exclude(pk=self.instance).exists():
            raise forms.ValidationError(u'Конкурс с таким алиасом уже существует')
        return slug
