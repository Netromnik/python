# -*- coding: utf-8 -*-

import datetime
import logging

from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from irk.tourism.models import TourFirm, Tour, TourDate, TourBase, Hotel
from irk.tourism.forms import TourForm
from irk.tourism import permissions
from irk.tourism.helpers import parse_date, join_date, get_linked_firm

from irk.adv.permissions import get_sellers
from irk.phones.models import Sections, Firms
from irk.utils.notifications import tpl_notify
from irk.hitcounters.actions import hitcounter

logger = logging.getLogger(__name__)


def read_tour(request, tour_id):
    """Просмотр тура"""

    tour = get_object_or_404(Tour, pk=tour_id)
    can_edit = permissions.can_edit_tours(request.user, tour.firm)

    if tour.is_hidden and not permissions.can_edit_tours(request.user, tour.firm):
        return HttpResponseForbidden()

    hitcounter(request, tour)

    related_firm = None
    section = None
    try:
        related_firm = tour.firm.tourfirm
        content_type = ContentType.objects.get_for_model(related_firm)
        section = tour.firm.section.filter(content_type=content_type)[0]
    except (TourFirm.DoesNotExist, IndexError):
        try:
            related_firm = tour.firm.tourbase
            content_type = ContentType.objects.get_for_model(related_firm)
            section = tour.firm.section.filter(content_type=content_type)[0]
        except (TourBase.DoesNotExist, IndexError):
            try:
                related_firm = tour.firm.hotel
                content_type = ContentType.objects.get_for_model(related_firm)
                section = tour.firm.section.filter(content_type=content_type)[0]
            except (Hotel.DoesNotExist, IndexError):
                pass

    context = {
        'can_edit': can_edit,
        'related_firm': related_firm,
        'section': section,
        'tour': tour,
    }

    return render(request, 'tourism/tour/read.html', context)


def add_tour(request, section_slug, firm_id):
    """Добавляем тур"""

    section = get_object_or_404(Sections, slug=section_slug)
    firm = get_object_or_404(Firms, pk=firm_id)
    base_firm = firm

    if not permissions.can_edit_tours(request.user, base_firm):
        return HttpResponseForbidden()

    hot_tours = Tour.objects.filter(is_hot=True, firm=firm, is_hidden=False).count()

    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.firm_id = firm.pk
            instance = form.save()

            for date in form.cleaned_data['dates']:
                td = TourDate(tour=form.instance, date=date)
                td.save()

            emails = set(list(permissions.get_moderators().values_list('email', flat=True)) +
                         list(get_sellers().values_list('email', flat=True)))
            logger.debug('Sending notif about adding tour {0}'.format(instance.pk))
            tpl_notify(u'Добавлен тур', 'tourism/notif/tour/add.html',
                       {'object': instance}, request, emails=emails)

            return redirect(reverse('tourism:tour:success', args=(instance.pk, )))
    else:
        form = TourForm()

    title = u'Добавить тур'

    context = {
        'firm': firm,
        'hot_tours': hot_tours,
        'form': form,
        'base_firm': base_firm,
        'section': section,
        'title': title,
    }

    return render(request, 'tourism/tour/add.html', context)


def success_tour(request, tour_id):
    """Сообщение об отправки тура на модерацию"""
    tour = get_object_or_404(Tour, pk=tour_id)

    return render(request, 'tourism/tour/moderate.html', {'tour': tour})


def edit_tour(request, tour_id):
    """Редактирование тура"""

    section_slug = request.GET.get('section', None)
    if not section_slug:
        return HttpResponseNotFound()
    section = get_object_or_404(Sections, slug=section_slug)
    tour = get_object_or_404(Tour, pk=tour_id)
    firm = tour.firm

    if not permissions.can_edit_tours(request.user, firm):
        return HttpResponseForbidden()

    hot_tours = Tour.objects.filter(is_hot=True, firm=firm, is_hidden=False).count()

    if request.POST:
        form = TourForm(request.POST, request.FILES, instance=tour)

        if form.is_valid():
            instance = form.save(commit=False)

            # Отправлять на модерацию только при изменении названия, описания или фотки
            dirty_fields = instance.get_dirty_fields()
            if 'title' in dirty_fields or 'description' in dirty_fields or 'image' in dirty_fields:
                instance.is_hidden = True

            instance.save()

            if form.cleaned_data['dates']:
                TourDate.objects.filter(tour=tour).delete()
                for date in form.cleaned_data['dates']:
                    td = TourDate(tour=form.instance, date=date)
                    td.save()

            if instance.is_hidden:
                emails = set(list(permissions.get_moderators().values_list('email', flat=True)) +
                             list(get_sellers().values_list('email', flat=True)))

                logger.debug('Sending notif about editing tour {0}'.format(instance.pk))

                tpl_notify(u'Отредактирован тур', 'tourism/notif/tour/edit.html',
                           {'object': instance}, request, emails=emails)

                return redirect(reverse('tourism:tour:success', args=(instance.pk, )))
            else:
                return redirect(reverse('tourism:firm:read', args=('firms', firm.pk, )))

    else:
        form = TourForm(instance=tour)
        form.initial['dates'] = join_date([x.date for x in TourDate.objects.filter(tour=tour)])

    title = u'Редактирование тура'

    context = {
        'firm': firm,
        'hot_tours': hot_tours,
        'form': form,
        'title': title,
        'section': section,
        'tour': tour,
    }

    return render(request, 'tourism/tour/add.html', context)


def delete_tour(request, tour_id):
    """Удаление тура"""

    tour = get_object_or_404(Tour, pk=tour_id)
    rev = get_linked_firm(tour.firm).get_absolute_url()

    if permissions.can_edit_tours(request.user, tour.firm):
        # TODO: Периоды, галереи и привязки к отелям удаляются автоматически?
        tour.delete()

    return redirect(rev)


def update_status(request, tour_id):
    """Обновлние статуса тура"""

    section = get_object_or_404(Sections, slug=request.GET.get('section'))
    tour = get_object_or_404(Tour, pk=tour_id)
    rev = reverse('tourism:firm:read', args=(section.slug, tour.firm_id))

    if permissions.can_edit_tours(request.user, tour.firm):
        try:
            hot = int(request.GET.get('hot'), 0)
        except (TypeError, ValueError):
            hot = 0

        if hot > 0:
            # Делаем дополнительную проверку, сколько туров уже отмечены горячими
            amount = Tour.objects.filter(firm=tour.firm, is_hot=True, is_hidden=False).count()
            if amount >= 5:
                return redirect(rev)

    return redirect(rev)
