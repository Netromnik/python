from django.shortcuts import reverse
from base.models_i.file import CollectMedia
from django.shortcuts import reverse

from base.models_i.file import CollectMedia


class UserModelCustomManeger():

    def get_view_type_url(self,q,s):
        ## table
        return reverse("view:router:router_table",kwargs={"slug_query_pk":q,"slug_stream_pk":s})

    def get_view_list(self,queue,stream):
        obj = {}
        obj['title'] = "Виды отображения"
        obj["dep"] = [
            {
                "name":"Таблица",
                "url" :reverse("view:router:router_table", args=[queue['id'], stream['id']])
            },{
                "name":"Доска",
                "url" :reverse("view:router:router_kanban", args=[queue['id'], stream['id']])
            },
        ]
        return obj

    def get_collect(self,user):
        obj = CollectMedia.obj.get(name="wiki")
        return obj
