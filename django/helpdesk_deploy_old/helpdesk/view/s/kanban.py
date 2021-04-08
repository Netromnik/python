from django.core.exceptions import ObjectDoesNotExist, ValidationError

from base.models import Task, Queue
from mixin.generic_viev.page import BreadcrumbItem, Page


class KanbalDefault(Page):
    title = "Таблица"
    template_name = "locations/dosk.html"
    context_object_name = "obj"
    manager = Queue.support_manager_kanban
    def get(self, request, *args, **kwargs):
        self.q_list = self.manager.get_test_root(kwargs["slug_query_pk"],kwargs["slug_stream_pk"])
        # Valid active event
        if request.GET.get("event") != None and request.GET.get("id") != None:
            event = self.request.GET.get("event")
            id = self.request.GET.get("id")
            try:
                Task.manager_task_state.get_task(id, self.q_list[1], self.request.user)
            except ObjectDoesNotExist:
                pass
            except ValidationError:
                pass
        
        return super(KanbalDefault, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        queue = self.q_list[0]
        stream = self.q_list[1]
        kwargs = super().get_context_data(**kwargs)
        kwargs["q_list"] = self.manager.get_list(self.request.user,queue)
        kwargs["dropdown_menu_view"] = self.request.user.support_q.get_view_list(queue,stream)
        kwargs["stream_list"] = self.manager.get_list_stream(q_id=queue,view_name="view:router:router_kanban")
        kwargs["table"] = self.manager.get_tables(queue,stream,self.request.user)
        return kwargs

    def get_breadcrumb(self):
        obj1 = BreadcrumbItem(name="Дашборд", is_active=False, url="/")
        obj2 = BreadcrumbItem(name=self.q_list[0]["name"], is_active=True, url="#")
        obj3 = BreadcrumbItem(name=self.q_list[1]["name"], is_active=True, url="#")
        obj4 = BreadcrumbItem(name="Таблица", is_active=True, url="#")
        return  [ obj1, obj2,obj3,obj4 ]