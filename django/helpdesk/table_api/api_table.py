from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SettingsTable
from django.core.exceptions import MultipleObjectsReturned ,ObjectDoesNotExist

@csrf_exempt
def user_save_table(request,table_id:str):
    ###
    ## data key = ['time', 'start', 'length', 'order', 'search', 'columns', 'searchBuilder', 'page']
    if request.method == 'POST':
        ## check data
        try:
            obj = SettingsTable.object.get(user = request.user,table_id=table_id)
            obj.json_dump = request.body.decode("utf-8")
            obj.save(update_fields="json_dump")
        except ObjectDoesNotExist:
            obj = SettingsTable(user=request.user, table_id=table_id,json_dump = request.body.decode("utf-8"))
            obj.save()
        finally:
            return HttpResponse("200", content_type="application/json")
    return HttpResponse("300", content_type="application/json")


    # if not  ( task.owner == user or task.responsible == user):
    #     raise Http404

@csrf_exempt
def user_get_table(request,table_id:str):
    ###
    ## data key = ['time', 'start', 'length', 'order', 'search', 'columns', 'searchBuilder', 'page']
    if request.method == 'GET':
        ## check data
        try:
            obj = SettingsTable.object.get(user = request.user,table_id=table_id)
            return HttpResponse(obj.json_dump,content_type="application/json")
        except MultipleObjectsReturned:
            obj_list = SettingsTable.object.filter(user=request.user, table_id=table_id)
            obj = obj_list[1]
            for i in range(1,len(obj_list)):
                obj_list[i].delete()
        except SettingsTable.DoesNotExist:
            return HttpResponse("[]",content_type="application/json")
    return HttpResponse("300", content_type="application/json")

@csrf_exempt
def user_save(request):
    if request.method == 'POST':
        d = json.loads(request.body)
        msg = d.get('msg')
        return HttpResponse("200", content_type="application/json")
    return HttpResponse("300", content_type="application/json")


    # if not  ( task.owner == user or task.responsible == user):
    #     raise Http404

@csrf_exempt
def user_save(request):
    if request.method == 'POST':
        d = json.loads(request.body)
        msg = d.get('msg')
        return HttpResponse("200", content_type="application/json")
    return HttpResponse("300", content_type="application/json")


    # if not  ( task.owner == user or task.responsible == user):
    #     raise Http404
