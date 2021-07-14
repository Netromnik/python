# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from irk.newyear2014.forms import WishForm


def index(request):
    if request.POST:
        form = WishForm(request.POST)

        if form.is_valid():
            wish = form.save(commit=False)
            if request.user.is_authenticated:
                wish.user = request.user
            wish.save()

            return redirect(reverse('newyear2014.views.wish.sent'))

    else:
        form = WishForm()

    context = {
        'form': form
    }

    return render(request, 'newyear2014/wish/index.html', context)


def sent(request):
    """Пожелание отправлено"""

    return render(request, 'newyear2014/wish/sent.html', {})
