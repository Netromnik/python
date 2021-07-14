# -*- coding: utf-8 -*-

import random

# Зачем здесь as global_settings:
# В utils.session делается импорт from irk.utils import settings.
# При импорте from django.conf import settings модуль utils.settings перекрывается им.
# TODO: реализовать рабочие импорты без этих дел, возможно через __all__
from django.conf import settings as global_settings

from pytils import dt


def random_int_challenge():
    """Генерация случайного seed для капчи"""

    chars, ret = range(0, 9), u''
    for i in range(global_settings.CAPTCHA['LENGTH']):
        ret += str(random.choice(chars))
    return ret.upper(), ret


images = ['jpg', 'gif', 'jpeg', 'png']

dt.DAY_NAMES = (
    (u"пн", u"понедельник", u"понедельник", u"в\xa0"),
    (u"вт", u"вторник", u"вторник", u"во\xa0"),
    (u"ср", u"среда", u"среду", u"в\xa0"),
    (u"чт", u"четверг", u"четверг", u"в\xa0"),
    (u"пт", u"пятница", u"пятницу", u"в\xa0"),
    (u"сб", u"суббота", u"субботу", u"в\xa0"),
    (u"вс", u"воскресенье", u"воскресенье", u"в\xa0")
)
