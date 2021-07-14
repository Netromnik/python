# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from irk.utils.search.managers import ModelSearch
from irk.utils.search.tasks import elasticsearch_update


class SearchSignalAdminMixin(object):
    """
    Миксин для исправления ошибки с попаданием в индекс elasticsearch не актуальных данных

    Сигналы на добавление и удаление в индексе поиска при сохранении в админе работают неверно.
    Из-за транзакций в сигнал попадют данные еще не обновленные в админе. Для того чтобы в сигнале были актуальные
    данные, его вызов необходимо делать за пределами транзакции (переопределение change_view).
    Сигнал поиска навешивается автоматически на модели с методом search. Поэтому он отключается и переподключается
    заного, для того чтобы убрать его повторный вызов с неактуальными данными
    """

    def change_view(self, request, object_id, *args, **kwargs):
        # Из-за декоратора transaction.atomic для родительского change_view, задача на обновление
        # индекса elasticsearch берет не закоммиченные данные из БД. Поэтому вызываем ее после
        # выхода из блока transaction.atomic

        post_save.disconnect(ModelSearch.update_search, sender=self.model)
        result = super(SearchSignalAdminMixin, self).change_view(request, object_id, *args, **kwargs)

        if hasattr(self.model, 'search') and request.method == 'POST':
            ct = ContentType.objects.get_for_model(self.model)
            elasticsearch_update.delay(ct.id, object_id)

        post_save.connect(ModelSearch.update_search, sender=self.model)

        return result

    def add_view(self, request, *args, **kwargs):
        # Из-за декоратора transaction.atomic для родительского add_view, задача на обновление
        # индекса elasticsearch берет не закоммиченные данные из БД. Поэтому вызываем ее после
        # выхода из блока transaction.atomic

        post_save.disconnect(ModelSearch.update_search, sender=self.model)
        result = super(SearchSignalAdminMixin, self).add_view(request, *args, **kwargs)

        if hasattr(self.model, 'search') and request.method == 'POST':
            ct = ContentType.objects.get_for_model(self.model)
            elasticsearch_update.delay(ct.id, self.model.objects.latest('pk').pk)

        post_save.connect(ModelSearch.update_search, sender=self.model)

        return result
