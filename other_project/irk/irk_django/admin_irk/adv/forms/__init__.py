"""Формы для админки баннеров"""

import logging
import os.path
import re

from django import forms
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.urls import reverse
from lxml.html import fromstring

from about.models import Price
from options.models import Site
from utils.fields.file import AdminImagePreviewWidget
from utils.fields.select import MultiAjaxTextField
from utils.grabber import proxy_requests

from adv.helpers import add_utm
from adv.models import Place, Period, Client, Booking, Communication, Contact, Payment, UserOption, File, Banner

logger = logging.getLogger(__name__)


BANNER_IFRAME_VALIDATION_RE = re.compile(r'<[\/]{0,1}([a-z]*)', re.IGNORECASE | re.MULTILINE | re.DOTALL)


class BannerAdminForm(forms.ModelForm):
    """
    Форма для редактирования баннера в админке
    !TODO: Даделать
    """

    def clean(self):
        data = self.cleaned_data
        start_time = data.get('show_time_start')
        end_time = data.get('show_time_end')

        if (start_time or end_time) and (not start_time or not end_time):
            raise forms.ValidationError(u'Нужно указывать даты начала и окончания показа вместе!')

        roll_direction = data.get('roll_direction')
        roll_width = data.get('roll_width')
        if any([roll_direction, roll_width]) and not all([roll_direction, roll_width]):
            raise forms.ValidationError(u'Для разворачивающихся баннеров нужно указывать направление и ширину')

        client = self.cleaned_data.get('client')
        places = self.cleaned_data['places']
        if client:
            for place in places:
                if place.juridical_required and not client.juridical_name:
                    raise forms.ValidationError(
                        u'Место размещения «{}» требует заполненного юридического названия клиента'.format(place.name))

        return data

    def clean_iframe(self):
        html = self.cleaned_data.get('iframe')
        if html:
            if not '<iframe' in html or not '</iframe' in html:
                raise forms.ValidationError(u'В тексте должен находиться тег <iframe>')

            tags = BANNER_IFRAME_VALIDATION_RE.findall(html)
            for tag in tags:
                if tag and tag != 'iframe':
                    raise forms.ValidationError(u'В тексте запрещено использование любых тегов, кроме <iframe>')

        return html or ''

    def clean_url(self):
        value = self.cleaned_data.get('url', '')
        return value.strip() if value else value

    class Meta:
        model = Banner
        fields = ['show_time_start', 'show_time_end', 'roll_direction', 'roll_width', 'iframe']
        autocomplete_fields = ['client', 'places']


class PeriodAdminInlineForm(forms.ModelForm):
    """Форма для инлайнового редактирования периодов в админке"""

    def clean_date_to(self):
        date_from = self.cleaned_data.get('date_from')
        date_to = self.cleaned_data.get('date_to')

        if not date_from or not date_to:
            raise forms.ValidationError(u'Не указаны начальная и конечная даты периода')

        if date_from > date_to:
            raise forms.ValidationError(u'Неверно задан период')

        return date_to

    class Meta:
        fields = '__all__'
        model = Period


class FileTestForm(forms.Form):
    """Форма тестирования файлов для баннеров"""

    file = forms.FileField()


class FileAdminInlineForm(forms.ModelForm):
    """Форма для :class:`adv.admin.FileInline`"""

    # Скаченный html5 код баннера
    _html5_code = None

    main = forms.FileField(widget=AdminImagePreviewWidget, label=u'Баннер', required=False)
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 70}), label=u'Текст', required=False)

    class Meta:
        model = File
        fields = '__all__'

    def clean_dummy(self):
        main = self.cleaned_data.get('main')
        value = self.cleaned_data.get('dummy')

        ext = None
        if main:
            ext = os.path.splitext(main.name)[1]
        elif self.instance.main:
            ext = os.path.splitext(self.instance.main.name)[1]

        if ext == '.swf' and (not value[0] and not self.instance.dummy):
            raise forms.ValidationError(u'Загрузите заглушку для Flash-баннера')

        return value

    def clean_html5_url(self):
        """Проверяем, что введен правильный url. Скачиваем код баннера."""

        html5_url = self.cleaned_data.get('html5_url')

        # Если поле не менялось, ничего не делаем
        if 'html5_url' not in self.changed_data:
            return html5_url

        # Поле было очищено, удаляем код баннера
        if not html5_url:
            self._html5_code = ''
            return html5_url

        try:
            response = proxy_requests.get(html5_url)
            response.raise_for_status()
        except proxy_requests.RequestException:
            logger.debug(u'Fail download html5 banner from {}'.format(html5_url))
            raise forms.ValidationError(u'Не удалось скачать html5 баннер, проверьте введенный url')

        try:
            html = fromstring(response.content)
            code = html.xpath('//script')[1].text
            code = code.replace('swiffyobject = ', '').strip().rstrip(';')
        except Exception:
            logger.exception(u'Error parse html5 banner code.')
            raise forms.ValidationError(u'Не удалось найти код баннера, проверьте введенный url ')

        self._html5_code = code

        return html5_url

    def save(self, commit=True):
        # Сохранение html5 кода баннера
        if self._html5_code is not None:
            self.instance.html5_code = self._html5_code

        # добавляем ютм-метку уже после сохранения файла, чтобы был id
        if self.instance.url and self.instance.url.strip():
            utm_content = 'file-{}'.format(self.instance.id)
            self.instance.url = add_utm(self.instance.url, self.instance.banner, utm_content)

        return super(FileAdminInlineForm, self).save(commit)


