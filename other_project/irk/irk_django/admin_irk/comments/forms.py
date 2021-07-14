# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django import forms

from irk.comments import models as m
from irk.utils.decorators import strip_fields


@strip_fields
class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = m.Comment
        fields = (
            'text', 'parent'
        )

@strip_fields
class CommentEditForm(forms.ModelForm):
    class Meta:
        model = m.Comment
        fields = (
            'text',
        )
