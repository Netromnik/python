# -*- coding: utf-8 -*-

import datetime

from django.http import Http404, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic import View

from irk.news.permissions import can_see_hidden
from irk.utils.helpers import iptoint, get_client_ip
from irk.utils.http import get_redirect_url

from irk.polls.models import Poll, PollChoice, PollVote, Quiz


def index(request):
    """Список годов с опросами в них"""

    years = Poll.objects.dates('start', 'year')

    context = {
        'years': years,
    }

    return render(request, 'polls/index.html', context)


def year(request, year):
    """Список голосований за год"""

    years = Poll.objects.dates('start', 'year')

    polls = Poll.objects.filter(start__year=year, end__lte=datetime.date.today())
    curr_year = year

    context = {
        'polls': polls,
        'years': years,
        'curr_year': curr_year,
    }

    return render(request, 'polls/year.html', context)


def results(request, year, poll_id):
    """Результаты голосования"""

    arh_link = False
    today = datetime.date.today()
    years = Poll.objects.dates('start', 'year')
    poll = get_object_or_404(Poll, start__year=int(year), pk=poll_id)

    if poll.end is not None and poll.end < today:
        voted = True
    else:
        voted = poll.voted(request)

    context = {
        'years': years,
        'today': today,
        'voted': voted,
        'poll': poll,
        'arh_link': arh_link,
        'year': int(year),
    }

    if request.is_ajax():
        return render(request, 'polls/snippets/poll.html', context)
    else:
        return render(request, 'polls/result.html', context)


@csrf_protect
def delete_vote(request):
    """Удалить голоса"""

    if not request.user.is_authenticated:
        return HttpResponse(u'Удаление доступно только пользователям')

    try:
        poll_id = int(request.POST.get('poll'))
    except (ValueError, TypeError):
        raise Http404(u'Нет параметров голосования')

    try:
        poll = Poll.objects.get(pk=poll_id)
        url = request.POST.get('next', poll.get_absolute_url())
    except Poll.DoesNotExist:
        raise Http404(u'Опрос не существует')

    choice_ids = PollChoice.objects.filter(poll_id=poll.pk).values_list('pk', flat=True)

    PollVote.objects.filter(user_id=request.user.pk, choice_id__in=choice_ids).delete()

    if request.is_ajax():
        response = HttpResponse('OK')
    else:
        response = redirect(url)

    return response


@csrf_protect
def vote(request, template='polls/snippets/poll.html'):
    """Голосование"""
    try:
        poll_id = int(request.POST.get('poll'))
        choice_id = int(request.POST.get('choice'))
    except (ValueError, TypeError):
        raise Http404(u'Нет параметров голосования')

    if 'brand' in request.POST:
        template = 'polls/tags/poll_block.html'

    try:
        choice = PollChoice.objects.get(pk=choice_id, poll=poll_id)
        url = request.POST.get('next', choice.poll.get_absolute_url())
    except PollChoice.DoesNotExist:
        raise Http404(u'Опрос не существует')
    else:
        if choice.poll.voted(request):
            if request.is_ajax():
                return HttpResponse(u'Вы уже проголосовали')

            return redirect(url)

        ip = iptoint(get_client_ip(request))
        vote = PollVote(choice=choice, ip=ip)
        if request.user.is_authenticated:
            vote.user = request.user
        vote.save()

        if request.is_ajax():
            new = bool(request.GET.get('new'))
            poll = Poll.objects.get(pk=poll_id)
            response = render(request, template, {'poll': poll, 'voted': True, 'arh_link': False, 'new': new,
                                                  'today': datetime.date.today()})
        else:
            response = redirect(url)

        # Для незарегистрированных пользователей храним еще и cookie
        if not request.user.is_authenticated:
            cookie = request.COOKIES.get('pl', '').split(':')
            cookie_values = []
            for poll in cookie:
                try:
                    cookie_values.append(int(poll))
                except (TypeError, ValueError):
                    continue

            cookie_values.append(poll_id)
            cookie_values = list(set(cookie_values))

            response.set_cookie('pl', ':'.join([str(x) for x in cookie_values]),
                                expires=datetime.datetime.now() + datetime.timedelta(days=365))

        return response


