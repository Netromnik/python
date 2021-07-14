# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import datetime
from django import template
from django.conf import settings

from irk.game.models import Treasure, Gamer
from irk.game.helpers import Game

register = template.Library()


@register.inclusion_tag('game/tags/treasure.html', takes_context=True)
def treasure(context, secret):

    request = context.get('request')

    context['show_treasure'] = False

    if not request.user.is_authenticated or settings.BIRTHDAY_GAME_GAMERS == 'noone':
        return context

    if settings.BIRTHDAY_GAME_GAMERS == 'moderators' and not request.user.is_staff:
        return context

    game = Game(request.user)
    treasure = game.get_treasure_by_secret(secret)
    if treasure:
        found = game.is_treasure_found(treasure)
        if not found:
            context['show_treasure'] = True
            context['treasure'] = treasure
            context['treasure_hash'] = game.create_treasure_hash(treasure)
            context['hint'] = game.gamer.get_hint(treasure.pk)

    return context
