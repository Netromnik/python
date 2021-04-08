from django.shortcuts import resolve_url
from django.views.generic.edit import UpdateView

from base.models import Task
from mixin.generic_viev.page import LoginRequiredMixin, BreadcrumbItem
from .CreateTicket import TicketForm


class TaskUpdate(LoginRequiredMixin,UpdateView):
    model = Task
    form_class = TicketForm
    title = "Редактирования заявки"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Редактирования заявки",is_active=True,url="/wiki/"),]
    menu_item = []

    template_name = "locations/ticket_crud/create/ticket_create.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["breadcrumb_list"] = self.breadcrumb_list
        kwargs["title"] = self.title
        kwargs["menu_item"] = self.menu_item
        return  kwargs

    def form_valid(self, form):
        if form.is_valid():
            data = form.cleaned_data
            t = Task.obj.get(pk = self.kwargs["pk"])
            t.title = data['title']
            t.description = data['description']
            t.stream = data['stream']
            t.date_due = data['date_due']
            t.autors = self.request.user
            t.chenge_user = self.request.user
            t.status = t.STATUS[0][0]
            t.save()
            # file =self.request.FILES.get('files')
            # if file != None:
            #     t.upload_file.(file)

        return super(TaskUpdate, self).form_valid(form)


    def get_success_url(self):
        return resolve_url("view:detail_ticket",pk=self.kwargs['pk'])