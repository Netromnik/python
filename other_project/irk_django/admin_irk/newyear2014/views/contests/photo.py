# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponseRedirect, Http404
from django.views import generic
from django.shortcuts import get_object_or_404, render

from irk.newyear2014.models import PhotoContest, PhotoContestParticipant
from irk.newyear2014.forms import PhotoContestAnonymousParticipantForm, PhotoContestAuthenticatedParticipantForm


class ListView(generic.ListView):
    model = PhotoContest
    template_name = 'newyear2014/contests/photo/index.html'

    def get_queryset(self):
        today = datetime.date.today()

        return self.model.objects.filter(date_start__lte=today, date_end__gte=today).order_by('id')

index = ListView.as_view()


class DetailView(generic.DetailView):
    model = PhotoContest
    template_name = 'newyear2014/contests/photo/read.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['participants'] = kwargs['object'].participants.filter(is_visible=True).order_by('-id')
        return context

read = DetailView.as_view()


def create(request, pk):
    contest = get_object_or_404(PhotoContest, pk=pk)

    if not contest.can_rate or not contest.user_can_add:
        raise Http404

    initial = {}
    if request.user.is_authenticated:
        form_cls = PhotoContestAuthenticatedParticipantForm
        initial['name'] = request.user.get_full_name()
    else:
        form_cls = PhotoContestAnonymousParticipantForm

    if request.POST:
        form = form_cls(request.POST, request.FILES, initial=initial)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.contest = contest
            if request.user.is_authenticated:
                instance.user = request.user
            instance.save()

            return HttpResponseRedirect(instance.get_absolute_url())

    else:
        form = form_cls(initial=initial)

    context = {
        'contest': contest,
        'form': form,
    }

    return render(request, 'newyear2014/contests/photo/create.html', context)


def participant(request, pk, participant_id):
    obj = get_object_or_404(PhotoContestParticipant, contest_id=pk, id=participant_id, is_visible=True)
    all_participants = PhotoContestParticipant.objects.filter(contest=obj.contest, is_visible=True)
    participants = PhotoContestParticipant.objects.filter(contest=obj.contest, is_visible=True).exclude(id=obj.id).order_by('?')[:8]

    try:
        next_ = all_participants.filter(id__gt=obj.id).order_by('id')[0]
    except IndexError:
        next_ = all_participants.order_by('id')[0]

    try:
        previous = all_participants.filter(id__lt=obj.id).order_by('-id')[0]
    except IndexError:
        previous = all_participants.order_by('-id')[0]

    context = {
        'object': obj,
        'participants': participants,
        'next': next_,
        'previous': previous,
    }

    return render(request, 'newyear2014/contests/photo/participant.html', context)
