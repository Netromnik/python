# -*- coding: utf-8 -*-

import types

from django import template
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType

from irk.ratings import settings
from irk.ratings.helpers import is_rateable, is_rated
from irk.ratings.models import RatingObject, RateableModel
from irk.utils.helpers import force_unicode
from irk.utils.metrics import newrelic_record_timing

register = template.Library()


class RatingObjectNode(template.Node):

    def __init__(self, obj, next=None, variable=None, disabled=False, new_makeup=False, new_makeup2=False,
                 new_line=False, without_text=False, template_path=None, closed=False):
        self.obj = obj
        self.next = next
        self.variable = variable
        self.disabled = disabled
        self.new_makeup = new_makeup
        self.new_makeup2 = new_makeup2
        self.closed = closed
        self.new_line = new_line
        self.without_text = without_text
        self.template_path = template_path

    @newrelic_record_timing('Custom/Ratings/TemplateTag')
    def render(self, context):
        request = context['request']
        if isinstance(self.obj, types.StringTypes):
            obj = template.Variable(self.obj).resolve(context)
        else:
            obj = self.obj

        if not obj:
            return ''

        # Рейтинг применяется только для объекта фирмы
        if hasattr(obj, "firms_ptr"):
            obj = obj.firms_ptr

        if isinstance(self.next, types.StringTypes):
            next = template.Variable(self.next).resolve(context)
        else:
            next = self.next

        if not next and not self.disabled:
            next = force_unicode(request.META.get('HTTP_REFERER', obj.get_absolute_url()))

        obj_settings = is_rateable(obj)
        if not obj_settings:
            raise template.TemplateSyntaxError(u'Переданному аргументу нельзя устанавливать рейтинги')

        content_type = ContentType.objects.get_for_model(obj)

        try:
            rating = RatingObject.objects.get(content_type=content_type, object_pk=obj.pk)
        except RatingObject.DoesNotExist:
            rating = None

        if rating and isinstance(obj, RateableModel):
            rating.external = obj.rating
            if rating.total_cnt < settings.BAYES_MINIMUM_VOTES:
                rating.external = 0

        values_range = settings.RATING_TYPES[obj_settings['type']]
        if self.template_path:
            template_name = self.template_path
        else:
            if isinstance(obj, RateableModel):
                template_name = 'ratings/widgets/%s_ext.html' % obj_settings['type']
            else:
                template_name = 'ratings/widgets/%s.html' % obj_settings['type']

        content = render_to_string(template_name, {
            'obj': obj,
            'values': values_range,
            'content_type': content_type,
            'is_rated': is_rated(obj, request) if request.user.is_authenticated else True,
            'closed': self.closed,
            'rating': rating,
            'next': next,
            'authenticated': request.user.is_authenticated,
            'disabled': self.disabled,
            'new_makeup': self.new_makeup,
            'new_makeup2': self.new_makeup2,
            'new_line': self.new_line,
            'without_text': self.without_text,
            'allow_anonymous': obj_settings.get('anonymous', False),
            'min_bayes_votes': settings.BAYES_MINIMUM_VOTES,
        }, request=request)

        if self.variable:
            context[self.variable] = {
                'html': content,
            }
            if not isinstance(obj, RateableModel):
                context[self.variable]['value'] = rating.total_sum if rating else 0
                context[self.variable]['total_cnt'] = rating.total_cnt if rating else 0
                context[self.variable]['average'] = rating.average() if rating else 0
            return ''

        return content


@register.tag
def rating(parser, token):
    """Виджет рейтинга для объекта

    Параметры:
     - объект рейтинга
     - URL для последующего редиректа
     - disabled: рейтинг в режиме read-only
     - переменная для контекста

    {% rating some_object %}
    {% rating some_object http://www.example.org [disabled,new_makeup,new_makeup2,new_line,path_to_template.html] %}
    {% rating some_object http://www.example.org [disabled,new_makeup,new_makeup2,new_line,path_to_template.html] as foo %}

    TODO: документация по всем возможным параметрам тега!
    """

    bits = token.split_contents()

    if len(bits) not in range(2, 7):
        raise template.TemplateSyntaxError('Tag `%s` receives 1 or more arguments' % bits[0])

    kwargs = {}
    for arg in ('disabled', 'new_makeup', 'new_makeup2', 'new_line', 'without_text', 'closed'):
        kwargs[arg] = False
        if arg in bits:
            bits.remove(arg)
            kwargs[arg] = True

    kwargs['template_path'] = None
    for bit in bits:
        if bit.strip('\'').strip('"').endswith('.html'):
            kwargs['template_path'] = bit.strip('\'').strip('"')
            bits.remove(bit)
            break

    variable = None
    if bits[-2] == 'as':
        variable = bits[-1]
        bits = bits[:-2]

    obj = bits[1]
    try:
        next = bits[2]
    except IndexError:
        next = None

    return RatingObjectNode(obj, next, variable=variable, **kwargs)


class RatingResultNode(template.Node):

    def __init__(self, obj, template):
        self.obj = obj
        self.template = template

    def render(self, context):
        request = context['request']

        if isinstance(self.obj, types.StringTypes):
            obj = template.Variable(self.obj).resolve(context)
        else:
            obj = self.obj

        obj_settings = is_rateable(obj)
        if not obj_settings:
            raise template.TemplateSyntaxError(u'Переданному аргументу нельзя устанавливать рейтинги')

        content_type = ContentType.objects.get_for_model(obj)

        try:
            rating = RatingObject.objects.get(content_type=content_type, object_pk=obj.pk)
        except RatingObject.DoesNotExist:
            rating = None

        values_range = settings.RATING_TYPES[obj_settings['type']]
        template_name = self.template
        if template_name is None:
            template_name = 'ratings/widgets/results/%s.html' % obj_settings['type']  # Имя шаблона
        else:
            template_name = self.template.strip('\'').strip('"')

        context_params = {
            'obj': obj,
            'values': values_range,
            'content_type': content_type,
            'is_rated': is_rated(obj, request),
            'rating': rating,
        }
        return render_to_string(template_name, context=context_params, request=request)


@register.tag
def rating_result(parser, token):
    """Виджет вывода рейтинга для объекта

    Параметры:
     - объект рейтинга

    {% rating_result some_object %}"""

    bits = token.split_contents()

    obj = bits[1]
    template_name = None

    if len(bits) == 2:
        pass
    elif len(bits) == 3:
        template_name = bits[2]
    else:
        raise template.TemplateSyntaxError('Tag `%s` receives 1 argument' % bits[0])

    return RatingResultNode(obj, template_name)
