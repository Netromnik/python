from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse

from base.models import Task, ChatModel, LogHistory


def a_crete(url,body):
    a = "<a href= {}> {} </a>".format(url,body)
    return a

@receiver(post_save, sender=Task)
def alert_task(sender, **kwargs):
    # obj = {'instance': "","raw": False, 'using': 'default', 'update_fields': None}
    ct = ContentType.objects.get(model = sender.__name__.lower())
    task = kwargs['instance']
    url = reverse("view:detail_ticket",args= [task.pk])
    update_fields = kwargs.get("update_fields")
    if update_fields == None:
        return
    if not "status" in update_fields:
        return
    messenge = "В заявка {} был изменён статус на <b>{}</b>".format(a_crete(url, "#{}".format(task.pk), ),
                                                                    task.get_status())

    log = LogHistory()
    log.content_type = ct
    log.action_flag = log.CHANGE
    log.user = task.chenge_user
    log.object_id = task.pk
    log.change_message = messenge
    log.save()


@receiver(post_save, sender=ChatModel)
def alert_chat(sender, **kwargs):
    # obj = {'instance': "","raw": False, 'using': 'default', 'update_fields': None}
    ct = ContentType.objects.get(model = sender.__name__.lower())
    chat = kwargs['instance']
    url = reverse("view:detail_ticket",args= [chat.task.pk])
    messenge = "Новое сообщения в заявки {}".format(a_crete(url,"#{}".format(chat.task.pk)))
    log = LogHistory()
    log.content_type = ct
    log.action_flag = log.CHANGE
    log.user = chat.user
    log.object_id = chat.pk
    log.change_message = messenge
    log.save()
