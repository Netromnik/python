from django import forms
from django.db import models


class CheckBoxManyToManyField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class CheckBoxManyToMany(models.ManyToManyField):
    def formfield(self, *args, **kwargs):
        defaults = {'form_class': CheckBoxManyToManyField, }
        defaults.update(kwargs)
        return super(CheckBoxManyToMany, self).formfield(**defaults)  
