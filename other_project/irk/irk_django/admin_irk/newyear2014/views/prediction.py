# -*- coding: utf-8 -*-

import logging

from django.shortcuts import render, redirect

from irk.newyear2014.models import Prediction
from irk.newyear2014.user_options import PredictionOption
from irk.utils.http import JsonResponse

logger = logging.getLogger(__name__)


def index(request):

    prediction_option = PredictionOption(request)

    if prediction_option.value:
        prediction = Prediction.objects.get(pk=prediction_option.value)
    else:
        prediction = None
        if request.is_ajax() or request.POST:
            try:
                prediction = Prediction.objects.all().order_by('?')[0]
                prediction_option.value = prediction.pk
                prediction_option.save()
            except IndexError:
                prediction = None

        if request.is_ajax():
            return JsonResponse({'prediction': prediction.content})
        elif request.POST:
            return redirect('newyear2014.views.prediction.index')

    context = {
        'prediction': prediction.content if prediction else None
    }

    return render(request, 'newyear2014/prediction/index.html', context)
