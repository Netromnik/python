from django.contrib.contenttypes.models import ContentType
from django.db import models

from base.models_i.tasks import Task


class AlertSupport(models.Manager):
    ## return alert
    def get_alerts_for_task(self,task):
        obj_list = []
        ct_task = ContentType.objects.get(model="task")
        qury_f = self.filter(content_type = ct_task,object_id =  task.pk )
        for q in qury_f:
            obj = {}
            obj["class"] = q.get_action_flag_alert()
            obj["messenge"] = q.change_message
            obj["date"] = q.action_time
            obj_list.append(obj)
        return obj_list

    def get_alert_task_user(self,user):
        # obj = {
        #     "status" :"info",
        #     "body": "Заявка 1 была изменена"
        # }
        ct_task = ContentType.objects.get(model="task")
        task_q_summ = Task.manager_user_self.all_task_for_user(user)
        task_q_summ = [ i.pk for i in task_q_summ ]
        task_alert = self.filter(content_type = ct_task,object_id__in = task_q_summ)
        return list(task_alert)

    def get_alert_task_chat_user(self,user):
        chat_id = Task.manager_user_self.all_chat_for_user(user)
        ct_chat = ContentType.objects.get(model="chatmodel")
        task_alert = self.filter(content_type = ct_chat,object_id__in = chat_id)
        return list(task_alert)

    def serilazer(self,data_q,status="info"):
        # obj = {
        #     "status" :"info",
        #     "body": "Заявка 1 была изменена"
        # }
        list_obj = [ {
            "status": status,
            "body": alert.change_message
        } for alert in data_q ]
        return list_obj


    def get_alert_user(self, user):
        ct_task_chat = list(ContentType.objects.filter(model__in=["task","chatmodel"]))
        # get all sub pk fields
        task_q_summ = set([ task.pk for task in Task.manager_user_self.all_task_for_user(user)])
        task_q_summ |=    set([chat.pk for chat in Task.manager_user_self.all_chat_for_user(user)])
        # get row in bd
        task_alert = self.filter(content_type_id__in = ct_task_chat,object_id__in = task_q_summ)
        data = self.serilazer(task_alert)
        return data