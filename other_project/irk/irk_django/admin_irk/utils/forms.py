# -*- coding: utf-8 -*-


class EmptyLabelSuffixFormMixin(object):
    """Миксин форм для убирания двоеточия у лейблов полей"""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(EmptyLabelSuffixFormMixin, self).__init__(*args, **kwargs)
