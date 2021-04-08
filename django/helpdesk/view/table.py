from fsm.models import Queue,Task,is_sub_page
from mixin.generic_viev.page import Page ,BreadcrumbItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .table_class.common import NotActiveTask,ActiveTask
from django.contrib.auth.models import User
class MuxQueqry():
    title = None


## activ task res =user q_user
## not act q = user

class AbstructTable(Page):
    title = "Таблица"
    template_name = "locations/table.html"
    context_object_name = "obj"

    def get(self, request, *args, **kwargs):
        try:
            kwargs = self.static_kwarg(**kwargs)
            if self.kwargs['slug_sub_pk'] == 0:
                context = self.get_root_context_data(request,**kwargs)
            elif is_sub_page(self.kwargs["slug_query_pk"], self.kwargs['slug_sub_pk']) :
                context = self.get_sub_context_data(request,**kwargs)
        except ObjectDoesNotExist:
            raise Http404("Очередь не была найдена")
        return self.render_to_response(context)

    def get_sub_context_data(self,request,**kwargs):
        return self.get_context_data(**kwargs)

    def get_root_context_data(self,request,**kwargs):
        return self.get_context_data(**kwargs)

    def static_kwarg(self,**kwargs):
        kwargs["title"] = self.title
        kwargs["menu_item"] = self.menu_item
        return kwargs

    def get_breadcrumb(self,q_name:str,sub_q_name:str):
        obj1 = BreadcrumbItem(name="Дашборд", is_active=False, url="/")
        obj2 = BreadcrumbItem(name=q_name, is_active=True, url="#")
        obj3 = BreadcrumbItem(name=sub_q_name, is_active=True, url="#")
        obj4 = BreadcrumbItem(name="Таблица", is_active=True, url="#")
        return  [ obj1, obj2,obj3,obj4 ]

class Table(AbstructTable):
    def get_quriset(self,q:Queue,sub_q:Queue,user):
        activ_task_table = Task.object.filter(state__in = ['Ваполняется', 'Решена'],responsible=user,queue__in=[q,sub_q]).exclude(owner=user)
        not_activ_task_table = Task.object.filter(state__in = ['Открыта','Переоткрыта','Ошибка'],responsible=None,queue__in=[q,sub_q]).exclude(owner=user)
        return activ_task_table,not_activ_task_table

    def get_root_context_data(self,request,**kwargs):
        queue = Queue.objects.get(pk = self.kwargs["slug_query_pk"])
        activ_task_table,not_activ_task_table = self.get_quriset(queue,queue.get_children()[0],user=request.user)

        ### wor k kwarg
        kwargs["all"] = queue.url()
        kwargs["breadcrumb_list"] = self.get_breadcrumb(queue.title,"Всё")
        kwargs["stream_list"] = queue.get_children()
        kwargs['table_activ'] = ActiveTask(activ_task_table)
        kwargs['table_not_activ'] = NotActiveTask(not_activ_task_table)
        return kwargs

    def get_sub_context_data(self,request,**kwargs):
        queue = Queue.objects.get(pk = self.kwargs["slug_sub_pk"])
        activ_task_table,not_activ_task_table = self.get_quriset(queue,queue,user=request.user)

        ### wor k kwarg
        kwargs["all"] = queue.parent.url()
        kwargs["breadcrumb_list"] = self.get_breadcrumb(queue.parent.title,queue.title)
        kwargs["stream_list"] = queue.parent.get_children()
        kwargs['table_activ'] = ActiveTask(activ_task_table)
        kwargs['table_not_activ'] = NotActiveTask(not_activ_task_table)
        return kwargs

# class Table(AbstructTable):
#
#     def static_kwarg(self,queue , sub_q,**kwargs):
#         kwargs["title"] = self.title
#         kwargs["menu_item"] = self.menu_item
#         kwargs["breadcrumb_list"] = self.get_breadcrumb(queue.title , sub_q.title)
#         kwargs["all"] = queue.url()
#         kwargs["stream_list"] = queue.get_children()
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         queue , sub_q = self.get_queue(self.kwargs["slug_query_pk"],self.kwargs['slug_sub_pk'])
#         kwargs = self.static_kwarg(queue,sub_q,**kwargs)
#         admin_table, activ_table, not_activ_table = self.table_logick(queue,sub_q,kwargs['slug_sub_pk'])
#         if admin_table !=False:
#             if admin_table.count !=0:
#                 kwargs['table_admin'] = AdminTask(admin_table)
#         if activ_table.count() !=0:
#             kwargs['table_activ'] = ActiveTask(activ_table)
#         if not_activ_table.count() !=0:
#             kwargs['table_not_activ']= NotActiveTask(not_activ_table)
#         return  kwargs
#
#     def table_logick(self,queue , sub_q,slug_sub_pk):
#         if slug_sub_pk == 0:
#             """ Если выбрана подкатегория"""
#             admin_table, activ_table, not_activ_table = self.sub_kategory(queue)
#         else:
#             activ_table = Task.object.filter(queue=sub_q, responsible=self.request.user)
#             not_activ_table = Task.object.filter(queue=sub_q, responsible=None).exclude(owner=self.request.user)
#             if self.request.user.is_superuser or self.request.user.is_staff:
#                 admin_table = Task.object.filter(queue=sub_q)
#             else:
#                 admin_table=False
#         activ_table = activ_table.exclude(state='Закрыта')
#         return admin_table,activ_table,not_activ_table
#
#     def sub_kategory(self,queue):
#         activ_table = Task.object.filter(queue__in=queue.get_children(),
#                                                  responsible=self.request.user) | Task.object.filter(queue=queue,
#                                                                                                      responsible=self.request.user)
#         not_activ_table = Task.object.filter(queue__in=queue.get_children(),
#                                                   responsible=None) | Task.object.filter(queue=queue, responsible=None)
#         if self.request.user.is_superuser or self.request.user.is_staff:
#             admin_table = Task.object.filter(queue__in=queue.get_children()) | Task.object.filter(queue=queue)
#         else:
#             admin_table = False
#         return admin_table,activ_table,not_activ_table
#
#
#     def get_breadcrumb(self,q_name,sub_q_name):
#         obj1 = BreadcrumbItem(name="Дашборд", is_active=False, url="/")
#         obj2 = BreadcrumbItem(name=q_name, is_active=True, url="#")
#         obj3 = BreadcrumbItem(name=sub_q_name, is_active=True, url="#")
#         obj4 = BreadcrumbItem(name="Таблица", is_active=True, url="#")
#         return  [ obj1, obj2,obj3,obj4 ]
