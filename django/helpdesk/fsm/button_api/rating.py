from fsm.models import Task
from django.views.decorators.http import require_http_methods
from django.shortcuts import HttpResponse,Http404


## Открыта -> Ваполняется
@require_http_methods(["GET",])
def rating(request,task_pk:int,raiting:int)->HttpResponse:
    task = Task.object.get(pk=task_pk)
    if task.state != "Закрыта":
        raise Http404
    user =request.user
    if task.responsible == user:
        raise Http404
    if raiting in range(5) and task.raiting == -1:
        task.raiting = raiting
        task.save()
    else:
        raise Http404
    return HttpResponse("200")

