# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse

from irk.landings.settings import PREDICTION_SOCIAL_CARD_PATH
from irk.utils.http import ajax_request

PREDICTION_DATA = {
    1: "Займись своим здоровьем, оно еще пригодится.",
    2: "Трудное, не есть невозможное.\nРезультат впереди. Не сдавайся!",
    3: "Трать больше времени на себя.",
    4: "Интересуйся своей жизнью больше, чем чужой.",
    5: "Не пытайся всё успеть. Расслааабься.",
    6: "Смейся трудностям в лицо! ",
    7: "Не сиди сложа руки, действуй!",
    8: "Всем известно, как Новый год встретишь,\nтак его и проведешь.\nНе подкачай! Не опозорься!",
    9: "Пей больше воды.\nОна освежает мысли и наполняет тело энергией.",
    10: "Пей больше не воды.\nМысли не освежит, но станет веселее.",
    11: "Перестань худеть и все получится.",
    12: "Боишься позвонить, но очень хочется?\nПора, все изменится к лучшему.",
    13: "В июле тебя ждет Байкал.\nА в мае – майские праздники.",
    14: "Лучше целоваться, чем волноваться.",
    15: "Есть специальный рецепт счастья для тебя.\nОтправить в Ирк.ру бутылочку шампанского.",
    16: "Тебе срочно нужно побаловать себя покупками.",
    17: "Настало время любви!",
    18: "Пора провести отпуск как ты хочешь.\nСпланируй и все получится.",
    19: "Не забудьте, что во всем должна быть мера.",
    20: "Ты молодец! Год будет отличным."
}


def index(request):
    """
    Индекс с общей карточкой для соцсети
    """
    return render(request, 'landings/predictions.html')


def read(request, prediction_id):
    """
    Страница одного ответа

    Создана для расшаривания в соцсетях и отличается карточкой соцсетей, на которой
    написан конкретный текст предсказания.
    """
    try:
        PREDICTION_DATA[int(prediction_id)]
    except (KeyError, TypeError):
        raise Http404()

    context = {
        'prediction_id': prediction_id,
        'prediction_social_card': '{}{}{}.png'.format(settings.MEDIA_URL, PREDICTION_SOCIAL_CARD_PATH, prediction_id)
    }

    return render(request, 'landings/predictions.html', context)


@ajax_request
def ajax_data(request):
    data = []

    for idx, text in PREDICTION_DATA.items():
        data.append({
            'id': idx,
            'text': text.replace('\n', ' '),
            'url': '{}{}'.format(settings.BASE_URL, reverse('predictions_read', kwargs={'prediction_id': idx})),
        })

    return data
