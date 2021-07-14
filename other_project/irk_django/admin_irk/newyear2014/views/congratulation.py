# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from irk.newyear2014.forms import CongratulationForm, AnonymousCongratulationForm
from irk.newyear2014.models import Congratulation
from irk.newyear2014.permissions import get_moderators

from irk.utils.notifications import tpl_notify


def index(request):
    initial = {}

    if request.POST:
        if request.user.is_authenticated:
            form = CongratulationForm(request.POST)
        else:
            form = AnonymousCongratulationForm(request.POST)
        if form.is_valid():
            congratulation = form.save(commit=False)
            if request.user.is_authenticated:
                congratulation.user = request.user
            congratulation.save()

            tpl_notify(u'Добавлено новое поздравление на сайте IRK.ru',
                       'newyear2014/congratulation/notif/create_moderator.html',
                       {'instance': congratulation}, request, emails=get_moderators().values_list('email', flat=True))

            return HttpResponseRedirect('.')

    else:
        if request.user.is_authenticated:
            fio = []
            if request.user.last_name:
                fio.append(request.user.last_name)
            if request.user.first_name:
                fio.append(request.user.first_name)
            if request.user.profile.mname:
                fio.append(request.user.profile.mname)
            if not fio:
                if request.user.profile.full_name:
                    fio.append(unicode(request.user.profile.full_name))
                else:
                    fio.append(unicode(request.user.profile))
            initial['sign'] = ' '.join(fio)

        if request.user.is_authenticated:
            form = CongratulationForm(initial=initial)
        else:
            form = AnonymousCongratulationForm(initial=initial)

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    congratulations = Congratulation.objects.filter(is_hidden=False).order_by('-created', '-id')

    paginate = Paginator(congratulations, 20)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(1)

    context = {
        'form': form,
        'objects': objects
    }

    return render(request, 'newyear2014/congratulation/index.html', context)
