# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse

from irk.landings.settings import FORTUNE_TELLER_YOTA_SOCIAL_CARD_PATH
from irk.utils.http import ajax_request

FORTUNE_TELLER_YOTA_DATA = {
    1: 'Ты разобьешь свою\nдетскую копилку - как раз\nхватит, чтобы купить сахар\nи подсолнечное масло.',
    2: 'Этим летом тебя ждет\nлето.',
    3: 'Ты наконец-то займешься\nспортом. Ведь\nкомпьютерные игры\nпризнаны официальным\nвидом спорта.',
    4: 'В этом году ты начнешь\nзарабатывать еще больше.\nПотому что найдешь\nтретью работу.',
    5: 'Твоя мечта всегда рядом,\nцени её. Только запомни,\nбутерброд с колбасой\nлучше есть с маслом.',
    6: 'Первого января ты\nнайдешь кошелек с\nденьгами. Который\nпотерял 31 декабря.',
    7: 'Ты найдешь PlayStation 5\nпод елкой. Не забывай про\nежемесячные платежи.',
    8: 'Родственники подарят\nтебе кошку на новый год.\nМожет это намек, что пора\nкупить квартиру?',
    9: 'Твои соседи перестанут\nшуметь. Теперь вечеринки\nбудут проходить у тебя.',
    10: 'Твои инвестиции окупятся -\nеды с нового года хватит\nнадолго.',
    11: 'Ты наконец-то выспишься.\nНочные клубы будут все\nеще закрыты.',
    12: 'Настанет тот день, когда ты\nвыспишься.',
    13: 'Наконец ты выучишь\nанглийский. Главное не\nзабыть его до того, как\nоткроются границы.',
    14: 'Премия, отпуск впереди.\nОй, не та карта, попробуй\nеще раз.',
    15: 'Тебя ждет безлимитный\nинтернет без вирусов. Но\nтолько вместе с Yota.',
    16: 'Вместе с Yota у тебя не\nбудет никаких границ!',
    17: 'Снимется невезение с\nинстаграмных\nрозыгрышей: на тебя\nпосыпется халява.',
}


def index(request):
    """
    Индекс с общей карточкой для соцсети
    """
    return render(request, 'landings/fortune_teller_yota.html')


def read(request, prediction_id):
    """
    Страница одного ответа

    Создана для расшаривания в соцсетях и отличается карточкой соцсетей, на которой
    написан конкретный текст предсказания.
    """
    try:
        FORTUNE_TELLER_YOTA_DATA[int(prediction_id)]
    except (KeyError, TypeError):
        raise Http404()

    context = {
        'prediction_id': prediction_id,
        'prediction_social_card': '{}{}{}.png'.format(settings.MEDIA_URL, FORTUNE_TELLER_YOTA_SOCIAL_CARD_PATH, prediction_id)
    }

    return render(request, 'landings/fortune_teller_yota.html', context)


@ajax_request
def ajax_data(request):
    data = []

    for idx, text in FORTUNE_TELLER_YOTA_DATA.items():
        data.append({
            'id': idx,
            'text': text.replace('\n', ' '),
            'url': '{}{}'.format(settings.BASE_URL, reverse('fortune_teller_yota_read', kwargs={'prediction_id': idx})),
        })

    return data
