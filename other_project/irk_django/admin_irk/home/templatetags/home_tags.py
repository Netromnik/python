# -*- coding: utf-8 -*-

from django import template

from irk.home.controllers import ProjectController

register = template.Library()


@register.inclusion_tag('home/tags/special_projects.html', takes_context=True)
def home_special_projects(context):
    """Блок Спецпроектов на главной"""

    ctrl = ProjectController()

    return {
        'items': ctrl.get_items(),
        'request': context.get('request'),
    }
