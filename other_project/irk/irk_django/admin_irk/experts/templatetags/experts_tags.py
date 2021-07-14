# -*- coding: utf-8 -*-

import datetime
import types
import random

from django import template
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.safestring import SafeUnicode

from irk.experts.models import Expert, Question

from irk.news.models import Category
from irk.utils.templatetags import parse_arguments
from irk.utils.templatetags.search_utils import base_search_form
from irk.utils.cache import TagCache


register = template.Library()


class ExpertSmallBlockNode(template.Node):
    def __init__(self, obj, show_image=False, show_date=True):
        self._obj = obj
        self._show_image = show_image
        self._show_date = show_date

    def render(self, context):
        obj = self._obj.resolve(context)

        if not isinstance(self._show_image, types.BooleanType):
            show_image = self._show_image.resolve(context)
        else:
            show_image = self._show_image

        if not isinstance(self._show_date, types.BooleanType):
            show_date = self._show_date.resolve(context)
        else:
            show_date = self._show_date

        now = datetime.datetime.now()

        template_context = {
            'expert': obj,
            'show_image': bool(show_image),
            'show_date': bool(show_date),
            'now': now,
            'day_offset': now + datetime.timedelta(days=3),
        }

        return render_to_string('experts/tags/small_block.html', template_context)


@register.tag
def expert_small_block(parser, token):
    """Маленький блок пресс-конференции

    Позиционные параметры::
        1. объект модели `experts.models.Expert'

    Ключевые параметры::
        show_image - показывать изображение эксперта
        show_date - показывать дату конференции
    """

    args, kwargs = parse_arguments(parser, token.split_contents()[1:])

    return ExpertSmallBlockNode(*args, **kwargs)


@register.inclusion_tag('experts/tags/main_block.html')
def expert_big_block(obj):
    """Большой блок пресс-конференции

    Параметры::
        obj - объект модели `experts.model.Expert'
    """

    now = datetime.datetime.now()

    return {
        'expert': obj,
        'now': now,
        'day_offset': now + datetime.timedelta(days=3),
    }


@register.inclusion_tag('experts/tags/announce.html')
def expert_announce():
    """Анонс пресс-конференции"""

    try:
        expert = Expert.objects.filter(
            is_announce=True, stamp__gt=datetime.date.today()).order_by('stamp')[0]
    except IndexError:
        expert = None

    return {
        'expert': expert,
    }


@register.simple_tag
def questions_count(conf, new_layout=False):
    """Блок с количеством вопросов к эксперту"""

    layout = 'experts/snippets/questions_count.html'
    if bool(new_layout):
        layout = 'experts/tags/questions_count.html'

    if not isinstance(conf, Expert):
        return ''

    if conf.is_consultation:
        questions = Question.objects.filter(expert=conf).exclude(answer='').count()
    else:
        questions = conf.questions_count

    context = {
        'object': conf,
        'questions': questions
    }

    return render_to_string(layout, context)


@register.inclusion_tag('experts/tags/popular.html')
def experts_popular(amount=5):
    """Популярные пресс-конференции"""

    return {
        'experts': Expert.objects.all().order_by('-questions_count')[:amount],
    }


class SiteRelatedExperts(template.Node):
    def __init__(self, amount, variable):
        self.amount = amount
        self.variable = variable

    def render(self, context):
        request = context['request']

        context[self.variable] = Expert.objects.filter(
            sites=request.csite).order_by('-stamp').select_related()[:self.amount]

        return ''


@register.tag
def get_site_experts(parser, token):
    """Список конференций, привязанных к разделу

    Параметры::
        amount - количество записей, int
        variable - имя результирующей переменной в контексте шаблона

    Пример использования::
        {% get_site_experts 5 as related_experts %}
    """

    try:
        tag_name, amount, as_, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires three arguments" % token.contents.split()[0])
    return SiteRelatedExperts(amount, variable)


@register.inclusion_tag('experts/tags/status.html')
def expert_status(expert):
    """Разноцветная плашка со статусом конференции"""

    return {
        'expert': expert,
        'today': datetime.date.today(),
    }


class ExpertBlockNode(template.Node):
    def __init__(self, image_size, limit=1, category=None):
        self.image_size = image_size or '140x1000'  # Размер изображения строкой передается в {% thumbnail %}
        self.limit = limit
        self.category = category

    def render(self, context):
        try:
            request = context['request']
        except KeyError:
            raise ImproperlyConfigured(u'Объект `request` недоступен в контексте шаблона')

        limit = self.limit
        if not isinstance(limit, (int, long)):
            try:
                limit = limit.resolve(context)
            except template.VariableDoesNotExist:
                limit = 1

        category = self.category

        if category:
            try:
                category = category.resolve(context)
            except template.VariableDoesNotExist:
                category = None
            # Если переменная category объявлена но имеет пустое значение то не выводить блок
            if not category or not isinstance(category, Category):
                return ''

        today = datetime.date.today()

        experts = Expert.objects.filter(sites=request.csite, stamp__lte=today, stamp_end__gte=today)
        if category:
            experts = experts.filter(category=category)
        objects = list(experts[:limit])
        random.shuffle(objects)

        cache_key = 'experts.sidebar.%s.%s.%s.%s' % (request.csite.id, today.isoformat(), limit,
                                                     ','.join(str(x.pk) for x in objects))
        with TagCache(cache_key, 86400, tags=('experts',)) as cache:
            value = cache.value
            if value is cache.EMPTY:
                # Нам нужно обернуть строку с размерами в SafeUnicode, чтобы шаблонный тег {% thumbnail %} ее воспринял
                template_context = {
                    'objects': objects,
                    'image_size': SafeUnicode(self.image_size.resolve(context).strip('\'').strip('"')),
                }

                value = render_to_string('experts/tags/sidebar-block.html', template_context)

                cache.value = value

            return value


@register.tag
def experts_sidebar_block(parser, token):
    """Вывод блока экспертов в сайдбаре

    Примеры использования::
        {% experts_sidebar_block %}
        {% experts_sidebar_block 150x600 %}
        {% experts_sidebar_block limit=2 %}
        {% experts_sidebar_block category=category %}
    """

    args, kwargs = parse_arguments(parser, token.split_contents()[1:])

    try:
        image_size = args[0]
    except IndexError:
        image_size = None

    return ExpertBlockNode(image_size, **kwargs)
