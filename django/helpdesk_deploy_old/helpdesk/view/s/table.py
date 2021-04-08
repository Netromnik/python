from django.core.exceptions import ObjectDoesNotExist, ValidationError

from base.models import Queue, Task
from mixin.generic_viev.page import Page, BreadcrumbItem
from mixin.table import TableAsignet, TableNonAsignet


class Table(Page):
    title = "Таблица"
    template_name = "locations/table.html"
    context_object_name = "obj"
    ## object name id
    q_list = None
    manager = Queue.support_manager_table

    def get(self, request, *args, **kwargs):
        self.q_list = self.manager.get_test_root(kwargs["slug_query_pk"], kwargs["slug_stream_pk"])
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

        return super(Table, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        queue = self.q_list[0]
        stream = self.q_list[1]
        kwargs = super().get_context_data(**kwargs)
        kwargs["q_list"] = self.manager.get_list(self.request.user,queue)
        kwargs["dropdown_menu_view"] = self.request.user.support_q.get_view_list(queue,stream)
        kwargs["stream_list"] = self.manager.get_list_stream(q_id=queue,view_name="view:router:router_table")
        data1 =  self.manager.get_asignet(queue,stream,self.request.user)
        data2 =  self.manager.get_non_asignet(queue,stream,self.request.user)
        kwargs["table_asignet"] = TableAsignet(data1,1).get_table_html()
        kwargs["table_avtor"] = TableNonAsignet(data2,2).get_table_html()
        return  kwargs

    def get_breadcrumb(self):
        obj1 = BreadcrumbItem(name="Дашборд", is_active=False, url="/")
        obj2 = BreadcrumbItem(name=self.q_list[0]["name"], is_active=True, url="#")
        obj3 = BreadcrumbItem(name=self.q_list[1]["name"], is_active=True, url="#")
        obj4 = BreadcrumbItem(name="Таблица", is_active=True, url="#")
        return  [ obj1, obj2,obj3,obj4 ]
