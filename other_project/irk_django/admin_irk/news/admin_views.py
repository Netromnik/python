# -*- coding: utf-8 -*-
# Представления для админки новостей

import datetime
import logging
import time

from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import View

from irk.home import settings as app_settings
from irk.home.controllers import MaterialController as HomeMaterialController
from irk.news.controllers import ArticleIndexController
from irk.news.models import (BaseMaterial, BaseNewsletter, DailyNewsletter,
                             WeeklyNewsletter)
from irk.news.tasks import social_post_task
from irk.options.models import Site
from irk.utils.helpers import get_object_or_none
from irk.utils.http import ajax_request
from irk.utils.views.mixins import AjaxMixin, PaginateMixin

logger = logging.getLogger(__name__)
ailogger = logging.getLogger('article_index')


@permission_required('news.change_news', login_url='admin:login')
def material_home_positions(request):
    """Расположение материалов на Главной"""

    mc = HomeMaterialController(show_hidden=True)
    main_materials = mc.get_materials()

    context = {
        'positions': range(1, app_settings.HOME_POSITIONS_COUNT + 1),
        'main_materials': main_materials,
        'title': u'Расположение материалов на Главной',
    }

    return render(request, 'admin/news/material/positions.html', context)


class BaseOtherMaterials(AjaxMixin, PaginateMixin, View):
    """Список материалов для колонки поиска"""

    # поисковый запрос
    query = u''
    # исключаемые id материалов. Это обычно те, что уже находятся в основной колонке
    excludes_ids = []
    template = 'admin/news/material/list.html'

    page_limit_default = app_settings.HOME_POSITIONS_COUNT

    def post(self, *args, **kwargs):
        """Основной обработчик запросов."""

        self._parse_params()

        qs = self._get_queryset()
        qs = self._exclude(qs)
        qs = self._search(qs)

        from irk.utils.debug import print_sql
        result_list, page_info = self._paginate(qs)
        context = {'object_list': self._concretize(result_list)}

        result = dict(
            ok=True,
            html=render_to_string(self.template, context),
            **page_info
        )

        return result

    def _parse_params(self):
        """
        Разобрать параметры переданные в формате json.

        Ожидаемый формат данных:
            {
                "query": "",
                "exclude": [],
                "start": 0,
                "limit": 20,
            }
        """

        self.excludes_ids = self.request.json.get('exclude', self.excludes_ids)
        self.query = self.request.json.get('query', self.query).strip()
        start_index = self.request.json.get('start', self.start_index)
        self.start_index = max(start_index, 0)
        page_limit = self.request.json.get('limit', self.page_limit_default)
        self.page_limit = min(page_limit, self.page_limit_max)

    def _get_queryset(self):
        """Получить предварительный набор материалов."""

        raise NotImplementedError

    def _exclude(self, queryset):
        """Исключить материалы переданные в параметре exclude"""

        if self.excludes_ids:
            queryset = queryset.exclude(pk__in=self.excludes_ids)

        return queryset

    def _search(self, queryset):
        """Поиск по заголовку материала"""

        if self.query:
            queryset = queryset.filter(title__icontains=self.query)

        return queryset

    def _concretize(self, material_list):
        """
        Привести материалы к конкретному виду (из базового)

        :param list material_list: список материалов
        """

        result_list = [m.content_object for m in material_list if not m.is_specific()]

        return result_list


class HomeOtherMaterials(BaseOtherMaterials):
    """Список материалов не попавших на главную"""

    def _get_queryset(self):
        site_home = Site.objects.get(slugs='home')

        # Ограничиваемся материалами вышедшими с 2015 года.
        queryset = BaseMaterial.longread_objects \
            .for_site(site_home) \
            .filter(stamp__gte=datetime.date(2015, 1, 1)) \
            .order_by('-home_position', '-pk')

        return queryset


class ArticleIndexOther(BaseOtherMaterials):
    """Материалы справа в админе индекса статей"""

    template = 'admin/news/article_index/list.html'

    def _get_queryset(self):
        controller = ArticleIndexController()
        return controller.get_other_materials()


