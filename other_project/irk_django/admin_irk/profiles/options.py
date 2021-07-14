# -*- coding: utf-8 -*-

import types
import pickle
import logging
import datetime
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.db.models import Model
from django.db.models.query import QuerySet

from irk.profiles import models
from irk.utils.decorators import deprecated

logger = logging.getLogger(__name__)


class EmptyValue(Exception):
    pass


class OptionValidationError(Exception):
    """Ошибка валидации данных, установленных в качестве значения настройки"""


class EmptyValueError(OptionValidationError):
    """Нет данных на входе"""


class BaseOption(object):
    """Базовый класс для настроек пользователя

    Зарегистрированный пользователь
    -----------------------------------------

    Данные сохраняются в базу данных. Используется модель `profiles.models.Options`
    и методы `prepare_value_for_db`/`load_value_from_cookie`

    Значения настроек кэшируются в контейнере request.user.options.
    См. `options.middleware.OptionsMiddleware`

    Незарегистрированный пользователь
    ------------------------------------------

    Данные хранятся в cookies, используются методы `prepare_value_for_cookie`/`load_value_from_cookie`

    Формат хранения::
        1. Контейнер данных - cookie с именем `p`
        2. Данные в формате *ключ=значение* разделены символом ";"

    Свойства класса::

        multiple : True или False
            Может ли настройка принимать множественные значения

        cookie_key : строка
            Имя настройки в cookies. Предпочтительно короткое название, т.к. размер cookies ограничен.

        choices : список
            Список возможных вариантов значений. Может быть Queryset или список значений формата `(1, 'title')`,
            где `1` - уникальный идентификатор, `'title'` - название значения

        default
            Значение по умолчанию. Варианты: QuerySet, объект класса django.db.models.Model либо идентификатор из
            _`choices`.

        form: класс, отнаследованный от django.forms.Form
            Для перегрузки валидации введенных данных

        expire: дата после которой данная настройка неактуальна
    """

    multiple = False

    def __init__(self, request, response=None, user=None):
        self._user = user or request.user
        self._request = request
        self._response = response
        self._obj = None  # Запись в БД этой настройки для пользователя
        self._value = None
        self._cookies = {}  # Распарсенные опции из cookies

        name = self.__class__.__name__.lower()
        app = self.__module__.split('.user_options')[0]
        if app.startswith('irk.'):
            app = app.lstrip('irk.')
        self._name = '%s.%s' % (app, name)  # Уникальный идентификатор настройки

        try:
            self._load()
        except (EmptyValueError, OptionValidationError):
            self._value = self.default
            self.save()

    @property
    def cookie_key(self):
        raise NotImplementedError(u'Subclasses must set this property')

    @property
    def choices(self):
        raise NotImplementedError(u'Subclasses must set this property')

    @property
    def default(self):
        raise NotImplementedError(u'Subclasses must set this property')

    @property
    def name(self):
        return self._name

    @property
    @deprecated
    def display(self):
        raise NotImplementedError(u'You must not implement this deprecated method. Use __unicode__ instead it')

    def prepare_value_for_db(self, value):
        """Нормализация значения перед сохранением в базу данных"""

        return pickle.dumps(value)

    def load_value_from_db(self, value):
        """Денормализация значения после загрузки из базы данных"""

        try:
            return pickle.loads(value)
        except (ValueError, pickle.UnpicklingError):
            return self.default

    def prepare_value_for_cookie(self, value):
        """Нормализация значения перед сохранением в cookies"""

        return value

    def load_value_from_cookie(self, value):
        """Денормализация значения после загрузки из cookies"""

        self.value = value

    def load_value_from_input(self, value):
        """Обработка данных, полученных через GET/POST запрос"""

        if self.multiple:
            return [int(x) for x in value.split(',')]
        return int(value)

    def _load(self, force=False):
        """Загрузка данных"""

        value = None

        # Значение опции уже было обработано в рамках этого запроса, используем готовое отвалидированное значение
        if not force and hasattr(self._user, 'options') and self._name in self._user.options.prepared:
            self._value = self._user.options.prepared[self._name]
            return

        if self._user.is_authenticated:
            if hasattr(self._user, 'options'):
                try:
                    value = self.load_value_from_db(self._user.options.raw[self._name])
                except KeyError:
                    raise EmptyValueError()
            else:
                # Получаем данные из БД
                try:
                    self._obj = models.Options.objects.get(user=self._user, param=self._name)
                except models.Options.DoesNotExist:
                    raise EmptyValueError(u'В базе нет данных для этого пользователя')
                except models.Options.MultipleObjectsReturned:
                    models.Options.objects.filter(user=self._user, param=self._name).delete()
                    raise EmptyValueError(u'В базе было несколько значений опции. Устанавливаем значение по умолчанию')
                else:
                    value = self.load_value_from_db(self._obj.value)
        else:
            # Данные берутся из cookies
            params = self._request.COOKIES.get('p')
            if not params:
                raise EmptyValueError(u'Нет cookie с именем p')
            for item in params.split(';'):
                try:
                    key, value = item.split('=')
                    self._cookies[key] = value
                except ValueError:
                    continue

            if self.cookie_key in self._cookies:
                value = self.load_value_from_cookie(self._cookies[self.cookie_key])
            else:
                raise EmptyValueError()

        # Пользователь может подменить cookies, например
        try:
            self._value = self._validate(value)
        except OptionValidationError:
            self._value = self.default

        if hasattr(self._user, 'options'):
            self._user.options.prepared[self._name] = self._value

    def save(self):
        """Сохранение данных"""

        if self._user.is_authenticated:
            if not self._obj:
                self._obj = models.Options(user=self._user, param=self._name)
            self._obj.value = self.prepare_value_for_db(self._value)
            logger.debug('Saving user option into database: %s=%s' % (self._obj.param, self._obj.value))
            self._obj.save()

            if hasattr(self._user, 'options'):
                self._user.options.prepared[self._name] = self._value
        else:
            self._cookies[self.cookie_key] = self.prepare_value_for_cookie(self._value)
            logger.debug('Saving user option into cookie: %s=%s' % (self._name, self._cookies[self.cookie_key]))
            # Сериализуем обратно значения всех опций
            values = []
            for value in self._cookies.items():
                values.append('%s=%s' % value)

            if self._response:
                # Если доступен response (было бы хорошо, чтобы он был доступен) - expires для cookie ставится на две
                # недели вперед
                self._response.set_cookie('p', ';'.join(values),
                                          expires=datetime.datetime.now() + datetime.timedelta(days=14))

            # Добавляем это же значение в request, чтобы все последующие обращения к кукам в рамках этого процесса
            # получили новые значения
            self._request.COOKIES['p'] = ';'.join(values)

    def form(self, fields=(), data=None):
        """Генерация объекта формы для отображения опции"""

        # Атрибуты класса формы
        properties = {
            'param': forms.CharField(widget=forms.HiddenInput, initial=self._name),
            'next': forms.CharField(widget=forms.HiddenInput, initial=self._request.build_absolute_uri())
            # Адрес для редиректа
        }

        if fields:
            for field in fields:
                properties[field.name] = field
        else:

            if isinstance(self.choices, QuerySet):
                have_choices = self.choices.exists()
            else:
                have_choices = bool(self.choices)

            if have_choices:
                if self.multiple:
                    if isinstance(self.choices, QuerySet):
                        if isinstance(self.value, QuerySet):
                            value_pks = self.value.values_list('pk', flat=True)
                        elif isinstance(self.value, (types.ListType, types.TupleType)):
                            value_pks = [x.pk for x in self.value]
                        else:
                            raise ValueError(u'Неправильные данные опции')
                        properties['value'] = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                                             queryset=self.choices, initial=value_pks)
                    else:
                        properties['value'] = forms.MultipleChoiceField(choices=self.choices,
                                                                        initial=self.value or None)
                else:
                    if isinstance(self.choices, QuerySet):
                        properties['value'] = forms.ModelChoiceField(queryset=self.choices,
                                                                     initial=self.value.pk if self.value else None)
                    else:
                        properties['value'] = forms.ChoiceField(choices=self.choices, initial=self.value or None)

        form_class = type('OptionForm', (forms.Form,), properties)

        return form_class(data)

    def get_value(self):
        return self._value

    def set_value(self, value):
        try:
            self._value = self._validate(value)
        except OptionValidationError:
            logger.debug('Option "%s" validation error while setting new value' % self._name)
            self._value = self.default

    value = property(get_value, set_value)

    def _get_request(self):
        return self._request

    def _set_request(self, request):
        self._request = request

        self._cookies = {}
        try:
            self._load(force=True)
        except (EmptyValueError, OptionValidationError):
            self._value = self.default
            self.save()

        # Whoops!
        if hasattr(self._user, 'options'):
            delattr(self._user, 'options')

    request = property(_get_request, _set_request)

    def _validate(self, value):
        """Валидация данных"""

        if not value:
            raise OptionValidationError()

        if isinstance(self.choices, QuerySet):
            if isinstance(value, (QuerySet, types.ListType, types.TupleType)):
                # Для multiple настроек
                # Результирующим значением будет пересечение двух QuerySet
                return list(set(value) & set(self.choices))
            elif isinstance(value, Model):
                try:
                    if not self.choices.filter(pk=value.pk).exists():
                        raise ObjectDoesNotExist()
                except ObjectDoesNotExist:
                    raise OptionValidationError(u'Объект с pk=%s не находится в списке choices для `%s`' % (value.pk,
                                                                                                            self._name))
            else:
                # TODO: Чему может быть равен value, чтобы попадать в эту ветку?
                raise NotImplementedError(u'Не знаю, что делать со значением %s' % value)
        else:
            # choices - список значений, итерируемся по нему и ищем совпадение
            if self.multiple:
                return list(set([int(x) for x in value]) & set([x[0] for x in self.choices]))
            else:
                if not isinstance(value, types.BooleanType):
                    # boolean переменные не пытаемся конвертировать в int, они это выдерживают,
                    # а сравнивать с возможными вариантами потом не удается
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        pass

                match = False
                for item in self.choices:
                    item = item[0] if isinstance(item, (types.ListType, types.TupleType)) else item
                    if value == item:
                        match = True
                        break

                if not match:
                    raise OptionValidationError()

        return value

    def render(self, extra=None):
        """В ответ на запрос клиенту могут возвращаться данные
        Например, при изменении города в тулбаре, рендерится виджет погоды

        Метод должен возвращать сериализуемый объект

        Параметры::

            extra
                Дополнительные данные для шаблона"""

        raise NotImplementedError(u'Subclasses must implement this method')

    def __unicode__(self):
        for choice in self.choices:
            if isinstance(choice, Model) and self.value == choice.pk:
                return unicode(choice)
            elif isinstance(choice, (types.ListType, types.TupleType)) and self.value == choice[0]:
                return choice[1]
        return ''

    def __repr__(self):
        return '<%s: %s>' % (self._name, str(self._value))

    def __eq__(self, other):
        return self._name == other._name and self._value == other._value

    def __ne__(self, other):
        return not self == other


Option = BaseOption  # For old-style options


class OptionsContainer(dict):
    """Регистрация пользовательских настроек"""

    def __init__(self, *args):
        super(OptionsContainer, self).__init__(*args)
        self._is_loading = False

    def discovery(self):
        if self._is_loading:
            return

        self._is_loading = True
        for app in settings.INSTALLED_APPS:
            try:
                options_module = import_module('%s.user_options' % app)
            except ImportError:
                continue
            for attr in dir(options_module):
                attr_name = attr.lower()
                if attr == 'Option':
                    continue
                attr = getattr(options_module, attr)
                try:
                    if issubclass(attr, Option):
                        # app содержит 'irk.App', берем только имя приложения
                        app_name = app.split('.')[-1]
                        self['%s.%s' % (app_name, attr_name)] = attr
                except TypeError:  # attr не является классом
                    continue

        self._is_loading = False


options_library = OptionsContainer()
