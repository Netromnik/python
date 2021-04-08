from django.db import models
from django.utils.translation import gettext_lazy as _

# Managers
from base.managers.chat import ChatObjManager
from .base_model import BaseHistoryModel
# from .tasks import Task
from .users import CustomUser


###

class ChatModel(BaseHistoryModel):
    task = models.ForeignKey(
        "base.Task",
        models.DO_NOTHING,
        verbose_name=_("task")
    )
    user = models.ForeignKey(
        CustomUser,
        models.CASCADE,
        verbose_name=_('user'),
    )
    mesenge = models.TextField(_("messenge"),)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    obj = ChatObjManager()

# def get_all_ticket_for(queqe):
#     streams =Stream.obj.filter(queue=queqe)
#     tasks = Task.obj.filter(stream__in=streams)
#
#     return tasks