@permission_required('news.change_news', login_url='admin:login')
def article_index(request):
    """Расположение материалов на индексе статей"""

    controller = ArticleIndexController()
    main_materials = controller.get_materials()
    supermaterial = controller.get_supermaterial()
    base_position = controller.get_base_position()

    context = {
        'positions': range(1, app_settings.HOME_POSITIONS_COUNT + 1),
        'main_materials': main_materials,
        'supermaterial': supermaterial,
        'base_position': base_position,
        'title': u'Индекс статей',
    }

    return render(request, 'admin/news/article_index/positions.html', context)


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def article_index_save(request):
    """
    Сохранение порядка материалов на индексе статей

    Ожидаемый формат данных:
    {
        'supermaterial: {'id': 5},
        'materials': [
            {'id': 12345, 'stick_position': None},
            {'id': 6789, 'stick_position': 2},
            ...
        ]
    }
    """

    controller = ArticleIndexController()

    supermaterial_id = request.json.get('supermaterial', {}).get('id')
    if supermaterial_id:
        try:
            controller.set_supermaterial(supermaterial_id)
        except IntegrityError:
            logger.exception('Material id=%s does not exist', supermaterial_id)
    else:
        controller.reset_supermaterial()

    materials = request.json['materials']
    base_position = request.json['base_position']
    controller.admin_sort(materials, base_position)

    return {'ok': True, 'msg': u'Новое расположение материалов сохранено'}


class NewsletterOtherMaterials(BaseOtherMaterials):
    """Список материалов не попавших в рассылку"""

    template = 'admin/news/newsletter/list.html'

    def _get_queryset(self):
        # Отбираем материалы за последние 2 недели
        start_stamp = datetime.date.today() - datetime.timedelta(days=14)

        queryset = BaseMaterial.material_objects \
            .filter(stamp__gte=start_stamp, is_hidden=False) \
            .order_by('-stamp', '-pk')

        return queryset


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def material_home_positions_save(request):
    """
    Сохранение нового расположения материалов

    Ожидаемый формат данных:
    {
        'materials': [
            {'id': 12345, 'stick_position': None},
            {'id': 6789, 'stick_position': 4},
            ...
        ]
    }
    """

    materials = request.json.get('materials', [])

    timestamp = int(time.time() * 1000000)

    try:
        for index, data in enumerate(materials):
            material = BaseMaterial.material_objects.get(pk=data.get('id')).content_object
            material.home_position = timestamp - index
            material.set_stick_position(data.get('stick_position'))
            material.save()

        return {'ok': True, 'msg': u'Новое расположение материалов сохранено'}
    except ValueError as e:
        return {'ok': False, 'msg': u'Неверный идентификатор {}'.format(e)}
    except BaseMaterial.DoesNotExist:
        logger.exception('Invalid material id')
        return {'ok': False, 'msg': u'Неверный идентификатор'}
    except Exception as e:
        logger.exception('Unknown error')
        return {'ok': False, 'msg': u'Ошибка', 'error': str(e)}


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def material_set_stick_position(request):
    """
    Закрепление/открепление материала на определенной позиции

    Ожидаемый формат данных:
    для закрепления:
        {'id': 12345, 'stick_position': 6}
    для открепления:
        {'id': 12345, 'stick_position': None}
    """

    material_id = request.json.get('id')

    try:
        material = BaseMaterial.material_objects.get(pk=material_id).content_object
        material.set_stick_position(request.json.get('stick_position'), save=True)
    except BaseMaterial.DoesNotExist:
        logger.exception('Invalid material id')
        return {'ok': False, 'msg': u'Неверный идентификатор'}
    except Exception as e:
        logger.exception('Unknown error')
        return {'ok': False, 'msg': u'Ошибка', 'error': str(e)}

    if material.is_sticked():
        message = u'Закреплен менее минуты назад'
    else:
        message = u''

    return {'ok': True, 'msg': message}


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def article_index_lock(request):
    """
    Закрепление/открепление материала на определенной позиции

    Ожидаемый формат данных:
    для закрепления:
        {'id': 12345, 'stick_position': 6}
    для открепления:
        {'id': 12345, 'stick_position': None}
    """
    material_id = request.json.get('id')
    stick_position = request.json.get('stick_position')
    if stick_position is not None:
        stick_position -= 1  # fix frontend 1-based index

    try:
        controller = ArticleIndexController()
        sticked = controller.stick(material_id, stick_position)
    except BaseMaterial.DoesNotExist:
        logger.exception('Invalid material id')
        return {'ok': False, 'msg': u'Неверный идентификатор'}
    except Exception as e:
        logger.exception('Unknown error')
        return {'ok': False, 'msg': u'Ошибка', 'error': str(e)}

    if sticked:
        message = u'Закреплен менее минуты назад'
    else:
        message = u''

    return {'ok': True, 'msg': message}


