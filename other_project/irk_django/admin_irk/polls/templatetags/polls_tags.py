# -*- coding: utf-8 -*-

import datetime

from django import template
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext, Variable
from django.template.loader import render_to_string

from irk.news.models import BaseMaterial
from irk.polls.models import Poll
from irk.utils.templatetags import parse_arguments

__all__ = ('poll', 'related_poll')

register = template.Library()


class PollNode(template.Node):
    def render(self, context):
        today = datetime.date.today()
        request = context['request']

        try:
            # Ротация среди открытых голосований
            poll = Poll.objects.filter(sites=request.csite, start__lte=today, end__gte=today,
                                       target_ct__isnull=True).order_by('?')[0]
        except IndexError:
            try:
                # Последнее закрытое
                poll = Poll.objects.filter(sites=request.csite, end__lt=today,
                                           target_ct__isnull=True).order_by('-end')[0]
            except IndexError:
                poll = None

        if not poll:
            return render_to_string('polls/tags/poll_block.html', {'poll': None, 'voted': True},
                                    request=request)
        context['poll'] = poll
        if poll.end is not None and poll.end < today:
            voted = True
        else:
            voted = poll.voted(request)

        return render_to_string('polls/tags/poll_block.html', {'poll': poll, 'voted': voted, 'today': today},
                                request=request)


@register.tag
def poll(parser, token):
    """Блок с голосованием для текущего раздела"""

    return PollNode()


class PollObjNode(template.Node):
    def __init__(self, obj):
        self._obj = Variable(obj)

    def render(self, context):
        try:
            request = context['request']
        except KeyError:
            raise template.VariableDoesNotExist(u'Для отображения голосования в шаблоне должен быть доступен request')

        poll = self._obj.resolve(context)

        today = datetime.date.today()

        if poll.end is not None and poll.end < today:
            voted = True
        else:
            voted = poll.voted(request)

        return render_to_string('polls/tags/poll_block_quiz.html', {'poll': poll, 'voted': voted, 'today': today})


@register.tag
def pollobj(parser, token):
    """Вывод конкретного голосования"""

    bits = token.split_contents()

    poll = bits[1]

    return PollObjNode(poll)


class RelatedPollNode(template.Node):
    def __init__(self, obj, template):
        self._obj = Variable(obj)
        self._template = template or 'polls/snippets/related_poll_less.html'

    def render(self, context):
        try:
            request = context['request']
        except KeyError:
            raise template.VariableDoesNotExist(u'Для отображения голосования в шаблоне должен быть доступен request')

        obj = self._obj.resolve(context)

        if issubclass(obj.__class__, BaseMaterial):
            obj = obj.uncast()

        ct = ContentType.objects.get_for_model(obj)
        today = datetime.date.today()

        try:
            poll = Poll.objects.filter(target_ct=ct, target_id=obj.pk, start__lte=today).order_by('-end')[0]
            poll.choices_have_images = any(choice.image for choice in poll.choices)
            if poll.end is not None and poll.end < today:
                voted = True
            else:
                voted = poll.voted(request)
        except IndexError:
            template_context = {'poll': None, 'voted': True}
        else:
            template_context = {'poll': poll, 'voted': voted, 'today': today}

        return render_to_string(self._template, template_context, request)


@register.tag
def related_poll(parser, token):
    """Вывод голосования, привязанного к объекту

    Примеры использования::
        {% related_poll news_obj %}
        {% related_poll news_obj 'polls/new-template.html' %}
    """

    bits = token.split_contents()[1:]
    try:
        obj, template_name = bits
        template_name = template_name.strip('"').strip('\'')
    except ValueError:
        obj = bits[0]
        template_name = None

    return RelatedPollNode(obj, template_name)


class QuizNode(template.Node):
    def __init__(self, quiz, *args, **kwargs):
        self._quiz = quiz
        self._args = args
        self._kwargs = kwargs

    def render(self, context):
        request = context.get('request')
        if not request:
            raise template.VariableDoesNotExist(u'Request object is required')

        quiz = self._quiz.resolve(context)
        if not quiz:
            raise template.VariableDoesNotExist(u'Quiz object is required')

        ct = ContentType.objects.get_for_model(quiz)
        today = datetime.date.today()
        polls = Poll.objects.filter(target_ct=ct, target_id=quiz.pk, start__lte=today).order_by('-end', 'pk')

        return render_to_string(
            'polls/tags/quiz.html',
            {'polls': polls, 'voted': quiz.voted(request), 'quiz_url': quiz.get_absolute_url()},
            request=request
        )


@register.tag
def quiz(parser, token):
    """Блок с голосованием для текущего раздела"""

    bits = token.split_contents()
    args, kwargs = parse_arguments(parser, bits[1:])

    return QuizNode(*args, **kwargs)
