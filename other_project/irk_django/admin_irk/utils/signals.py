# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

from django.db.models import signals
from django.apps import apps

logger = logging.getLogger(__name__)


def connect(signal, receiver, sender=None, weak=True, dispatch_uid=None, with_children=False):
    """Обертка вокруг `django.dispatch.dispatcher.Signal.Signal`

    При вызове может искать все модели-наследники переданной модели и подключать этот сигнал к ним же

    Параметры::

        signal: название сигнала для подключения.
            Может быть или строкой 'post_save', или callable объектом:
            >>> from django.db.models.signals import post_save
            >>> connect(post_save, SomeModel)

        check_children: при указанном True производит поиск моделей-наследников

    Все остальные параметры соответствуют сигнатуре метода `django.dispatch.dispatcher.Signal.Signal.connect`

    """

    if isinstance(signal, (str, unicode)):
        signal = getattr(signals, signal)

    models = [sender, ]
    if with_children:
        for model in apps.get_models():
            if issubclass(model, sender) and model != sender:
                models.append(model)

    for model in models:
        signal.connect(receiver, model, weak, dispatch_uid)
        logger.debug('Connecting signal {} to model {}'.format(signal, model))