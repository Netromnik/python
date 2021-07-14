# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist


# TODO: Определить необходимость использования обработчика сигнала. Возможно пора его удалять.
def section_post_save(sender, instance, **kwargs):
    """Сигнал на создание/редактирование рубрики"""

    if instance.parent:
        instance.parent.recalculate_firms_count()


# TODO: Определить необходимость использования обработчика сигнала. Возможно пора его удалять.
def firm_post_save(sender, instance, **kwargs):
    """Сигнал на создание/сохранение фирмы"""

    if not kwargs.get('created') and instance.visblity_changed:
        for section in instance.section.all():
            section.recalculate_firms_count()


# TODO: Определить необходимость использования обработчика сигнала. Возможно пора его удалять.
def firm_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ('post_add', 'post_remove'):
        sections = instance.section.all()
        for section in sections:
            section.recalculate_firms_count()


# TODO: Определить необходимость использования обработчика сигнала. Возможно пора его удалять.
def maps_changed(sender, instance, **kwargs):
    """Добавление/удаление связки фирм и рубрик"""

    from irk.phones.models import Sections

    action = kwargs.get('action')

    # Данный обработчик цепляется к сигналу m2m_changed, в котором instance может быть объектом класса
    # phones.models.Firms или класса phones.models.Sections. Но судя по коду, ожидается только объект класса Firms,
    # поэтому, если instance - объект класса Sections, возникает ошибка AttributeError при вызовах `instance.section`.
    if isinstance(instance, Sections):
        return

    if action == 'pre_clear':
        setattr(instance, 'deleted_sections', list(instance.section.all()))
        return
    elif action == 'post_clear':
        sections = instance.deleted_sections
        is_active = False
    elif action == 'post_add':
        sections = list(instance.section.all())
        is_active = True
    else:
        return

    map(lambda s: s.recalculate_firms_count(), sections)
    for section in sections:
        if section.content_type:
            model = section.content_type.model_class()
            try:
                related_obj = section.content_type.get_object_for_this_type(pk=instance.pk)
            except ObjectDoesNotExist:
                pass
            else:
                model.objects.filter(pk=related_obj.pk).update(is_active=is_active)
