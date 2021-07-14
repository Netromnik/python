# -*- coding: utf-8 -*-

import ephem


def get_moon_phase(stamp):
    """
    Получить фазу луны
    """

    # ephem.Moon().phase() возращает процент видимой части луны, это не совсем то что нам нужно.
    # Поэтому вычисляем фазу на основе цикла новолуний.

    date = ephem.Date(stamp.date())
    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)
    lunation = (date - pnm) / (nnm - pnm)
    lunation = round(lunation, 1)

    if lunation == 0 or lunation == 1:
        return u'новолуние'
    elif lunation == 0.5:
        return u'полнолуние'
    elif 0 < lunation < 0.5:
        return u'растущая'
    elif 0.5 < lunation < 1:
        return u'убывающая'
    else:
        return ''
