
from django.db import models
from django.utils.translation import gettext_lazy as _

from base.managers.Queue import QueueSupportManagerKanban, QueueSupportManagerTable
from .users import CustomGroup
"""

"""
class Queue(models.Model):
    name = models.CharField(
        _('name'),
        max_length=30,
        unique=True,
    )
    order = models.PositiveIntegerField("Порядок отоброжения",default=0)
    groups = models.ManyToManyField(
        CustomGroup,
        verbose_name=_('groups'),
        blank=True,
        related_name="queue_set",
        related_query_name="queue",
    )
    obj = models.Manager()
    support_manager_table = QueueSupportManagerTable()
    support_manager_kanban = QueueSupportManagerKanban()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Очередь')
        verbose_name_plural = _('Очереди')
        ordering = ['-order']

