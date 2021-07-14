# coding=utf-8
"""
Тесты для отложенных публикаций.
"""
import datetime
from django.test import RequestFactory
from irk.tests.unit_base import UnitTestBase
from irk.news.admin import SchedulerAdminMixin
from irk.news.models import ScheduledTask
from irk.news.tests.unit.material import create_material


class SchedulerAdminMixinTest(UnitTestBase):
    """
    Тесты класса SchedulerAdminMixin

    Вся логика будущих публикаций хранится в миксине SchedulerAdminMixin. Тут
    мы проверяем, что он корректно планирует/отменяет запланированные задания.
    Мы эмулируем вызов save_admin() админа. Если эти тесты проходят, то задачи
    должны успешно создаваться при работе редакторов через джанговскую адмику.
    """

    def setUp(self):
        super(SchedulerAdminMixinTest, self).setUp()

        class FakeModelAdmin(object):
            def save_model(self, req, obj, form, change):
                obj.save()

        class SomeModelAdmin(SchedulerAdminMixin, FakeModelAdmin):
            enable_scheduler = True

        self.admin = SomeModelAdmin()
        self.req = RequestFactory().post('/dummyurl/')  # не важен юрл

    def create_future_material(self):
        material = create_material('news', 'news')
        material.is_hidden = True
        material.stamp = datetime.date.today() + datetime.timedelta(days=1)
        material.published_time = datetime.time(12)
        return material

    def create_present_material(self):
        material = create_material('news', 'news')
        material.is_hidden = True
        material.stamp = datetime.datetime.now().date()
        material.published_time = datetime.datetime.now().time()
        return material

    def test_scheduler_do_nothing_if_enable_scheduler_is_not_set(self):
        """
        Если в наследнике миксина enable_scheduler = False, планировщик не планирует
        """
        self.admin.enable_scheduler = False

        material = self.create_future_material()
        self.admin.save_model(self.req, material, {}, True)

        self.assertFalse(hasattr(material, 'scheduled_task'))

    def test_scheduler_creates_task_for_future(self):
        """
        Если мы сохраняем материал в будущем, админ запланирует задачу на публикацию
        """
        material = self.create_future_material()

        self.admin.enable_scheduler = True
        self.admin.save_model(self.req, material, {}, False)

        # задача создана
        self.assertTrue(hasattr(material, 'scheduled_task'))

        # на ту же дату, что материал
        self.assertEqual(material.scheduled_task.when.date(), material.stamp)
        self.assertEqual(material.scheduled_task.when.time(), material.published_time)

        # и статус у нее "Запланирована"
        self.assertTrue(material.scheduled_task.is_scheduled)
        self.assertEqual(material.scheduled_task.task, ScheduledTask.TASK_PUBLISH)

    def test_task_unscheduled_if_time_is_not_set(self):
        """
        Если сбросить время публикации, задача помечается отмененной
        """
        material = self.create_future_material()
        self.admin.save_model(self.req, material, {}, False)

        # задача создана
        self.assertTrue(hasattr(material, 'scheduled_task'))
        self.assertTrue(material.scheduled_task.is_scheduled)

        # теперь сбросим время
        material.published_time = None
        self.admin.save_model(self.req, material, {}, True)

        self.assertEqual(material.scheduled_task.state, ScheduledTask.STATE_CANCELED)

    def test_task_unscheduled_if_material_becode_public(self):
        """
        Если опубликовать запланированный материал, задача помечается отмененной
        """
        material = self.create_future_material()
        self.admin.save_model(self.req, material, {}, False)

        # задача создана
        self.assertTrue(hasattr(material, 'scheduled_task'))
        self.assertTrue(material.scheduled_task.is_scheduled)

        # теперь опубликуем материал
        material.is_hidden = False
        self.admin.save_model(self.req, material, {}, True)

        # задача отменена
        self.assertEqual(material.scheduled_task.state, ScheduledTask.STATE_CANCELED)

    def test_task_not_created_if_time_is_present(self):
        """
        Задача не создается для материалов в прошлом, опубликованных или без времени
        """
        # материал-черновик не в будущем
        material = self.create_present_material()
        self.admin.save_model(self.req, material, {}, False)
        self.assertFalse(hasattr(material, 'scheduled_task'))

        # материал на завтра, но без времени
        material = self.create_future_material()
        material.published_time = None
        self.admin.save_model(self.req, material, {}, False)
        self.assertFalse(hasattr(material, 'scheduled_task'))

        # материал на завтра, но уже опубликованный (на практике такого не видел)
        material = self.create_future_material()
        material.is_hidden = False
        self.admin.save_model(self.req, material, {}, False)
        self.assertFalse(hasattr(material, 'scheduled_task'))

        # опубликованный материал не в будущем
        material = self.create_present_material()
        material.is_hidden = False
        self.admin.save_model(self.req, material, {}, False)
        self.assertFalse(hasattr(material, 'scheduled_task'))


class ScheduledTaskTest(UnitTestBase):
    """
    Тесты для модели ScheduledTask
    """

    def test_scheduled_task_publish(self):
        """
        Запланированная задача при выполнении публикует материал
        """
        m = create_material('news', 'news')
        m.is_hidden = True
        m.save()

        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        task = ScheduledTask(material=m)
        task.task = ScheduledTask.TASK_PUBLISH
        task.when = yesterday
        task.save()

        now = datetime.datetime.now()
        self.assertTrue(len(ScheduledTask.get_due_tasks(now)) == 1)

        task.run()

        # после запуска задачи, материал стал опубликован
        self.assertTrue(m.is_hidden == False)
        self.assertTrue(task.is_done == True)

        self.assertTrue(len(ScheduledTask.get_due_tasks(now)) == 0)

