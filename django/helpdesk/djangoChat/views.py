from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from djangoChat.models import Message
from fsm.models import Task

@csrf_exempt
def chat_api(request):
    # get request
    r = Message.objects.filter(is_new=True).order_by('time')
    res = []
    for msgs in list(r):

        res.append(
            {
			 'username': msgs.user.get_full_name(),
             'actor':msgs.type,
             'content': msgs.message,
             'date': msgs.time.strftime('%m/%d/%Y, %H:%M:%S').lstrip('0')
             }
        )
        msgs.is_new = False
        msgs.save()

    data = json.dumps(res)
    return HttpResponse(data, content_type="application/json")
@csrf_exempt
def chat_api_new(request):
    if request.method == 'POST':
        d = json.loads(request.body)
        msg = d.get('msg')
        if msg == '':
            return HttpResponse("300", content_type="application/json")
        task_pk = request.headers._store['referer'][1].split("/")[-2]
        task = Task.object.get(pk = task_pk)
        user = request.user
        if task.is_owner(user):
            type_msg = "owner"
        else:
            type_msg = "resp"
        m = Message(user = user,message=msg,type=type_msg,is_new=True,task =task)
        m.save()
        return HttpResponse("200", content_type="application/json")
    return HttpResponse("300", content_type="application/json")