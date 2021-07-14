# ! TODO: Нужно подключить
#
from django.core.management import call_command

from celery import task as celery_task
from celery.app.task import Task as CeleryTask

from utils.exceptions import raven_capture
from irk_celery.celery_app import app


class Task(CeleryTask):
    """Перегруженный класс для задач celery, чтобы перехватывать ошибки и отсылать их в sentry"""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if status == 'FAILURE' or self.max_retries == self.request.retries:
            raven_capture(einfo.exc_info if einfo else None)

        return super(Task, self).after_return(status, retval, task_id, args, kwargs, einfo)


def task(*args, **kwargs):
    """Декоратор, превращающий функцию в задачу celery

    Должен использоваться вместо `celery.task`
    """

    kwargs['base'] = Task

    return celery_task(*args, **kwargs)


def _on_failure(self, exc, task_id, args, kwargs, einfo):
    """При получении исключения во время работы задачи celery, отсылаем его в sentry"""

    raven_capture(einfo.exc_info)


def make_command_task(name, **kwargs):
    """Конвертирование команды django в задачу celery

    Позиционные параметры ::
        name : имя задачи, например "runserver", "weather_grabber"

    Именованные параметры ::
        retry : повторить задачу в случае исключения

        Остальные параметры передаются в `Task.retry`
    """

    retry = kwargs.pop('retry', False)

    def run(self, *task_args, **task_kwargs):
        try:
            call_command(name, *task_args, **task_kwargs)
        except Exception as e:
            if retry:
                raise self.retry(args=task_args, kwargs=task_kwargs, exc=e, **kwargs)
            raise

    task_class = type(name, (Task,), {
        'run': run,
        'name': name,
        'on_failure': _on_failure,
    })

    app.tasks.register(task_class())

    return task_class
