# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.utils.decorators import method_decorator

from irk.game.helpers import Game


class IndexView(View):
    def get(self, request, *args, **kwargs):

        game = Game(request.user)
        context = {'g': game}

        return render(request, 'game/index.html', context)


class FoundView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FoundView, self).dispatch(request, *args, **kwargs)

    def get(self, request, treasure_id, hash_, *args, **kwargs):
        if settings.DEBUG:
            return self.post(request, treasure_id, hash_, *args, **kwargs)
        else:
            return HttpResponseNotAllowed('Use POST')

    def post(self, request, treasure_id, hash_, *args, **kwargs):
        if request.user.is_authenticated:
            game = Game(request.user)

            treasure = game.get_treasure_obj(treasure_id)
            if treasure:
                if game.check_treasure_hash(treasure, hash_):
                    game.found_treasure(treasure)
                    return HttpResponse('success')

        return HttpResponseNotFound('fail')


class PurchaseView(View):
    def get(self, request, prize_id, *args, **kwargs):
        if request.user.is_authenticated:
            game = Game(request.user)
            game.take_prize(prize_id)

        return redirect('game:index')
