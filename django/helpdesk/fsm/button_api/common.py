from fsm.models import Task
from django.views.decorators.http import require_http_methods
from django.shortcuts import HttpResponse,Http404


## Открыта -> Ваполняется
@require_http_methods(["GET",])
def open_start(request,task_pk:int):
    task = Task.object.get(pk=task_pk)
    user =request.user
    task.progress()
    task.responsible = user
    task.save()
    return HttpResponse("200")

## Ваполняется -> Решена
@require_http_methods(["GET",])
def sucefful(request,task_pk:int):
    task = Task.object.get(pk=task_pk)
    user =request.user
    if not  ( task.owner == user or task.responsible == user):
        raise Http404
    task.resolve()
    task.the_importance = "warm"
    task.save()
    return HttpResponse("200")

## Решена --> Закрыта
@require_http_methods(["GET",])
def close(request,task_pk:int):
    task = Task.object.get(pk=task_pk)
    user =request.user
    if task.owner != user:
        raise Http404
    task.close()
    task.the_importance = 'low'
    task.save()
    return HttpResponse("200")


##  --> Переоткрыта
@require_http_methods(["GET",])
def re_open(request,task_pk:int):
    task = Task.object.get(pk=task_pk)
    user =request.user
    if not ( user.is_superuser or user.is_staff):
        raise Http404
    task.re_resolve()
    task.responsible = None
    task.raiting = -1
    task.save()
    return HttpResponse("200")
