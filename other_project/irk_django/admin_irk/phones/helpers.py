# -*- coding: utf-8 -*-

import re
import string

from django.apps import apps
from django.db.models.query import QuerySet

from irk.phones.models import SectionFirm

FIRM_CLEAN_RE = re.compile('\(.*?\)', re.IGNORECASE | re.UNICODE)


class SectionFirmContainer(set):
    """Контейнер для хранения всех фирм, отнаследованных от `phones.models.Firms'

    Не регистрируем прокси-модели для админки"""

    def __init__(self, *args):
        super(SectionFirmContainer, self).__init__(*args)
        self._is_loading = False

    def autodiscover(self):
        if self._is_loading:
            return

        self._is_loading = True

        for model in apps.get_models():
            if issubclass(model, SectionFirm) and model._meta.proxy:
                self.add(model)

        self._is_loading = False


firms_library = SectionFirmContainer()


class SearchHelper(object):
    """Helper получает ряд QuerySet моделей Firms и Address,
    и при итерации возвращает объекты модели Firms
    """

    def __init__(self, *args, **kwargs):
        self.querysets = []
        self._count = 0
        for qs in args:
            if isinstance(qs, QuerySet):
                self.querysets.append(qs)

    def count(self):
        if not self._count:
            self._count = max([qs.count() for qs in self.querysets])
        return self._count

    def __len__(self):
        return self.count()

    def __iter__(self):
        for qs in self.querysets:
            for item in qs.all():
                yield self._validate(item)

    def __getitem__(self, item):
        indices = (offset, stop, step) = item.indices(self.count())
        items = []
        total_len = stop - offset

        for qs in self.querysets:
            n = qs[offset:stop]

            if len(n) == 0:
                continue
            items += n

            if len(items) >= total_len:
                return map(self._validate, items)
            else:
                stop = total_len - len(items)
                continue

        return map(self._validate, items)

    def __add__(self, other):
        if isinstance(other, QuerySet):
            return SearchHelper(self, other)
        elif isinstance(other, SearchHelper):
            querysets = other._clone().querysets
            return SearchHelper(self, *querysets)
        else:
            raise TypeError

    def _validate(self, item):
        from irk.phones.models import Firms, Address

        if isinstance(item, Address):
            firm = item.firm_id
            firm.address = item
            return firm

        elif isinstance(item, Firms):
            try:
                item.address = item.address_set.all()[0]
            except (KeyError, IndexError):
                item.address = None

        return item


def clean_firm_name(name):
    name = FIRM_CLEAN_RE.sub('', name)
    name = name.strip(string.punctuation).split(',', 1)[0].strip()

    return name


def clear_phone(value):
    """Очищает телефон от лишних символов, возвращает только цифры"""

    return re.sub(r'[^\d]', '', value)