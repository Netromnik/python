# -*- coding: utf-8 -*-

from irk.utils.search import ModelSearch


class SectionSearch(ModelSearch):
    fields = ('name',)


class FirmSearch(ModelSearch):
    fields = ('name', 'alternative_name', 'description')
    boost = {
        'name': 1.0,
        'alternative_name': 0.75,
        'description': 0.5,
    }

    def get_queryset(self):
        return super(FirmSearch, self).get_queryset().filter(visible=True)


class SectionFirmSearch(FirmSearch):

    def get_queryset(self):
        return super(SectionFirmSearch, self).get_queryset().filter(is_active=True)


class AddressSearch(ModelSearch):
    fields = ('name', 'location', 'phones')

    def get_queryset(self):
        return super(AddressSearch, self).get_queryset().filter(firm_id__visible=True)
