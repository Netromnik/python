from django import forms
from .models import Question, Vacancy, Section
from utils.helpers import filter_invalid_xml_chars


class CoordinateInlineFormset(forms.models.BaseInlineFormSet):
    def is_valid(self):
        # TODO: зачем этот метод?
        return super(CoordinateInlineFormset, self).is_valid() and not any([bool(e) for e in self.errors])


class AuthFeedbackForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail', required=True)

    class Meta:
        model = Question
        fields = ('content', 'email', 'attach')


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('reply', 'attach')


class OrderForm(forms.Form):
    contact = forms.CharField(max_length=1000)
    description = forms.CharField(widget=forms.TextInput())

    class Meta:
        fields = ('contact', 'description')


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = '__all__'


class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data

        device_pc_percent = data.get('device_pc_percent', 0)
        device_mobile_percent = data.get('device_mobile_percent', 0)
        device_percent = device_pc_percent + device_mobile_percent

        if int(round(device_percent)) != 100:
            raise forms.ValidationError('Суммарный процент всех девайсов не равен 100')

        return data

    def clean_mediakit_title(self):
        return filter_invalid_xml_chars(self.cleaned_data['mediakit_title'])

    def clean_mediakit_attraction_text(self):
        return filter_invalid_xml_chars(self.cleaned_data['mediakit_attraction_text'])

    def clean_mediakit_benefit_text(self):
        return filter_invalid_xml_chars(self.cleaned_data['mediakit_benefit_text'])


class AgeGenderPercentAdminInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        percent_sum = 0
        for form in self.forms:
            percent_sum += form.cleaned_data.get('percent', 0)
        if int(round(percent_sum)) != 100:
            raise forms.ValidationError('Суммарный процент всех возраст-полов {} не равен 100'.format(percent_sum))


class FaqQuestionForm(forms.Form):
    """Форма вопроса на странице FAQ"""

    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'col': '30'}))
