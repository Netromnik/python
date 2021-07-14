# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
import redis
from irk.utils.http import JsonResponse
from django.conf import settings


def index(request):
    """Гоночки"""

    r = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])
    top = r.zrange(name='racing-game-top', start=0, end=9, withscores=True)
    top = [(player[0], player[1]) for player in top]
    if request.is_ajax():
        try:
            player = request.POST['player']

            self_record = r.zscore('racing-game-top', player)
            if self_record:
                top.append((player, self_record))

            prev = r.zscore('racing-game-checkpoint', player)
            if not prev:
                prev = 0
            r.zadd('racing-game-checkpoint', prev+1, player)
        except (MultiValueDictKeyError, ):
            pass
        return JsonResponse(top)
    return render(request, 'racinggame/index.html', {'top': top})


def save_record(request):
    """Проверить на читы и сохранить рекорд"""

    if request.POST and request.is_ajax():
        try:
            player = request.POST['player'] if request.user.is_anonymous else request.user.username
            fast_lap_time = float(request.POST['fast_lap_time'])

            r = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])
            self_record = r.zscore('racing-game-top', player)
            checkpoints = r.zscore('racing-game-checkpoint', player)
            record = True
            if self_record:
                record = fast_lap_time < self_record
            if checkpoints > 9 and record:
                r.zadd('racing-game-top', fast_lap_time, player)
                r.zadd('racing-game-checkpoint', 0, player)
                return JsonResponse({'result': 'ok'})
            else:
                return JsonResponse({'result': 'CHEATER!'})
        except (MultiValueDictKeyError, ValueError):
            pass
    return redirect('racinggame:index')


@user_passes_test(lambda u: u.is_superuser)
def delete_from_top(request, username):
    """Грохнуть читера из топа по юзернейму"""

    r = redis.StrictRedis(host=settings.REDIS['default']['HOST'], db=settings.REDIS['default']['DB'])
    r.zrem('racing-game-top', username)
    return redirect('racinggame:index')
