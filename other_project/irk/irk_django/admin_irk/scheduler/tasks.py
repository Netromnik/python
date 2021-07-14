# coding=utf-8
from __future__ import unicode_literals, print_function

import datetime
import json
import logging

from irk.scheduler.models import Task
from irk.utils.tasks.helpers import make_command_task


logger = logging.getLogger(__name__)

class BaseScheduler(object):
    """
    Родитель всех планировщиков

    Отвечает за сохранение и загрузку задач из базы данных и передачу задач
    на выполнение в дочерние классы в функцию run_task.
    """

    def add_task(self, task_name, when, meta=None):
        """Запланировать задание"""
        task = Task()
        task.scheduler = self.__class__.__name__
        task.task_name = task_name
        task.when = when
        task.meta = meta
        task.save()
        return task

    def tick(self, moment=None):
        """
        Выполняет задачи, которые пора делать, используя метод run_task.

        Этот метод вызывается через Селери-бит раз в минуту.
        moment используется для тестирования
        """
        logger.debug('Tick')
        tasks = self.get_due_tasks(moment)
        logger.debug('Found %s tasks to run', len(tasks))

        done = 0
        err = None
        for task in tasks:
            logger.debug('Running task %r', task)
            try:
                self.run_task(task)
                task.state = Task.STATE_DONE
                task.save()
                logger.debug('Task complete and saved')
            except Exception as err:
                logger.exception('Exception while running task')
            done += 1

        if err:
            raise err

        return done

    def get_due_tasks(self, moment=None):
        """
        Запрашивает из базы данных список задач, которые пора выполнить
        """
        if not moment:
            moment = datetime.datetime.now()
        return Task.objects.filter(when__lte=moment, state=Task.STATE_SCHEDULED)

    @classmethod
    def get_scheduled_tasks(cls, task_name=None, moment=None):
        """
        Возвращает запланированные на будущее задачи
        """
        if not moment:
            moment = datetime.datetime.now()
        tasks = Task.objects.filter(when__gte=moment, state=Task.STATE_SCHEDULED, scheduler=cls.__name__)
        if task_name:
            tasks = tasks.filter(task_name=task_name)

        return tasks

    def run_task(self, task):
        raise NotImplementedError


class SocpultScheduler(BaseScheduler):
    """
    Планировщик и выполнятель заданий для публикации постов в соцсетях
    """
    def run_task(self, task):

        # эти импорты в заголовке вызывают цикличный импорт
        from irk.news.tasks import social_post_task
        from irk.news.models import SocialPost

        if task.task_name == 'publish':
            # тут нужно поставить публикацию в очередь через селери

            # найдем материал, для которого эта задача запланирована
            meta = json.loads(task.meta)
            social_post = SocialPost.objects.get(pk=meta['social_post'])
            task = social_post_task.delay(social_post.network, social_post.material_id, social_post.id, meta['data'])
            social_post.task_id = task.id
            social_post.save()

            # if task.id in (10,9,8):
            #    raise ValueError('Просто чтобы повторить выполнение задания'.encode('utf-8'))


scheduler_socpult = make_command_task(str('scheduler_socpult'))
