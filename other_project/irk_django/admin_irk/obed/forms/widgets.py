# -*- coding: utf-8 -*-

from django.forms.widgets import CheckboxSelectMultiple, RadioSelect


class BillCheckboxSelectMultiple(CheckboxSelectMultiple):
    """ Вывод поля среднего счета заведения """

    option_template_name = 'obed/forms/widgets/bill_checkbox_option.html'


class BillRadioSelect(RadioSelect):
    """ Вывод поля среднего счета заведения в формы """

    option_template_name = 'obed/forms/widgets/bill_radio_option.html'
