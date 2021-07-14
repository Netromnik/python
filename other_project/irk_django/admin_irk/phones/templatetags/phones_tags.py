# -*- coding: UTF-8 -*-

import types
import datetime

from django import template

from irk.phones.models import Sections, MetaSection

from irk.utils.settings import WEEKDAYS, WEEKDAY_SAT, WEEKDAY_SUN

register = template.Library()


class SiteRelatedRubrics(template.Node):
    def __init__(self, amount, variable):
        self.amount = amount
        self.variable = variable

    def render(self, context):

        request = context['request']
        try:
            context[self.variable] = Sections.objects.filter(sites=request.csite).order_by('position').select_related()[
                                     :self.amount]
        except IndexError:
            context[self.variable] = None

        return ''


@register.tag
def get_phones_rubrics(parser, token):
    """
    {% get_phones_rubrics 5 as phones_rubrics %}
    """

    try:
        tag_name, amount, as_, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    return SiteRelatedRubrics(amount, variable)


class MetaSectionRubrics(template.Node):
    def __init__(self, section, variable):
        self.section = section
        self.variable = variable

    def render(self, context):
        try:
            if isinstance(self.section, types.IntType):
                section = MetaSection.objects.get(pk=int(self.section))
            else:
                section = MetaSection.objects.get(alias=self.section)
        except MetaSection.DoesNotExist:
            raise template.VariableDoesNotExist(u'Рубрика с id `%s` не существует' % self.section)
        context[self.variable] = list(section.sections_set.all().order_by('position'))

        return ''


@register.tag
def get_phones_rubrics_from_section(parser, token):
    try:
        _, section, _, variable = token.split_contents()

        try:
            section = int(section)
        except TypeError:
            pass

    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.contents.split()[0]
    return MetaSectionRubrics(section, variable)


@register.inclusion_tag('phones/tags/worktime.html')
def worktime(address):
    """ Время работы """

    if not address:
        return {}

    if address.twenty_four_hour:
        return {
            'address': address
        }

    now = datetime.datetime.now()

    worktimes = {}
    for worktime in address.address_worktimes.all():
        worktimes[worktime.weekday] = worktime

    weekdays = []
    for weekday in sorted(WEEKDAYS.keys()):
        try:
            worktime = worktimes[weekday]
        except KeyError:
            worktime = None

        current_weekday = weekday == now.weekday()

        weekdays.append({'weekday': weekday,
                         'worktime': worktime,
                         'current_weekday': current_weekday})

    return {
        'weekdays': weekdays,
        'address': address,
        'weekday_sat': WEEKDAY_SAT,
        'weekday_sun': WEEKDAY_SUN
    }
