#coding=utf-8
from __future__ import unicode_literals

import pytest
import datetime
import mock

from irk.scheduler.tasks import BaseScheduler
from irk.scheduler.models import Task


@pytest.fixture
def scheduler():
    class TestScheduler(BaseScheduler):
        pass

    return TestScheduler()


@pytest.mark.django_db
def test_add_task_creates_record_in_database():
    """Задачи добавляется в базу данных и планировщики не пересекаются"""

    # первый планировщик, первая задача
    class NewsScheduler(BaseScheduler):
        pass

    sched = NewsScheduler()
    when = datetime.datetime(2018, 9, 10, 15, 40)
    sched.add_task('sometask', when, meta='любой объект')

    task = Task.objects.filter(scheduler='NewsScheduler').all()[0]
    assert task.task_name == 'sometask'
    assert task.when == when

    # вторая задача
    class SocpultScheduler(BaseScheduler):
        pass

    sched = SocpultScheduler()
    when = datetime.datetime(2018, 9, 11, 16, 22)
    sched.add_task('othertask', when, meta='любой объект')
    task = Task.objects.filter(scheduler='SocpultScheduler').all()[0]

    assert task.when == when
    assert task.task_name == 'othertask'


@pytest.mark.django_db
def test_due_tasks(scheduler):
    now = datetime.datetime.now()
    scheduler.add_task('task1', when=now)
    scheduler.add_task('task2', when=now+datetime.timedelta(seconds=30))

    tasks = scheduler.get_due_tasks()
    assert len(tasks) == 1
    assert tasks[0].task_name == 'task1'

    tasks = scheduler.get_due_tasks(now+datetime.timedelta(seconds=31))
    assert len(tasks) == 2
    assert tasks[1].task_name == 'task2'


@pytest.mark.skip(reason="Пока не реализовано")
def test_meta_serialization_test(scheduler):
    now = datetime.datetime.now()
    task = Task(task_name='anything', when=now, meta=4)
    task.save()

    scheduler.get_due_tasks()


@pytest.mark.django_db
def test_completed_tasks_dont_run(scheduler):
    """Выполненные и отмененные не выполняются"""
    task = Task(when=datetime.datetime.now(), state=Task.STATE_DONE)
    task.save()
    task = Task(when=datetime.datetime.now(), state=Task.STATE_CANCELED)
    task.save()

    assert len(scheduler.get_due_tasks()) == 0


@pytest.mark.django_db
def test_task_executed_on_time():
    """Когда время приходит, задача передается на выполнение"""

    class NewsScheduler(BaseScheduler):
        called = False
        def run_task(self, task):
            NewsScheduler.called = True
            assert task.task_name == 'task1'

    sched = NewsScheduler()
    when = datetime.datetime.now() - datetime.timedelta(seconds=1)  # секунду назад
    sched.add_task('task1', when)

    sched.tick()
    assert NewsScheduler.called


@pytest.mark.django_db
def test_task_marked_as_done_after_run(scheduler):
    scheduler.run_task = mock.Mock()

    scheduler.add_task('sometask', '2018-09-12')  # дата в прошлом
    scheduler.tick()

    assert scheduler.run_task.called
    task = Task.objects.all()[0]
    assert task.state == Task.STATE_DONE


@pytest.mark.django_db
def test_exception_in_one_task_cant_stop_other_tasks_from_run(scheduler):
    scheduler.run_task = mock.Mock(side_effect=RuntimeError('Boom!'))
    scheduler.add_task('one', '2018-09-13')
    scheduler.add_task('two', '2018-09-13')
    scheduler.add_task('three', '2018-09-13')

    try:
        scheduler.tick()
    except RuntimeError:
        pass

    # несмотря на экзепшн в задании, все равно все таски передавались в run_task
    assert scheduler.run_task.call_count == 3


@pytest.mark.django_db
def test_task_dont_marked_as_complete_if_rised_exception(scheduler):
    # будет экзпешн при втором вызове метода run_task
    scheduler.run_task = mock.Mock(side_effect=['ok', RuntimeError('Boom!')])

    task1 = scheduler.add_task('one', '2018-09-13')  # будет выполнено
    task2 = scheduler.add_task('two', '2018-09-13')  # выбросит исключение
    try:
        scheduler.tick()
    except RuntimeError:
        pass

    task1.refresh_from_db()
    task2.refresh_from_db()

    assert task1.state == Task.STATE_DONE
    assert task2.state == Task.STATE_SCHEDULED
