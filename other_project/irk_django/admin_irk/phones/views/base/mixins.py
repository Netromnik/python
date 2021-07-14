# -*- coding: utf-8 -*-

"""Mixins для class-based views, связанных с фирмами"""

__all__ = ('FirmBaseViewMixin',)

import logging

from django.views.generic.base import View
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator

from irk.profiles.decorators import login_required
from irk.gallery.forms.helpers import gallery_formset
from irk.phones.forms import FirmForm, AddressFormSet
from irk.phones.models import Address, Firms as Firm

logger = logging.getLogger(__name__)


class FirmBaseViewMixin(View):
    """Mixin для создания/редактирования фирм

    Не должен использоваться напрямую

    Свойства класса::
        form - форма создания/редактирования. Используется методом get_form
        address_form - форма создания/редактирования адреса. Используется методом get_address_form
        model - редактируемая модель
        template - имя шаблона с формой
        has_gallery_form - Нужно ли добавить к форме инлайн с галереей
    """

    form = FirmForm
    address_form = AddressFormSet
    model = Firm
    template = None
    has_gallery_form = True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(FirmBaseViewMixin, self).dispatch(request, *args, **kwargs)

    def get(self, request, instance):
        """Обработка GET запроса

        Параметры::
            request: объект класса `django.http.HttpRequest'
            instance: объект класса ``self.model``. Может быть равен None, если объект еще не создан
        """

        form_class = self.get_form(request, instance)
        address_form_class = self.get_address_form(request, instance)

        form = form_class(instance=instance, initial=self.get_form_initial_data(request, instance))
        address_form = address_form_class(instance=instance)
        gallery_form = gallery_formset(instance=instance) if self.has_gallery_form else None

        if instance.pk:
            logger.debug('GET request for %s with PK %s' % (instance.__class__.__name__, instance.pk))
        else:
            logger.debug('GET request for %s without PK' % instance.__class__.__name__)

        context = {
            'object': instance,
            'form': form,
            'address_form': address_form,
            'gallery_form': gallery_form,
        }
        context.update(self.extra_context(request, instance))

        return render(request, self.get_template(request, instance, context, create=False), context)

    def post(self, request, instance):
        """Обработка POST запроса

        Параметры::
            request: объект класса `django.http.HttpRequest'
            instance: объект класса ``self.model``. Может быть равен None, если объект еще не создан
        """

        if instance.pk:
            logger.debug('POST request for %s with PK %s' % (instance.__class__.__name__, instance.pk))
        else:
            logger.debug('POST request for %s without PK' % instance.__class__.__name__)

        form_class = self.get_form(request, instance)
        address_form_class = self.get_address_form(request, instance)

        form = form_class(request.POST, request.FILES, instance=instance,
                          initial=self.get_form_initial_data(request, instance))

        address_form = address_form_class(request.POST, request.FILES, instance=instance)
        # gallery_form = gallery_formset(request.POST, request.FILES,
        #                                instance=instance) if self.has_gallery_form else None
        gallery_form = self.get_gallery_form(request, instance) if self.has_gallery_form else None

        if form.is_valid() and address_form.is_valid() and (not gallery_form or gallery_form.is_valid()):

            obj = self.save_form(request, form)
            self.save_model(request, obj, form)

            # Сохранение адресов
            address_form = address_form_class(request.POST, request.FILES, instance=obj)

            # Еще раз вызываем валидацию, чтобы получить `address_form.cleaned_data`
            address_form.is_valid()
            address_form.save()

            # Удаление отмеченных адресов
            existing_addr_ids = list(obj.address_set.all().values_list('pk', flat=True))
            delete_addrs = []
            for addr_id in request.POST.getlist('delete_addr'):
                try:
                    addr_id = int(addr_id)
                    # Удаляем только те адреса, которые действительно относятся к этой фирме
                    if addr_id in existing_addr_ids:
                        delete_addrs.append(addr_id)
                except (TypeError, ValueError):
                    continue
            if delete_addrs:
                logger.debug('Deleting old addresses: %s' % ', '.join([str(x) for x in delete_addrs]))
                Address.objects.filter(pk__in=delete_addrs).delete()

            if gallery_form:
                # if not instance:
                gallery_form.original_instance = obj
                gallery_form.save()

                # Сохраняем изображения
                # # gallery_form = gallery_formset(request.POST, request.FILES, instance=obj)
                # gallery_form = self.get_gallery_form(request, obj)
                # # Заново вызываем валидацию, чтобы получить заполненный `gallery_form.is_valid`
                # gallery_form.is_valid()
                # gallery_form.save()

            #obj.section.clear()
            #for section in form.cleaned_data['section']:
            #    obj.section.add(section)

            context = {
                'old_obj': instance,  # Старая версия объекта
            }
            self.notifications(request, obj, context)

            return self.response_completed(request, obj)

        else:
            # Если формы не валидны, записываем ошибки
            if not form.is_valid():
                logger.info('Base form is invalid in fields: %s' % ', '.join(['`%s`' % x for x in form.errors.keys()]))

            if not address_form.is_valid():
                logger.info('Address formset is invalid.')
                address_non_form_errors = address_form.non_form_errors()
                if address_non_form_errors:
                    logger.info('Address formset non-form errors in fields: %s' %
                                ', '.join(['`%s`' % x for x in address_non_form_errors.keys()]))

                for i in range(0, address_form.total_form_count()):
                    form_ = address_form.forms[i]
                    if not form_.errors:
                        continue
                    logger.info('Address form %d is invalid in fields: %s' %
                                (i, ', '.join(['`%s`' % x for x in form_.errors.keys()])))

            if gallery_form and not gallery_form.is_valid():
                logger.info('Gallery formset is invalid.')
                gallery_non_form_errors = gallery_form.non_form_errors()
                if gallery_non_form_errors:
                    logger.info('Gallery formset non-form errors in fields: %s'
                                % ', '.join(['`%s`' % x for x in gallery_non_form_errors.keys()]))

                for i in range(0, gallery_form.total_form_count()):
                    form_ = gallery_form.forms[i]
                    if not form_.errors:
                        continue
                    logger.info('Gallery form %d is invalid in fields: %s'
                                % (i, ', '.join(['`%s`' % x for x in form_.errors.keys()])))

        context = {
            'object': instance,
            'form': form,
            'address_form': address_form,
            'gallery_form': gallery_form,
        }
        context.update(self.extra_context(request, instance))

        return render(request, self.get_template(request, instance, context, create=False), context)

    def extra_context(self, request, obj=None):
        """Дополнительные данные для передачи в шаблон

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
        """

        return {}

    def get_form(self, request, obj=None):
        """Получение формы для использования в представлениях"""

        return self.form

    def get_gallery_form(self, request, obj=None):
        """Получение формы галереи для использования в представлениях"""

        return gallery_formset(request.POST, request.FILES, instance=obj)

    def get_address_form(self, request, obj=None):
        """Получение формы адреса для использования в представлениях"""

        return self.address_form

    def get_form_initial_data(self, request, obj=None, extra_context=None):
        """Начальные данные для формы"""

        return {}

    def save_form(self, request, form):
        """Сохранение формы"""

        return form.save(commit=True)

    def get_model(self, request):
        return self.model

    def save_model(self, request, obj, form):
        """Сохранение объекта

        Внимание: этот метод должен обязательно сохранять объект!"""

        obj.save()

    def response_completed(self, request, obj):
        """Объект класса HttpResponse, возвращаемый в случае корректного создания объекта"""

        return redirect(obj)

    def notifications(self, request, obj, extra_context=None):
        """Отправка уведомлений о завершенной операции пользователю

        Например, можно использовать django.contrib.messages и уведомления письмами"""

        messages.success(request, u'Изменения успешно сохранены')

    def get_template(self, request, obj, template_context, create):
        """Выбор шаблона для рендеринга

        Может возвращать список шаблонов, из которых будет выбран первый существующий

        Параметры::
            request: объект класса `django.http.HttpRequest'
            obj: объект класса ``self.model``
            template_context: словарь данных, который будет передан в шаблон
            create: если объект создается. будет равен True, иначе объект уже был создан раньше, и сейчас редактируется
        """

        if not self.template:
            raise ImproperlyConfigured(u'Не указан шаблон для вывода данных')

        return self.template
