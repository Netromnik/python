from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import Http404
from django.views.generic.edit import FormView

from base.models import Task, LogHistory, ChatModel
from mixin.generic_viev.page import Page, BreadcrumbItem


class DetailTask(FormView,Page):
    title = "Просмотр Заявки"
    success_url = '?thanks=ok'
    template_name = "locations/ticket_crud/view/ditail_ticket.html"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Заявка",is_active=True,url="/wiki/"),]

    def post(self, request, *args, **kwargs):
        self.task = Task.obj.get(pk=kwargs["pk"])
        try:
            self.form_class = Task.manager_task_detail.get_task_form(self.request.user,self.task)
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        except ObjectDoesNotExist:
            raise Http404("Not found")

    def get(self, request, *args, **kwargs):
        self.task = Task.obj.get(pk=kwargs["pk"])
        return super(DetailTask, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        try:
            kwargs["task"] = Task.manager_task_detail.get_task(self.task)
            kwargs["alerts"] = LogHistory.alert_manager.get_alerts_for_task(self.task)
            kwargs["chat"] = Task.manager_task_detail.get_chat(self.task,self.request.user)
            self.form_class = Task.manager_task_detail.get_task_form(self.request.user,self.task) ## avtors asignet None
            kwargs = super().get_context_data(**kwargs)
        except ObjectDoesNotExist:
            raise Http404("Not founds")
        except:
            pass
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        messenge = ChatModel()
        messenge.task = self.task
        messenge.mesenge = data["mesenge"]
        Task.manager_task_state.chenge_status(self.task,self.request.user,data["status"])
        messenge.user = self.request.user
        messenge.save()
        return super().form_valid(form)


