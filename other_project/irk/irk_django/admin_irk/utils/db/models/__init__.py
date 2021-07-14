# -*- coding: utf-8 -*-

import logging

from django.core.exceptions import ObjectDoesNotExist


logger = logging.getLogger(__name__)


class Loggable(object):
    """Mix-in для логирования изменений полей в модели

    Пример использования::
        class News(Loggable, models.Model):
            title = models.CharField()
        obj = News(title='test')
        obj.save()
        obj.title = 'new field value should be logged now'
        obj.save()
    """

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old = self._meta.concrete_model.objects.get(pk=self.pk)
            except ObjectDoesNotExist:
                # Вываливается в том случае, если PK вручную ставится только что созданному объекту
                # Например, в `django-dynamic-fixture`
                logger.warning('Object %(app)s.%(model)s have a PK #%(pk)s, but does\'nt exists in the database' % {
                    'app': self._meta.app_label,
                    'model': self._meta.object_name,
                    'pk': self.pk,
                })
            else:
                changed_fields = {}

                for field in self._meta.fields:
                    field_name = field.name
                    old_value = getattr(old, field_name)
                    new_value = getattr(self, field_name)
                    if old_value != new_value:
                        changed_fields[field_name] = u'%s -> %s' % (old_value, new_value)

                if changed_fields:
                    logger.debug('%(app)s.%(model)s object #%(pk)s have changes: %(values)s' % {
                        'app': self._meta.app_label,
                        'model': self._meta.object_name,
                        'pk': self.pk,
                        'values': ', '.join(['%s: %s' % (k, v) for k, v in changed_fields.items()])
                    })

        super(Loggable, self).save(*args, **kwargs)
