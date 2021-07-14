# -*- coding: utf-8 -*-

from django import forms

from irk.home.models import Logo

MONTH_NAMES = (
    (1, u"январь",),
    (2, u"февраль",),
    (3, u"март",),
    (4, u"апрель",),
    (5, u"май",),
    (6, u"июнь",),
    (7, u"июль",),
    (8, u"август",),
    (9, u"сентябрь",),
    (10, u"октябрь",),
    (11, u"ноябрь",),
    (12, u"декабрь"),
)


class LogoAdminForm(forms.ModelForm):
    """Форма для логотипов в админке"""

    start_month = forms.CharField(label=u'Месяц начала показа', widget=forms.Select(choices=MONTH_NAMES))
    end_month = forms.CharField(label=u'Месяц окончания показа', widget=forms.Select(choices=MONTH_NAMES))
    start_day = forms.CharField(label=u'День начала показа',
                                widget=forms.Select(choices=list(enumerate(range(1, 31), start=1))))
    end_day = forms.CharField(label=u'Дата окончания показа',
                              widget=forms.Select(choices=list(enumerate(range(1, 31), start=1))))

    class Meta:
        model = Logo
        fields = ('image', 'title', 'color', 'start_month', 'start_day', 'end_month', 'end_day', 'visible')
