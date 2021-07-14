# -*- coding: UTF-8 -*-

import types
import math as mathem
import random

from django.template import Library, Node, TemplateSyntaxError, Variable


def gt(value, arg):
    """Returns a boolean of whether the value is greater than the argument"""

    if type(value) is int:
        return value > int(arg)
    else:
        return value > arg


def lt(value, arg):
    """Returns a boolean of whether the value is less than the argument"""

    return int(value) < int(arg)


def gte(value, arg):
    """Returns a boolean of whether the value is greater than or equal to the argument"""

    return value >= int(arg)


def lte(value, arg):
    """Returns a boolean of whether the value is less than or equal tothe argument"""

    if type(value) is int:
        return value <= int(arg)
    else:
        return value <= arg


def percent(value, arg):
    """Процент от числа"""

    try:
        d = "%.1f" % ((float(value) / float(arg)) * 100)
        return d.replace('.', ',')
    except (ValueError, ZeroDivisionError):
        return ''


register = Library()
register.filter('gt', gt)
register.filter('lt', lt)
register.filter('gte', gte)
register.filter('lte', lte)
register.filter('percent', percent)


@register.filter
def remainder(value, arg):
    """Чем нужно дополнить value чтобы получившееся число делилось на arg"""

    if isinstance(value, types.IntType) and isinstance(value, types.IntType):
        return int(arg) - int(value) % int(arg)
    else:
        return float(arg) - (float(value) % float(arg))


class RangeNode(Node):
    def __init__(self, num, context_name):
        self.num, self.context_name = num, context_name

    def render(self, context):
        if isinstance(self.num, types.IntType):
            context[self.context_name] = range(0, int(self.num))
        else:
            try:
                context[self.context_name] = range(0, int(Variable(self.num).resolve(context)))
            except ValueError:
                context[self.context_name] = range(0, int(float(Variable(self.num).resolve(context))))

        return ''


@register.tag
def num_range(parser, token):
    """
    Takes a number and iterates and returns a range (list) that can be
    iterated through in templates

    Syntax:
    {% num_range 5 as some_range %}

    {% for i in some_range %}
      {{ i }}: Something I want to repeat\n
    {% endfor %}

    Produces:
    0: Something I want to repeat
    1: Something I want to repeat
    2: Something I want to repeat
    3: Something I want to repeat
    4: Something I want to repeat
    """

    try:
        fnctn, num, trash, context_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%s takes the syntax %s number_to_iterate\
            as context_variable" % (fnctn, fnctn)
    if not trash == 'as':
        raise TemplateSyntaxError, "%s takes the syntax %s number_to_iterate\
            as context_variable" % (fnctn, fnctn)
    return RangeNode(num, context_name)


@register.filter(name='division')
def division(first, val):
    """Деление"""

    result = float(float(first) / float(val))

    return result


@register.filter(name='round')
def do_round(value):
    """Округление"""

    try:
        return round(value)
    except (TypeError, ValueError):
        return None


@register.filter(name='ceil')
def do_ceil(value, as_int=False):
    """Округляет дробь в большую сторону"""

    try:
        result = mathem.floor(round(value) * 10.0) / 10.0
        if as_int:
            result = int(result)
        return result
    except (TypeError, ValueError):
        return 0


@register.simple_tag
def randint(a, b=None):
    """Рандомное число от a до b включительно"""
    if b is None:
        a, b = 0, a
    return random.randint(a, b)


@register.simple_tag
def randchoice(*variants):
    """
    Рандомный выбор одного из аргументов
    {% randchoice 3 5 7 as random %}
    """
    return random.choice(variants)
