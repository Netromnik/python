from fsm.models import Task
from mixin.generic_viev.page import Page,BreadcrumbItem
from  django.shortcuts import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.utils.safestring import mark_safe
from djangoChat.models import Message
import json
from fsm.stat_logick import dispath
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

class DetailTask(FormView,Page):
    title = "Просмотр Заявки"
    success_url = '?thanks=ok'
    template_name = "locations/ticket_crud/view/ditail_ticket.html"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Заявка",is_active=True,url="/wiki/"),]


    def get_context_data(self, **kwargs):
        kwargs =super(DetailTask, self).get_context_data(**kwargs)
        pk = kwargs['pk']
        try:
            kwargs["task"] = task = Task.object.get(pk =pk)
            kwargs["alerts"] = self.get_alert_target(task.pk)
            kwargs['data_js'] = self.get_chat_json(task)
            if task.raiting == -1 and task.state == "Закрыта" and task.owner == self.request.user:
                kwargs['task_is_raiting'] = True
            kwargs["task_active_button"] = self.get_active_event(task)
        except ObjectDoesNotExist:
            raise Http404("Not founds")
        return kwargs

    def get_alert_target(self,task_id):
        ct = ContentType.objects.get(model="task")
        return Notification.objects.filter(actor_content_type=ct,actor_object_id=task_id)

    def get_active_event(self,task:Task)->list:
        return dispath(task.state,task.get_role(self.request.user),task.pk)

    def get_chat_json(self,task:Task):
        # chat json start
        r = Message.objects.filter(task=task).order_by('time')
        if r.count() != 0:
            res = []
            for msgs in list(r):
                res.append(
                    {
                        'username': msgs.user.get_full_name(),
                        'actor': msgs.type,
                        'content': msgs.message,
                        'date': msgs.time.strftime('%H:%M:%S,%m/%d/%y').lstrip('0')
                    }
                )
                if msgs.is_new:
                    msgs.is_new = False
                    msgs.save()
            data = json.dumps(res)
            # end json
            return mark_safe(data)
        else:
            return False
    def form_valid(self, form):
        data = form.cleaned_data
        data['change_user'] = self.request.user
        data['task_id'] = form.id
        Task.manager_task_detail.save_via_form(**data)
        return super().form_valid(form)


