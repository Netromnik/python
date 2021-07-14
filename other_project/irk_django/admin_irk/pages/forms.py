# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from irk.pages.models import Page
from irk.pages.settings import FLATPAGE_TEMPLATES


class PageAdminForm(forms.ModelForm):
    """Форма текстовых страниц в админке"""

    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/]+$',
        help_text=_("Example: '/about/contact/'. Make sure to have leading and trailing slashes."),
        error_messages={'invalid': _("This value must contain only letters, numbers, underscores, dashes or slashes.")})
    content = forms.CharField(label=_("Content"), widget=forms.Textarea(attrs={'cols': 80, 'rows': 50}))
    template_name = forms.ChoiceField(label=u'Шаблон', choices=FLATPAGE_TEMPLATES)

    def clean_url(self):
        value = self.cleaned_data['url']
        value = '/{}/'.format(value.strip('/')).replace('//', '/')

        return value

    def clean(self):
        url = self.cleaned_data.get('url')
        site = self.cleaned_data.get('site')

        if url and site:
            queryset = Page.objects.filter(url=url, site=site)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(u'Страница с таким адресом уже существует')

        return self.cleaned_data
