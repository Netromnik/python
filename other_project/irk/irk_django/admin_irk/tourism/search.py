# -*- coding: utf-8 -*-

from irk.utils.search import ModelSearch
from irk.phones.search import SectionFirmSearch


class HotelSearch(SectionFirmSearch):
    pass


class TourBaseSearch(SectionFirmSearch):
    pass


class TourFirmSearch(SectionFirmSearch):
    pass


class CompanionSearch(ModelSearch):
    fields = ('place', 'my_composition', 'find_composition')
    boost = {
        'place': 1.0,
    }

