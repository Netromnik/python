# -*- coding: utf-8 -*-

from irk.profiles.options import BaseOption
from irk.newyear2014.models import Prediction


class PredictionOption(BaseOption):
    """Ответ на предсказание"""

    cookie_key = 'nypred'
    multiple = False

    @property
    def choices(self):
        return list(Prediction.objects.all().values_list('pk', flat=True))

    @property
    def default(self):
        return 0

    def prepare_value_for_db(self, value):
        if value:
            return int(value)
        return 0

    def load_value_from_db(self, value):
        try:
            for x in self.choices:
                if int(x) == int(value):
                    return int(x)
        except (ValueError, IndexError):
            return self.default

    def prepare_value_for_cookie(self, value):
        return self.prepare_value_for_db(value)

    def load_value_from_cookie(self, value):
        return self.load_value_from_db(value)
