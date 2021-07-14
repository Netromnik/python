# coding=utf-8
from __future__ import unicode_literals

from django.db import models


class Task(models.Model):
    """
    Задача, которую нужно выполнить в заданное время
    """

    STATE_SCHEDULED = 'scheduled'
    STATE_DONE = 'done'
    STATE_CANCELED = 'canceled'

    def __repr__(self):
        return 'Task(id={0.id}, state={0.state}, when={0.when}, scheduler={0.scheduler}, '\
               'task_name={0.task_name}>'.format(self).encode('utf-8')

    def __str__(self):
        return '<Task id={0.id}>'.format(self)

    state = models.CharField('Статус', max_length=20, default=STATE_SCHEDULED)
    scheduler = models.CharField('Идентификатор планировщика', max_length=250)
    task_name = models.CharField('Идентификатор задачи', max_length=250)
    when = models.DateTimeField('Время запуска')
    meta = models.TextField('Сериализованные данные', null=True, blank=True)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата обновления', auto_now=True)
