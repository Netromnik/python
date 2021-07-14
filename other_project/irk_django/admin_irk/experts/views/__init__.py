# -*- coding: utf-8 -*-

import datetime
import random

from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.views.decorators.http import require_POST
from django.views.generic import View

from irk.gallery.forms.helpers import gallery_formset
from irk.experts.forms import ReplyForm, QuestionForm
from irk.experts.models import Expert, Question, Subscriber
from irk.experts import permissions
from irk.experts.permissions import get_moderators, is_moderator
from irk.utils.decorators import nginx_cached
from irk.utils.http import JsonResponse
from irk.utils.helpers import force_unicode, int_or_none
from irk.utils.notifications import tpl_notify
from irk.news.models import Category


@nginx_cached(60 * 5)
def current_expert(request):
    """ Виджет эксперта """

    now = datetime.datetime.now()
    cnt = Expert.objects.filter(stamp__lte=now, stamp_end__gte=now).count()
    if cnt > 0:
        expert = Expert.objects.filter(stamp__lte=now, stamp_end__gte=now).values('id', 'title', 'specialist',
            'questions_count', 'stamp_end', 'image', 'image_title')[random.randrange(0, cnt)]
    else:
        expert = None

    context = {
        'expert': expert,
    }

    return render(request, 'yandex/expert.html', context)


def search(request):
    """Поиск по экспертам"""

    q = force_unicode(request.GET.get('q', '').strip())

    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1

    try:
        limit = int(request.GET.get('limit', 20))
    except (TypeError, ValueError):
        limit = 20

    queryset = Expert.search.query({
        'q': q,
    })

    paginate = Paginator(queryset, limit)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(paginate.num_pages)

    context = {
        'q': q,
        'page': page,
        'limit': limit,
        'objects': objects,
    }

    return render(request, 'experts/search.html', context)


class ExpertList(View):
    """Список конференций"""

    model = Expert
    template = 'experts/index.html'
    ajax_template = 'experts/snippets/expert_list.html'
    # Количество объектов на странице
    page_limit_default = 10
    # Максимальное количество объектов на странице
    page_limit_max = page_limit_default

    def get(self, request, *args, **kwargs):
        self._parse_params()

        queryset = self._get_queryset()
        object_list, page_info = self._paginate(queryset)

        context = {
            'expert_list': object_list,
        }

        if self.request.is_ajax():
            return self._render_ajax_response(context, page_info)

        context.update(page_info)
        return render(request, self.template, context)

    def _parse_params(self):
        """Разобрать параметры переданные в url и в строке запроса"""

        # Параметры пагинации
        start_index = int_or_none(self.request.GET.get('start')) or 0
        self._start_index = max(start_index, 0)
        page_limit = int_or_none(self.request.GET.get('limit')) or self.page_limit_default
        self._page_limit = min(page_limit, self.page_limit_max)

    def _get_queryset(self, **kwargs):
        """Вернуть queryset с предложениями"""

        queryset = self.model.objects.order_by('-stamp', '-published_time', '-id')

        if not self._show_hidden:
            queryset = queryset.filter(is_hidden=False)

        return queryset

    @cached_property
    def _show_hidden(self):
        """Показывать скрытые?"""

        return is_moderator(self.request.user)

    def _paginate(self, queryset):
        """
        Разбить queryset на страницы.
        :param QuerySet queryset: результирующий набор данных
        :return: список объектов на странице и информация о странице
        :rtype: tuple
        """

        object_count = queryset.count()

        end_index = self._start_index + self._page_limit
        end_index = min(end_index, object_count)
        object_list = queryset[self._start_index:end_index]

        page_info = {
            'has_next': object_count > end_index,
            'next_start_index': end_index,
            'next_limit': min(self.page_limit_default, object_count - end_index)
        }

        return object_list, page_info

    def _render_ajax_response(self, context, page_info):
        """
        Отправить ответ на Ajax запрос
        :param dict context: контекст шаблона
        :param dict page_info: информация о странице
        """

        return JsonResponse(dict(
            html=render_to_string(self.ajax_template, context),
            **page_info
        ))


index = ExpertList.as_view()


def read(request, category_alias, expert_id):
    """Просмотр пресс-конференции"""

    category = get_object_or_404(Category, slug=category_alias)
    expert = get_object_or_404(Expert, category=category, pk=expert_id)

    # Страница комментариев
    try:
        page = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page = 1

    # PK вопроса, на который отвечает ведущий конференции
    try:
        question_id = int(request.GET.get('question'))
    except (TypeError, ValueError):
        question_id = None

    # PK вопроса, который будет выделен в списке вопросов
    try:
        highlight_id = int(request.GET.get('highlight'))
    except (TypeError, ValueError):
        highlight_id = None

    # Всякие разрешения для текущего пользователя
    can_ask = request.user != expert.user  # Возможность задавать вопросы
    can_reply = permissions.can_reply(request.user, expert)  # Возможность отвечать на вопросы
    can_delete = permissions.can_delete(request.user)  # Возможность удалять вопросы

    # Форма ответа на сообщение ведущим конференции
    if question_id:
        question = expert.questions.get(pk=question_id)
        initial = {
            'question': question_id,
            'answer': question.answer
        }
        gallery_form = gallery_formset(instance=question)
        reply_form = ReplyForm(initial=initial)
        del initial

        if request.is_ajax():
            # Может подгружаться AJAX'ом, поэтому в этом случае рендерим ее отдельно, и передаем
            context = {
                'expert': expert,
                'reply_form': reply_form,
                'gallery_form': gallery_form,
            }

            return render(request, 'experts/snippets/answer_form.html', context)

    # Список вопросов
    paginate = Paginator(expert.questions, 20)

    try:
        objects = paginate.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginate.page(paginate.num_pages)

    if expert.stamp_end >= datetime.date.today() and can_ask:
        question_form = QuestionForm()
    else:
        question_form = None

    # Подписан ли пользоватль на эту конференцию
    if request.user.is_authenticated:
        is_subscribed = Subscriber.objects.filter(expert=expert, user=request.user).exists()
    else:
        is_subscribed = False

    context = {
        'category': category,
        'expert': expert,
        'objects': objects,
        'highlight_id': highlight_id,
        'can_reply': can_reply,
        'can_delete': can_delete,
        'question_form': question_form,
        'is_subscribed': is_subscribed,
        'is_moderator': is_moderator(request.user),
    }

    return render(request, 'experts/read.html', context)


