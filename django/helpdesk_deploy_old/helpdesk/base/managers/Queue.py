from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import reverse, Http404

from base.models_i.stream import Stream
from base.models_i.tasks import Task


class BaseQueueSupportManager(models.Manager):
    def get_url(self,view_name,q_id,s_pk):
        return reverse(view_name, args=[q_id['id'], s_pk])

    def get_user_all(self,user):
        gr = user.groups.all()
        qu = self.filter(groups__in = gr)
        return qu

    def get_test_root(self,q,s):
        # obj = [
        #     {"name":"test","id":1}, #Q
        #     {"name":"test","id":2}, #Stream
        # ]
        try:
            q=self.get(pk = q)
            if s != 0:
                s=Stream.obj.get(pk = s)
                if s.queue != q:
                    raise Http404("Not founds")
            else:
                class fake_obj:
                    description = "Всё"
                    pk = 0
                s = fake_obj()
        except ObjectDoesNotExist:
            raise Http404("Not founds")
        obj= []
        obj.append({ "name":q.name,"id":q.pk })
        obj.append({ "name":s.description,"id":s.pk })
        return obj

    def tree_create(self,qu):
        obj_list = []
        for q in qu:
            obj = {}
            obj["name"] = q.name
            sub = self.sup_stream(q)
            obj["sub"] = [ {"name": "Все заявки", "url": reverse("view:router:router", args=[q.pk, 0])} ,]
            obj["sub"] += [{"name": i.description, "url": reverse("view:router:router", args=[q.pk, i.pk])} for i in sub]
            obj_list.append(obj)
        return obj_list

    def get_root_list(self,user):
        # obj = {
        #     "name":"ИТДС",
        #     "sub": [
        #         { "name":"locki" ,"url":"#"},
        #         { "name":"tor","url":"#"},
        #         { "name":"ingris","url":"#"},
        #     ]
        # }
        gr = user.groups.all()
        qu = self.filter(groups__in = gr)
        list_node = self.tree_create(qu)
        return list_node

    def get_list(self,user,active_id):
        # {'id': 1, 'name': 'test'}
        qu = self.get_user_all(user)
        obj = {}
        obj["title"] = active_id["name"]
        obj["dep"] = [ { "name":i.name,"url": reverse("view:router:router", args=[i.pk, 1])} for i in qu ]
        return obj

    def sup_stream(self,q):
        return Stream.obj.filter(queue=q)

    def get_list_stream(self,q_id,view_name):
        # obj = [
        #     { "name":"test stream 1","url":"#"},
        #     { "name":"test stream 2","url":"#"},
        #     { "name":"test stream 3","url":"#"},
        # ]

        sub = self.sup_stream(q_id['id'])
        obj_nole = [{"name": "Всё", "url": reverse(view_name, args=[q_id['id'], 0])}]
        obj =  obj_nole + [{"name": i.description, "url": reverse(view_name, args=[q_id['id'], i.pk])} for i in sub]
        return obj




class QueueSupportManagerTable(BaseQueueSupportManager):
    ## return quese
    ## return dosk
    ## return path
    ## return table



    def get_asignet(self,queue,stream,user):
        stream = stream["id"]
        queue = queue["id"]
        if stream  == 0:
            poll = self.none()
            for stream_obj in Stream.obj.filter(queue = queue):
                poll |= Task.obj.filter(stream=stream_obj, asignet_to=user)
        else:
            poll = Task.obj.filter(stream = stream,asignet_to = user)
        return poll

    def get_non_asignet(self,queue,stream,user):
        stream = stream["id"]
        queue = queue["id"]
        if stream  == 0:
            poll = self.none()
            for stream_obj in Stream.obj.filter(queue = queue):
                poll |= Task.obj.filter(stream=stream_obj, asignet_to=None)
        else:
            poll = Task.obj.filter(stream = stream,asignet_to=None)
        return poll

class QueueSupportManagerKanban(BaseQueueSupportManager):


    def get_groups(self):
        obj = [
                    {"name":"Статусам","url":"#"},
                    {"name":"Людям","url":"#"},
                ]
        return None

    def get_button(self,task,user):
        obj_list = []
        get  = {"name": "Взять", "url": f"?event=get&id={task.pk}", "class": "get"}
        view = {"name": "Посмотреть", "url": task.get_view_url(), "class": "view"}
        push = {"name": "Отложить", "url": "?event=push", "class": "push"}

        if  task.autors  == user or task.asignet_to == user:
            #"get"
            # obj_list.append(push)
            pass
        else:
            obj_list.append(get)
        obj_list.append(view)
        return obj_list

    def _get_list_tree_ell(self,title,task_arr,user):
        obj = {}
        obj["title"] = title
        list_obj =[]
        for task in task_arr:
            el = {
                            "name": task.title,
                            "date": task.updated_at,
                            "button":self.get_button(task,user)
                 }
            list_obj.append(el)
        obj['sticker'] = list_obj
        return obj

    def _group_status(self,task_pool,user):
        obj_list = []
        for i,name in Task.STATUS:
            sub_pool = task_pool.filter(status=i)
            obj_list.append(self._get_list_tree_ell(name,sub_pool,user))
        return obj_list

    def get_list_tree(self,queue_id,stream_id,user):

        # pool
        # poll filter
        # poll filter element
        if stream_id == 0:
            q =self.get(pk= queue_id)
            sub = self.sup_stream(q=q)
            task_pool = Task.obj.filter(stream__in =sub )
        else:
            task_pool= Task.obj.filter(stream__id = stream_id)
        obj = self._group_status(task_pool,user)
        return obj

    def get_tables(self,queue,stream,user):
        obj = {}
        obj["status"] = self.get_groups()
        obj["list"] = self.get_list_tree(queue["id"],stream["id"],user)
        return obj

##### status
##    Task