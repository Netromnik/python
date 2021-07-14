# -*- coding: utf-8 -*-

"""Mixins для class-based views, связанных с участникам конкурсов"""

import os
import logging
import datetime
from pytils.dt import ru_strftime

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from irk.gallery.forms.helpers import gallery_formset

from irk.profiles.decorators import login_required
from irk.utils.notifications import tpl_notify

from irk.contests.forms import ParticipantForm
from irk.contests.models import Contest, Participant
from irk.contests.permissions import get_moderators

logger = logging.getLogger(__name__)


class ParticipantBaseViewMixin(View):
    """Mixin для создания/редактирования участников конкурсов

    Не должен использоваться напрямую

    Свойства класса::
        forms - соответствие типа конкурса форме
        model - редактируемая модель
        template_dir - директория шаблонов
        has_gallery_form - Нужно ли добавить к форме инлайн с галереей
    """

    contest = None
    model = Participant
    form_class = ParticipantForm
    template_dir = None
    has_gallery_form = False
    slug_url_kwarg = 'slug'
    by_csite = True  # Конкурс открыт не из раздела конкурсов

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ParticipantBaseViewMixin, self).dispatch(request, *args, **kwargs)

    def get(self, request, instance):
        """Обработка GET запроса

        Параметры::
            request: объект класса `django.http.HttpRequest'
            instance: объект класса ``self.model``. Может быть равен None, если объект еще не создан
        """
        contest = self.get_contest_object(request)

        form = self.form_class(instance=instance, initial=self.get_form_initial_data(request, instance))
        gallery_form = gallery_formset(instance=instance) if self.has_gallery() else None

        if Participant.objects.filter(contest=contest, user=request.user).exists():
            return render(request, 'contests/participant/add/rejected.html', {'object': instance, 'contest': contest})

        context = {
            'object': instance,
            'form': form,
            'gallery_form': gallery_form,
            'contest': contest,
        }
        context.update(self.extra_context(request, instance))

        return render(request, self.get_template(request, instance, context, create=False), context)

    def post(self, request, instance):
        """Обработка POST запроса

        Параметры::
            request: объект класса `django.http.HttpRequest'
            instance: объект класса ``self.model``. Может быть равен None, если объект еще не создан
        """

        contest = self.get_contest_object(request)

        form = self.form_class(
            request.POST, request.FILES, instance=instance, initial=self.get_form_initial_data(request, instance)
        )
        gallery_form = gallery_formset(
            request.POST, request.FILES, instance=instance
        ) if self.has_gallery() else None

        if form.is_valid() and (not gallery_form or gallery_form.is_valid()):
            obj = self.save_form(request, form)
            self.save_model(request, obj, form)

            if gallery_form:
                # Сохраняем изображения
                gallery_form = gallery_formset(request.POST, request.FILES, instance=obj)
                # Заново вызываем валидацию, чтобы получить заполненный `gallery_form.is_valid`
                gallery_form.is_valid()
                gallery_form.save()

            context = {
                'old_obj': instance,  # Старая версия объекта
                'contest': contest,
            }
            self.notifications(request, obj, context)

            if self.contest.type == Contest.TYPE_QUIZ:
                return redirect(self.contest)

            return self.response_completed(request, obj, context)

        else:
            # Если формы не валидны, записываем ошибки
            if not form.is_valid():
                logger.error('Base form is invalid in fields: %s' % ', '.join(['`%s`' % x for x in form.errors.keys()]),
                             extra={'request': request})

            if gallery_form and not gallery_form.is_valid():
                logger.error('Gallery formset is invalid.', extra={'request': request})
                gallery_non_form_errors = gallery_form.non_form_errors()
                if gallery_non_form_errors:
                    logger.error('Gallery formset non-form errors in fields: %s' % ', '.join(
                        ['`%s`' % x for x in gallery_non_form_errors.keys()]), extra={'request': request})

                for i in range(0, gallery_form.total_form_count()):
                    form_ = gallery_form.forms[i]
                    if not form_.errors:
                        continue
                    logger.error('Gallery form %d is invalid in fields: %s' % (
                        i, ', '.join(['`%s`' % x for x in form_.errors.keys()])), extra={'request': request})

        context = {
            'object': instance,
            'form': form,
            'gallery_form': gallery_form,
            'contest': contest,
        }
        context.update(self.extra_context(request, instance))

        return render(request, self.get_template(request, instance, context, create=False), context)

    def has_gallery(self):
        """Получение информаци о наличии галереи в форме участника конкурса."""

        return self.contest.type == Contest.TYPE_PHOTO

    def get_contest_object(self, request):
        """ Определение  объекта конкурса"""

        slug = self.kwargs.get(self.slug_url_kwarg, None)
        today = datetime.date.today()
        self.contest = get_object_or_404(
            Contest, slug=slug, date_start__lte=today, date_end__gte=today, user_can_add=True
        )

        return self.contest

    def extra_context(self, request, obj=None):
        """Дополнительные данные для передачи в шаблон

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
        """

        return {}

    def get_form_initial_data(self, request, obj=None, extra_context=None):
        """Начальные данные для формы"""

        profile = request.user.profile

        return {'full_name': profile.full_name, 'phone': profile.phone}

    def save_form(self, request, form):
        """Сохранение формы"""

        return form.save(commit=False)

    def get_model(self, request):
        return self.model

    def get_title(self, request, obj):
        try:
            title = obj.title
        except AttributeError:
            title = None

        if not title:
            if request.user.first_name or request.user.last_name:
                name = '%s %s' % (request.user.first_name, request.user.last_name)
            else:
                name = request.user.username
            title = u'Участник конкурса %s' % name

        return title

    def save_model(self, request, obj, form):
        """Сохранение объекта

        Внимание: этот метод должен обязательно сохранять объект!"""

        obj.contest = self.contest
        obj.user = request.user
        obj.title = self.get_title(request, obj)
        obj.save()

    def response_completed(self, request, obj, context):
        """Объект класса HttpResponse, возвращаемый в случае корректного создания объекта"""

        file_name = '%s_added.html' % self.contest.type
        template = os.path.join(self.template_dir, file_name)

        return render(request, template, context)

    def notifications(self, request, obj, extra_context=None):
        """Отправка уведомлений о завершенной операции пользователю

        Например, можно использовать django.contrib.messages и уведомления письмами"""

        tpl_notify(
            u'Новый участник конкурса на сайте Ирк.ру',
            'contests/notif/participant_add.html',
            {'participant': obj},
            request,
            list(get_moderators().values_list('email', flat=True))
        )

        if self.contest.type == Contest.TYPE_QUIZ:
            messages.success(
                request,
                u'Ваши ответы приняты. Результаты конкурса мы объявим {}.'.format(
                    ru_strftime('%d %B', self.contest.date_end, inflected=True)
                )
            )

    def get_template(self, request, obj, template_context, create):
        """Выбор шаблона для рендеринга

        Может возвращать список шаблонов, из которых будет выбран первый существующий

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
            template_context: словарь данных, который будет передан в шаблон
            create: если объект создается. будет равен True, иначе объект уже был создан раньше, и сейчас редактируется
        """

        if not self.template_dir:
            raise ImproperlyConfigured(u'Не указана директория шаблонов для вывода данных')

        file_name = '%s.html' % self.contest.type
        self.template_name = os.path.join(self.template_dir, file_name)

        return self.template_name
