# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from irk.utils.tasks.helpers import Task, make_command_task
from irk_celery.celery_app import app


class ElasticSearchTask(Task):
    """Сохранение данных об объекте в ElasticSearch"""

    name = 'utils.search.tasks.elasticsearch_update'

    def run(self, content_type_id, object_pk):
        """
        :param content_type_id: идентификатор модели из `django.contrib.contenttypes.models.ContentType`
        :type content_type_id:  int
        :param object_pk:       идентификатор объекта
        :type object_pk:        int
        """

        ct = ContentType.objects.get(id=content_type_id)
        model_cls = ct.model_class()

        if not hasattr(model_cls, 'search'):
            return

        search = model_cls.search.model_search
        if not search.get_queryset().filter(pk=object_pk).exists():
            # Объект скрыли/удалили, и его нужно убрать из индекса
            # В этом случае объекта в базе уже нет, поэтому работаем только с PK
            search.delete(object_pk)
        else:
            obj = ct.get_object_for_this_type(pk=object_pk)
            search.put(obj.pk, obj)

    def delay_for_object(self, instance):
        """
        :param instance: сохраняемый объект модели.
        """

        ct = ContentType.objects.get_for_model(instance)

        return self.delay(ct.pk, instance.pk)


elasticsearch_update = ElasticSearchTask()
app.tasks.register(elasticsearch_update)

elasticsearch = make_command_task('elasticsearch')
