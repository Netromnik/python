# -*- coding: utf-8 -*-

from django import forms

from irk.blogs.models import BlogEntry, Author
from irk.profiles.forms.fields import UserAutocompleteField


class BlogEntryForm(forms.ModelForm):
    caption = forms.CharField(label=u'Подводка', max_length=100, required=True, widget=forms.Textarea)

    class Meta:
        model = BlogEntry
        fields = ('title', 'caption', 'content')


class BlogEntryAdminForm(forms.ModelForm):
    class Meta:
        model = BlogEntry
        fields = ('title', 'caption', 'content', 'visible')


class AuthorAdminForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'is_visible', 'is_operative')


class AuthorCreateAdminForm(forms.Form):
    user = UserAutocompleteField()
