# -*- coding: utf-8 -*-

from django.shortcuts import render

from irk.newyear2014.forms import GuruForm
from irk.newyear2014.models import GuruAnswer


def index(request):
    answer = None
    if request.POST:
        form = GuruForm(request.POST)

        gender = form.data['gender']
        age = form.data['age']

        try:
            age = GuruAnswer.AGE_AFTER_30 if int(age) > 30 else GuruAnswer.AGE_UNDER_30
        except (TypeError, ValueError):
            age = GuruAnswer.AGE_UNDER_30

        try:
            answer = GuruAnswer.objects.filter(age=age, gender=gender).order_by('?')[0]
        except IndexError:
            answer = None

    else:
        form = GuruForm()

    context = {
        'form': form,
        'answer': answer
    }

    return render(request, 'newyear2014/guru/index.html', context)

