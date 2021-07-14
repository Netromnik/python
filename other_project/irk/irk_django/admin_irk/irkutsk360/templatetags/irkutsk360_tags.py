# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from irk.irkutsk360.models import Fact, Congratulation

register = template.Library()


@register.inclusion_tag('irkutsk360/tags/facts.html')
def fact():
    return {'fact': Fact.objects.all().first()}


@register.inclusion_tag('irkutsk360/tags/congratulations.html')
def congratulation():
    congratulation = Congratulation.objects.filter(is_visible=True).order_by('?').first()
    return {'congratulation': congratulation}
