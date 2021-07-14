# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from irk.afisha import permissions as afisha_permissions
from irk.afisha import settings as afisha_settings
from irk.afisha.forms import CustomEventForm, PeriodForm
from irk.afisha.models import Event, Period, EventGuide, Sessions, Announcement, Prism
from irk.afisha.views.events import EventsListView
from irk.afisha.settings import COMMERCIAL_EVENT_DEFAULT_PRISM
from irk.contests.views.base.list import ListContestBaseView
from irk.contests.views.base.participant_create import CreateParticipantBaseView
from irk.contests.views.base.participant_read import ReadParticipantBaseView
from irk.contests.views.base.read import ReadContestBaseView
from irk.gallery.forms.helpers import gallery_formset
from irk.utils.helpers import get_client_ip, iptoint
from irk.utils.notifications import tpl_notify
from irk.phones.permissions import is_moderator

contests_read = ReadContestBaseView.as_view(template_name='afisha/contests/read.html')
contests_list = ListContestBaseView.as_view(template_name='afisha/contests/list.html')
participant_read = ReadParticipantBaseView.as_view(template_name='afisha/contests/participant/read.html')
participant_create = CreateParticipantBaseView.as_view(template_dir='afisha/contests/participant/add')


def create(request):
    """Добавление нового события пользователями"""

    from irk.afisha.order_helpers import EventOrderHelper

    PeriodFormSet = formset_factory(PeriodForm, extra=1)

    if request.POST:
        event_form = CustomEventForm(request.POST, request.FILES,)
        gallery = gallery_formset(request.POST, request.FILES, instance=Event())
        period_formset = PeriodFormSet(request.POST)

        if event_form.is_valid() and gallery.is_valid() and period_formset.is_valid():

            price = event_form.cleaned_data.get('price', '')
            announcement_index_start_date = event_form.cleaned_data.get('announcement_index_start_date')
            announcement_index_end_date = event_form.cleaned_data.get('announcement_index_end_date')

            # Сохранение данных события
            event = event_form.save()
            event.is_user_added = True
            event.is_hidden = True
            event.author_ip = iptoint(get_client_ip(request))
            event.save()

            # Добавление призмы коммерческим материалам
            if event.is_commercial:
                event.prisms.add(Prism.objects.get(pk=COMMERCIAL_EVENT_DEFAULT_PRISM))

            # Сохранение платных анонсов
            announcement_index_count = 0
            if announcement_index_start_date and announcement_index_end_date:
                delta = announcement_index_end_date - announcement_index_start_date
                announcement_index_count = delta.days + 1
                Announcement.objects.create(
                    place=Announcement.PLACE_AFISHA_INDEX,
                    event=event,
                    start=announcement_index_start_date,
                    end=announcement_index_end_date,
                )

            # Сохранение периодов
            event_guide = EventGuide.objects.create(event=event)
            for period_form in period_formset.forms:
                date = period_form.cleaned_data.get('date')
                time = period_form.cleaned_data.get('time')
                period = Period.objects.create(
                    event_guide=event_guide,
                    price=price,
                    start_date=date,
                    end_date=date,
                )
                Sessions.objects.create(period=period, time=time)

            # Создать заказ на оплату для комерческого события
            periods = Period.objects.filter(event_guide__event_id=event.pk)
            if event.is_commercial:
                order = EventOrderHelper(event, request)
                amount = periods.count() * afisha_settings.COMMERCIAL_EVENT_PRICE + \
                         announcement_index_count * afisha_settings.COMMERCIAL_EVENT_CAROUSEL_PRICE
                order.create_order({'price': amount, 'event_id': event.pk})

            announcements = Announcement.objects.filter(event_id=event.pk)

            galley_form = gallery_formset(request.POST, request.FILES, instance=event)
            # Заново вызываем валидацию, чтобы получить заполненный `gallery_form.is_valid`
            galley_form.is_valid()
            galley_form.save()
            tpl_notify(u'Новое событие в афише', 'afisha/notif/new_event.html',
                       {'event': event, 'periods': periods, 'contacts': event_form.cleaned_data.get('contacts'),
                        'announcements': announcements},
                       request, afisha_permissions.get_moderators().values_list('email', flat=True))

            if event.is_commercial:
                return HttpResponseRedirect(reverse('afisha:commercial_event_created'))
            return HttpResponseRedirect(reverse('afisha:event_created'))

    else:
        event_form = CustomEventForm()
        gallery = gallery_formset(instance=Event())
        period_formset = PeriodFormSet()

    context = {
        'form': event_form,
        'gallery': gallery,
        'period_formset': period_formset,
        'prices': {'commercial_event': afisha_settings.COMMERCIAL_EVENT_PRICE,
                   'commercial_event_carousel': afisha_settings.COMMERCIAL_EVENT_CAROUSEL_PRICE},
        'is_moderator': is_moderator(request.user),
    }

    return render(request, 'afisha/event/create.html', context)


def created(request, is_commercial=False):
    """Страница с сообщением о том, что событие добавлено"""

    return render(request, 'afisha/event/created.html', {'is_commercial': is_commercial})


index = EventsListView.as_view(template_name='afisha/index.html')