@permission_required('news.change_news', login_url='admin:login')
def newsletter_materials(request, period):
    """Формирование списка рассылки материалов"""

    newsletter_map = {
        'daily': DailyNewsletter,
        'weekly': WeeklyNewsletter,
    }

    newsletter_class = newsletter_map.get(period)
    if not newsletter_class:
        raise Http404

    newsletter = newsletter_class.get_current()
    materials = newsletter.materials.select_subclasses()

    context = {
        'newsletter': newsletter,
        'title': unicode(newsletter),
        'main_materials': materials,
    }

    return render(request, 'admin/news/newsletter/index.html', context)


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def newsletter_save(request):
    """
    Сохранение рассылки

    Ожидаемый формат данных:
    {
        'newsletter_id': 123,
        'materials': [
            {'id': 12345},
            {'id': 6789},
            ...
        ]
    }
    """

    newsletter = get_object_or_none(BaseNewsletter, pk=request.json.get('newsletter_id'))
    if not newsletter:
        return {'ok': False, 'msg': u'Неверный идентификатор рассылки'}

    try:
        material_ids = [m['id'] for m in request.json.get('materials', []) if 'id' in m]
        materials = BaseMaterial.material_objects.in_bulk(material_ids)
        materials = sorted(materials.values(), key=lambda x: material_ids.index(x.id))

        newsletter.set(materials)

        return {'ok': True, 'msg': u'Рассылка сохранена'}
    except Exception as e:
        logger.exception('Unknown error')
        return {'ok': False, 'msg': u'Ошибка', 'error': str(e)}


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def social_post(request, alias, material_id):
    """Размещение материала в социальной сети

    :param request: запрос
    :param alias: название социальной сети. (vk, facebook, twitter)
    :param material_id: идентификатор материала
    """

    if not material_id:
        return {'ok': False, 'msg': u'Не указан id материала'}

    if alias not in ('vk', 'facebook', 'twitter'):
        return {'ok': False, 'msg': u'Размещение материала в {} невозможно'.format(alias)}

    task = social_post_task.delay(alias, material_id)

    return {
        'ok': True, 'msg': u'Задание на размещение материала {} в {} создано'.format(material_id, alias),
        'task_id': task.id
    }


@permission_required('news.change_news', raise_exception=True)
@ajax_request
def social_post_status(request):
    """Проверка состояния размещения материала в социальной сети"""

    task_id = request.json.get('task_id')
    if not task_id:
        return {'ok': False, 'msg': u'Задача {} не найдена'.format(task_id)}

    task = social_post_task.AsyncResult(task_id)

    if task.successful():
        return {'ok': True, 'status': 'success'}
    elif task.failed():
        return {'ok': True, 'status': 'error', 'msg': u'Произошла неизвестная ошибка. Обратитесь в тех отдел.'}
    else:
        return {'ok': True, 'status': 'pending'}


home_other_materials = HomeOtherMaterials.as_view()
article_index_other = ArticleIndexOther.as_view()
newsletter_other_materials = NewsletterOtherMaterials.as_view()
