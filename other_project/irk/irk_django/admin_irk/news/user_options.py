# -*- coding: utf-8 -*-

import datetime

from irk.profiles.options import Option


class PhotoFullscreenHintOption(Option):
    """
    Показывать подсказку о полноэкранном режиме фоторепов или нет
    """

    choices = (1, 2)
    cookie_key = 'pfull'
    default = 1
    multiple = False

    def load_value_from_cookie(self, value):
        return int(value)

    def prepare_value_for_cookie(self, value):
        return int(value)

    def load_value_from_db(self, value):
        return int(value)

    def prepare_value_for_db(self, value):
        return int(value)


class PushNotificationHintOption(Option):
    """
    Показывать подсказку о push уведомлениях
    """

    choices = (1, 2, 3)
    cookie_key = 'pnotif'
    default = 1
    # После наступления этой даты, значение опции будет 3
    expire = datetime.date(2016, 05, 31)
    multiple = False

    def load_value_from_cookie(self, value):
        return int(value)

    def prepare_value_for_cookie(self, value):
        return int(value)

    def load_value_from_db(self, value):
        return int(value)

    def prepare_value_for_db(self, value):
        return int(value)


class IGrajdaninHintOption(Option):
    """
    Показывать сообщение о новом пункте меню iGrajdanin
    """

    choices = (1, 2)
    cookie_key = 'igrajhint'
    default = 1
    multiple = False

    def load_value_from_cookie(self, value):
        return int(value)

    def prepare_value_for_cookie(self, value):
        return int(value)

    def load_value_from_db(self, value):
        return int(value)

    def prepare_value_for_db(self, value):
        return int(value)
