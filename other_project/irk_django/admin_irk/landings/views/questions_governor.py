# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.shortcuts import render

from irk.landings.forms import QuestionsGovernorForm
from irk.utils.notifications import tpl_notify
from irk.utils.http import JsonResponse


def index(request):
    """
    Задать вопрос губернатору
    """

    if request.is_ajax() and request.POST:
        form = QuestionsGovernorForm(data=request.POST)
        if form.is_valid():
            question = form.save()
            tpl_notify(
                'Вопрос с сайта IRK.ru',
                'landings/notif/questions_governor.html',
                {'question': question},
                request,
                emails=['varlogin@gmail.com', 'questions@tvoyirk.ru'])
            return JsonResponse({'result': 'ok'})
        else:
            return JsonResponse({'result': 'error', 'errors': form.errors})
    else:
        form = QuestionsGovernorForm()

    return render(request, 'landings/questions_governor.html', {'form': form})
