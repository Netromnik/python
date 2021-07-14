
from django import forms

from ..models import BusinessAccount
from .fields import ClientAutocompleteMultipleField


class BusinessAccountAdminForm(forms.ModelForm):
    """Форма админе бизнес аккаунта"""

    clients = ClientAutocompleteMultipleField(label=u'Клиент', required=False)

    class Meta:
        model = BusinessAccount
        fields = ('name', 'clients')