class FreePlacesForm(forms.Form):
    begin_date = forms.DateField()
    end_date = forms.DateField()
    sites = forms.ModelMultipleChoiceField(queryset=Site.objects.all(), required=False)


class BookingForm(forms.ModelForm):
    from_date = forms.DateField(widget=forms.DateInput(attrs={'autocomplete': 'off'}))
    to_date = forms.DateField(widget=forms.DateInput(attrs={'autocomplete': 'off'}))
    place = forms.ModelChoiceField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}),
                                   queryset=Place.objects.all())
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 18, 'rows': 5, 'autocomplete': 'off'}),
                              required=False)
    client = forms.ModelChoiceField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}),
                                    queryset=Client.objects.filter(is_deleted=False))

    class Meta:
        fields = '__all__'
        model = Booking


class UpdateBookingForm(BookingForm):
    client = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=Client.objects.filter(is_deleted=False),
                                    required=False)

    class Meta:
        fields = ['from_date', 'to_date', 'place']
        model = Booking


class ManagerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.last_name and obj.first_name:
            return u'{0} {1}'.format(obj.last_name, obj.first_name)
        else:
            return obj.username


class ClientForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'cols': 32, 'rows': 5, 'autocomplete': 'off'}),
                              required=False)
    info = forms.CharField(widget=forms.Textarea(attrs={'cols': 32, 'rows': 5, 'autocomplete': 'off'}), required=False)

    class Meta:
        fields = '__all__'
        model = Client

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        perm = Permission.objects.get(codename='can_use_bookings_system')
        self.fields['manager'].queryset = User.objects.filter(
            Q(id=self.instance.manager_id) | Q(user_permissions=perm) | Q(groups__permissions=perm),
            is_staff=True).distinct()


class AddClientForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Client

    def __init__(self, *args, **kwargs):
        super(AddClientForm, self).__init__(*args, **kwargs)

        perm = Permission.objects.get(codename='can_use_bookings_system')
        self.fields['manager'].queryset = User.objects.filter(
            Q(id=self.instance.manager_id) | Q(user_permissions=perm) | Q(groups__permissions=perm),
            is_staff=True).distinct()


class PaymentForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Payment


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'


class CommunicationForm(forms.ModelForm):
    client = forms.ModelChoiceField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}),
                                    queryset=Client.objects.filter(is_deleted=False))
    result = forms.CharField(widget=forms.Textarea(attrs={'cols': 18, 'rows': 7, 'autocomplete': 'off'}),
                             required=False)
    target = forms.CharField(widget=forms.Textarea(attrs={'cols': 18, 'rows': 7, 'autocomplete': 'off'}))

    class Meta:
        model = Communication
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CommunicationForm, self).__init__(*args, **kwargs)
        perm = Permission.objects.get(codename='can_use_bookings_system')
        self.fields['manager'].queryset = User.objects.filter(
            Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()
        if 'client' in self.initial:
            self.fields['contact'].queryset = Contact.objects.filter(client__id=self.initial['client'])


class CommunicationAdminForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CommunicationAdminForm, self).__init__(*args, **kwargs)
        perm = Permission.objects.get(codename='can_use_bookings_system')
        self.fields['manager'].queryset = User.objects.filter(
            Q(id=self.instance.manager_id) | Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()


class PlaceAdminForm(forms.ModelForm):
    about_price = forms.ModelChoiceField(queryset=Price.objects.all().order_by('page', 'place'))

    class Meta:
        model = Place
        fields = '__all__'


class UserOptionForm(forms.ModelForm):
    class Meta:
        model = UserOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserOptionForm, self).__init__(*args, **kwargs)
        perm = Permission.objects.get(codename='can_use_bookings_system')
        self.fields['user'].queryset = User.objects.filter(
            Q(id=self.instance.user_id) | Q(user_permissions=perm) | Q(groups__permissions=perm)).distinct()
