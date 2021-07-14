# -*- coding: utf-8 -*-

from django.utils.functional import SimpleLazyObject

from django_user_agents.utils import get_user_agent


def prepare_user_agent(req):
    """Подготовить объект user_agent для request с дополнительными проверками"""

    user_agent = get_user_agent(req)
    user_agent.is_gadget = user_agent.is_mobile or user_agent.is_tablet

    return user_agent


class CustomUserAgentMiddleware(object):
    """
    Мидлварь для добавления user_agent к request с кастомными настройками.

    Сделана по подобию django_user_agents.middleware.UserAgentMiddleware,
    но также добавляет проверку на гаджет (или мобильный, или планшет)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_agent = SimpleLazyObject(lambda: prepare_user_agent(request))
        return self.get_response(request)