@require_POST
def question_create(request, category_alias, expert_id):
    """Написание вопроса к пресс-конференции"""

    category = get_object_or_404(Category, slug=category_alias)
    expert = get_object_or_404(Expert, category=category, pk=expert_id)

    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    can_ask = expert.stamp_end >= datetime.date.today() and expert.user != request.user

    if not can_ask:
        # TODO: может другое что лучше возвращать?
        return HttpResponseForbidden()

    form = QuestionForm(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.expert = expert
        question.user = request.user
        question.created = datetime.datetime.now()
        question.save()

        tpl_notify(u'Новый вопрос в пресс-конференции на сайте Ирк.ру',
                   'experts/notif/new_question.html', {'question': question, 'expert': expert},
                   request, list(get_moderators().values_list('email', flat=True)))

        return HttpResponseRedirect(expert.get_absolute_url() + '?highlight=%s' % question.pk)
    return HttpResponseForbidden()


def question_reply(request, category_alias, expert_id):
    """Ответ на вопрос в конференции"""

    category = get_object_or_404(Category, slug=category_alias)
    expert = get_object_or_404(Expert, category=category, pk=expert_id)

    if not permissions.can_reply(request.user, expert):
        return HttpResponseForbidden()

    if request.POST:
        reply_form = ReplyForm(request.POST)
        try:
            question_post_id = int(request.POST.get('question'))
            gallery_form = gallery_formset(request.POST, request.FILES,
                                           instance=Question.objects.get(pk=question_post_id))
        except (TypeError, ValueError, forms.ValidationError):
            try:
                gallery_form = gallery_formset(request.POST, request.FILES, instance=Question())
            except forms.ValidationError:
                gallery_form = None

        if reply_form.is_valid() and gallery_form.is_valid():
            question = reply_form.cleaned_data['question']
            is_new_answer = bool(question.answer)  # На вопрос раньше не отвечали
            question.answer = reply_form.cleaned_data['answer']

            question.save()

            gallery_form = gallery_formset(request.POST, request.FILES, instance=question)
            # Заново вызываем валидацию, чтобы получить заполненный `gallery_form.is_valid`
            gallery_form.is_valid()
            gallery_form.save()

            # Составляем список получателей уведомлений об ответе
            recipients = []
            try:
                recipients.append(question.user.email)
            except User.DoesNotExist:
                pass
            for q in question.identical.all():
                try:
                    recipients.append(q.user.email)
                except User.DoesNotExist:
                    continue

            recipients = list(set(recipients))

            if is_new_answer:
                tpl_notify(u'Ответ на ваш вопрос в пресс-конференции на сайте Ирк.ру',
                           'experts/notif/new_answer.html', {'question': question, 'expert': expert},
                           request, recipients)
            else:
                tpl_notify(u'Ответ на ваш вопрос в пресс-конференции на сайте Ирк.ру изменен',
                           'experts/notif/edit_answer.html', {'question': question, 'expert': expert},
                           request, recipients)

            # Делаем редирект на ту страницу с вопросами. на которой мы были до этого
            redirect_page = (expert.questions.filter(created__gt=question.created).count() / 20) + 1

            return HttpResponseRedirect(
                '%s?page=%s#question-%s' % (expert.get_absolute_url(), redirect_page, question.pk))

        return HttpResponseBadRequest()

    else:
        # Пользователь может отвечать на вопросы, и нажал ссылку «ответить»
        return HttpResponseForbidden()


def question_delete(request, category_alias, expert_id, question_id):
    """Удаление вопроса в пресс-конференции"""

    category = get_object_or_404(Category, slug=category_alias)
    expert = get_object_or_404(Expert, category=category, pk=expert_id)
    question = get_object_or_404(Question, expert=expert, pk=question_id)

    if permissions.can_delete(request.user):
        question.delete()

    return redirect(expert.get_absolute_url())


def subscription(request):
    """Подписка на уведомление об ответах на конференцию"""

    if request.POST and request.is_ajax():
        try:
            expert_id = int(request.POST.get('id', 0))
            expert = Expert.objects.get(pk=expert_id)
        except (Expert.DoesNotExist, TypeError, ValueError):
            return HttpResponseBadRequest()

        if request.user.is_authenticated:
            user = request.user
            email = request.user.email
        else:
            user = None
            email = request.POST.get('email', '')
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'error': u'Неверный формат почтового адреса'})

        Subscriber.objects.get_or_create(user=user, email=email, expert=expert)

        return JsonResponse({'success': True})

    return HttpResponseForbidden()
