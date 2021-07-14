# coding=utf-8
# Этот файл станет модулем postmeta, когда news.models станет пакаджем

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models


class Postmeta(models.Model):
    """
    Кастомные поля материала

    Строковые пары ключ-значение с произволным содержимым, которые можно добавить к любому материалу.
    Используются для организации кастомной логики на фронтенде.

    Чтобы добавить кастомные поля к любой модели, добавьте ее как ForeignKey в эту модель
    """

    # я специально не использую generickey, мне ближе прямое перечисление
    material = models.ForeignKey('news.BaseMaterial', related_name='postmeta', null=True)
    landings_covidpage = models.ForeignKey('landings.CovidPage', related_name='postmeta', null=True)

    key = models.CharField('Поле', max_length=191, db_index=True)
    value = models.CharField('Значение', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Мета-поле'
        verbose_name_plural = 'Мета-поля'
        unique_together = ('material', 'key')

    def __unicode__(self):
        return 'Postmeta object #{}'.format(self.id)


class PostmetaMixin(object):

    def get_postmeta(self):
        """
        Мета-поля в виде словаря

        Для удобного использования в шаблоне: {{ material.get_postmeta.key }}
        """
        meta = {meta.key: meta.value for meta in self.postmeta.all()}
        return meta
