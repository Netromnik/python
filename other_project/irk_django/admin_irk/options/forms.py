
from django import forms

from .models import Site


class SiteAdminForm(forms.ModelForm):
    """Форма редактирования раздела сайта в админке"""

    class Meta:
        model = Site
        fields = '__all__'

    def clean(self):
        # будет False, если стоит галочку "Очистить" и None, если изменений в поле нет
        image = self.cleaned_data.get('branding_image')
        color = self.cleaned_data.get('branding_color')
        widget_image = self.cleaned_data.get('widget_image')

        if not self.errors:
            # Если установлена галочка для удаления изображения брендирования,
            # удаляем данные из поля цвета
            if image is False:
                self.cleaned_data['branding_color'] = None
            # если загружается изображение брендирования, то должен быть и цвет фона
            elif image and not color:
                raise forms.ValidationError(u'Для брендирования по умолчанию должны быть загружены изображение и цвет фона')

            # Если установлена галочка для удаления изображения виджета, то также удаляем ссылку и текст виджета
            if widget_image is False:
                self.cleaned_data['widget_link'] = None
                self.cleaned_data['widget_text'] = None

        return self.cleaned_data
