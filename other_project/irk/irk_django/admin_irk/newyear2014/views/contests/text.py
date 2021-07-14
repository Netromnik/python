# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponseRedirect, Http404
from django.views import generic
from django.shortcuts import get_object_or_404, render

from irk.newyear2014.models import TextContest, TextContestParticipant
from irk.newyear2014.forms import TextContestAnonymousParticipantForm, TextContestAuthenticatedParticipantForm


class ListView(generic.ListView):
    model = TextContest
    template_name = 'newyear2014/contests/text/index.html'

    def get_queryset(self):
        today = datetime.date.today()

        return self.model.objects.filter(date_start__lte=today, date_end__gte=today).order_by('id')

index = ListView.as_view()


class DetailView(generic.DetailView):
    model = TextContest
    template_name = 'newyear2014/contests/text/read.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['participants'] = kwargs['object'].participants.filter(is_visible=True).order_by('-id')
        return context

read = DetailView.as_view()


def create(request, pk):
    contest = get_object_or_404(TextContest, pk=pk)

    if not contest.can_rate or not contest.user_can_add:
        raise Http404

    initial = {}
    if request.user.is_authenticated:
        form_cls = TextContestAuthenticatedParticipantForm
        initial['name'] = request.user.get_full_name()
    else:
        form_cls = TextContestAnonymousParticipantForm

    if request.POST:
        form = form_cls(request.POST, request.FILES)
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

    return render(request, 'newyear2014/contests/text/create.html', context)


def participant(request, pk, participant_id):
    obj = get_object_or_404(TextContestParticipant, contest_id=pk, id=participant_id, is_visible=True)
    all_participants = TextContestParticipant.objects.filter(contest=obj.contest, is_visible=True)
    participants = all_participants.exclude(id=obj.id).order_by('?')[:8]

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

    return render(request, 'newyear2014/contests/text/participant.html', context)