@csrf_protect
def vote_quiz(request):
    """Голосование в опросе"""

    url = get_redirect_url(request)
    response = redirect(url)

    votes = {}
    polls = request.POST.getlist('poll')
    for poll in polls:
        try:
            poll_id = int(poll)
            choices = request.POST.getlist('choice[{}]'.format(poll_id))
            votes[poll_id] = []
            for choice in choices:
                votes[poll_id].append(int(choice))
        except (ValueError, TypeError):
            raise Http404(u'Неверные параметры голосования')

    for poll_id, choices in votes.items():

        poll = get_object_or_404(Poll, pk=poll_id)
        if poll.voted(request):
            continue

        if not poll.multiple and len(choices) > 1:
            raise Http404(u'Неверное число допустимых вариантов')

        for choice_id in choices:
            try:
                choice = PollChoice.objects.get(pk=choice_id, poll=poll_id)
            except PollChoice.DoesNotExist:
                raise Http404(u'Опрос не существует')
            else:
                ip = iptoint(get_client_ip(request))
                vote = PollVote(choice=choice, ip=ip)
                if request.user.is_authenticated:
                    vote.user = request.user
                vote.save()

                # Для незарегистрированных пользователей храним еще и cookie
                if not request.user.is_authenticated:
                    cookie = request.COOKIES.get('pl', '').split(':')
                    cookie_values = []
                    for poll in cookie:
                        try:
                            cookie_values.append(int(poll))
                        except (TypeError, ValueError):
                            continue

                    cookie_values.append(poll_id)
                    cookie_values = list(set(cookie_values))

                    response.set_cookie('pl', ':'.join([str(x) for x in cookie_values]),
                                        expires=datetime.datetime.now() + datetime.timedelta(days=365))

    messages.success(request, u'Спасибо, за участие в опросе.', fail_silently=True)
    return response


def quiz_read(request, slug, template):
    """Страница опроса"""

    quiz = get_object_or_404(Quiz, slug=slug)

    return render(request, template, {'quiz': quiz, 'voted': quiz.voted(request)})


class PollReadView(View):
    """Страница голосования"""

    model = Poll

    def get(self, request, *args, **kwargs):
        self._parse_params()

        context = self._get_context()

        return render(request, self._get_template(), context)

    def _parse_params(self):
        """Разобрать параметры"""

        self._app_label = self.kwargs.get('app_label', 'news')
        self._poll_id = self.kwargs.get('poll_id')

    def _get_context(self):
        """Получить контекст"""

        poll = get_object_or_404(Poll, pk=self._poll_id)
        poll.choices_have_images = any(choice.image for choice in poll.choices)

        if not self._show_hidden() and poll.is_hidden:
            raise Http404(u'Объект скрыт')

        return {
            'poll': poll,
            'voted': self._is_voted(poll),
            'app_layout': u'{}/layout_cr.html'.format(self._get_template_dir()),
        }

    def _get_template(self):
        """Получить шаблон"""

        app_template = u'{}/poll/read.html'.format(self._get_template_dir())

        return [app_template, u'polls/read.html']

    def _get_template_dir(self):
        """Получить каталог где хранятся шаблоны раздела"""

        template_dir = self._app_label

        if template_dir == 'news':
            template_dir = 'news-less'

        return template_dir

    def _show_hidden(self):
        """Показывать скрытые?"""

        return can_see_hidden(self.request.user)

    def _is_voted(self, poll):
        """Пользователь уже проголосовал или голосование закончено"""

        today = datetime.date.today()

        if poll.end is not None and poll.end < today:
            return True
        else:
            return poll.voted(self.request)


read = PollReadView.as_view()
