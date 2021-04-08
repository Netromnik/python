import calendar
from datetime import datetime, timedelta

from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .base_model import BaseHistoryModel
from .file import File
from .stream import Stream
from .users import CustomUser


def set_time_default():
    date = datetime.now(tz=timezone.get_current_timezone())
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    return date


from base.managers.task import DetailTaskManager, CustomManegerTaskSelf, StateTaskManager


class Task(BaseHistoryModel):
    STATUS = (
        ("W", "Ожидает"),
        ("O", "Открыта"),
        ("H", "Замороженно"),
        ("S", "Решено"),
        ("C", "Закрыто")
    )
    ACTIVE = (
        ("G", "Взять"),
        ("P", "Положить"),
        ("L", "Перейти"),
    )

    title = models.CharField(_("title"),
                             max_length=50)
    description  = models.TextField(_("Описание"))
    stream = models.ForeignKey(Stream, on_delete=models.DO_NOTHING,verbose_name="Категория")
    asignet_to = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,blank=True,related_name='asing_to',null=True,verbose_name="Ответственный")
    chenge_user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,blank=True,related_name='chenge_user',null=True,verbose_name="Последний изменивший")
    file = models.ForeignKey(File, on_delete=models.DO_NOTHING,blank=True,related_name='file_re',null=True,verbose_name="Файл")
    autors = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,related_name='autorTask',verbose_name="автор")
    status = models.CharField(max_length=1, choices=STATUS,verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="Дата обновления")
    date_due = models.DateField(default=set_time_default,verbose_name="Дата оканчания")
    obj = models.Manager()

    manager_user_self = CustomManegerTaskSelf()
    manager_task_detail = DetailTaskManager()
    manager_task_state = StateTaskManager()

    def get_view_url(self):
        return reverse("views:detail_ticket", args=[self.pk])

    def get_status(self):
        for i in self.STATUS:
            if i[0] == self.status:
                return i[1]

    def upload_file(self, file):
        file = File.obj.create(document=file)
        self.file = file
        self.save()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
