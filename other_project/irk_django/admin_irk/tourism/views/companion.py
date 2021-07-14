# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from irk.tourism.forms.companion import CompanionForm, CompanionSearchForm
from irk.tourism.models import Companion
from irk.tourism.permissions import get_moderators, is_moderator

from irk.utils.notifications import tpl_notify


@login_required
def create_companion(request):
    """Добавть объявления о поиске компаньона"""

    if request.POST:
        form = CompanionForm(request.POST)
        if form.is_valid():
            companion = form.save(commit=False)
            companion.author = request.user
            companion.save()

            tpl_notify(u'Добавлено новое объявлние в попутчике туризма', 'tourism/companion/notif/create.html',
                       {'companion': companion}, request,
                       emails=get_moderators().values_list('email', flat=True))

            return redirect(reverse('tourism:companion:read', args=(companion.pk,)))
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['email'] = request.user.email
            if request.user.profile.phone:
                initial['phone'] = request.user.profile.phone

            fio = []
            if request.user.last_name:
                fio.append(request.user.last_name)
            if request.user.first_name:
                fio.append(request.user.first_name)
            if request.user.profile.mname:
                fio.append(request.user.profile.mname)
            initial['name'] = ' '.join(fio)

        form = CompanionForm(initial=initial)

    context = {
        'form': form,
    }

    return render(request, 'tourism/companion/create.html', context)


@login_required
def edit_companion(request, companion_id):
    """Добавть объявления о поиске компаньона"""

    companion = get_object_or_404(Companion, pk=int(companion_id))

    if companion.author == request.user or is_moderator(request.user):
        if request.POST:
            form = CompanionForm(request.POST, instance=companion)
            if form.is_valid():
                companion = form.save(commit=False)
                companion.author = request.user
                companion.save()

                tpl_notify(u'Отредактировано объявлние в попутчике туризма', 'tourism/companion/notif/edit.html',
                           {'companion': companion}, request,
                           emails=get_moderators().values_list('email', flat=True))

                return redirect(reverse('tourism:companion:read', args=(companion.pk,)))

        else:
            initial = {'email': request.user.email}
            if request.user.profile.phone:
                initial['phone'] = request.user.profile.phone

            fio = []
            if request.user.last_name:
                fio.append(request.user.last_name)
            if request.user.first_name:
                fio.append(request.user.first_name)
            if request.user.profile.mname:
                fio.append(request.user.profile.mname)
            initial['name'] = ' '.join(fio)

            form = CompanionForm(initial=initial, instance=companion)
    else:
        return HttpResponseForbidden()

    context = {
        'form': form,
    }

    return render(request, 'tourism/companion/edit.html', context)


def search_companion(request):
    """Поиск попутчика"""

    kwargs = {}

    try:
        my_composition = int(request.GET.get('my_composition'))
        if my_composition > 0:
            kwargs['find_composition'] = [my_composition, 0]
    except (TypeError, ValueError):
        my_composition = None

    try:
        find_composition = int(request.GET.get('find_composition'))
        if find_composition > 0:
            kwargs['my_composition'] = [find_composition, 0]
    except (TypeError, ValueError):
        find_composition = None

    try:
        place = request.GET.get('place')
        if place:
            kwargs['place'] = place
    except (TypeError, ValueError):
        place = None

    if kwargs:
        companions = Companion.search.filter(**kwargs)
    else:
        companions = Companion.objects.filter(visible=True)

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    paginate = Paginator(companions, 10)

    try:
        companions = paginate.page(page)
    except (EmptyPage, InvalidPage):
        companions = paginate.page(paginate.num_pages)

    initial = {
        'my_composition': my_composition,
        'find_composition': find_composition,
        'place': place
    }

    form = CompanionSearchForm(initial=initial)
    context = {
        'form': form,
        'companions': companions,
        'is_moderator': is_moderator(request.user),
        'place': place,
        'my_composition': my_composition,
        'find_composition': find_composition,
        'is_search': any([my_composition, find_composition, place]),
    }

    return render(request, 'tourism/companion/search.html', context)


def read_companion(request, companion_id):
    """Страница объявления"""

    if request.user.is_authenticated:
        companion = get_object_or_404(Companion, Q(pk=int(companion_id)), (Q(author=request.user.pk) | Q(visible=True)))
    else:
        companion = get_object_or_404(Companion, pk=int(companion_id), visible=True)

    context = {
        'companion': companion,
    }

    return render(request, 'tourism/companion/read.html', context)


@login_required
def my_companion(request):
    """Собственные объявления пользователя"""

    try:
        visible = int(request.GET.get("visible", 1))
    except ValueError:
        visible = 1

    companions = Companion.objects.filter(author=request.user.pk, visible=visible).order_by('-created')

    context = {
        'visible': visible,
        'companions': companions,
    }

    return render(request, 'tourism/companion/my.html', context)


@login_required
def delete_companion(request, companion_id):
    """Удаление объявления"""

    companion = get_object_or_404(Companion, pk=int(companion_id))
    if companion.author == request.user or is_moderator(request.user):
        companion.delete()
    else:
        return HttpResponseForbidden()

    return redirect(reverse('tourism:companion:my'))
