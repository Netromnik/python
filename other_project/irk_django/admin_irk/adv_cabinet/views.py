# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from irk.adv.models import Banner
from irk.adv_cabinet.helpers import get_ba_clients
from irk.adv_cabinet.permissions import business_account_required


@business_account_required
def index(request):
    """Первая страница"""

    return redirect('adv_cabinet:companies')


@business_account_required
def companies(request):
    """Список компаний"""

    context = {
        'business_account': request.user.profile.business_account,
        'clients': get_ba_clients(request),
    }

    return render(request, 'adv_cabinet/companies.html', context)


@business_account_required
def banner_list(request):
    """Список размещений"""

    return render(request, 'adv_cabinet/banners.html', {})


@business_account_required
def banner_details(request, banner_id):
    """Размещение"""

    banner = get_object_or_404(Banner, pk=banner_id)

    if banner.client not in get_ba_clients(request):
        raise Http404

    context = {
        'banner': banner,
        'files': banner.files,
    }

    return render(request, 'adv_cabinet/banner.html', context)
