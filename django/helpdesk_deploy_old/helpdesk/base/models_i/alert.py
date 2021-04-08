from django.contrib.auth.models import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.managers.log_history import AlertSupport
from .users import CustomUser


class LogHistory(models.Model):
    ADDITION = 1
    CHANGE = 2
    DELETION = 3

    ACTION_FLAG_CHOICES = (
        (ADDITION, _('Addition')),
        (CHANGE, _('Change')),
        (DELETION, _('Deletion')),
    )

    action_time = models.DateTimeField(
        _('action time'),
        default=timezone.now,
        editable=False,
    )
    user = models.ForeignKey(
        CustomUser,
        models.CASCADE,
        verbose_name=_('user'),
    )
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True, null=True,
    )

    object_id = models.TextField(_('object id'), blank=True, null=True)
    action_flag = models.PositiveSmallIntegerField(_('action flag'), choices=ACTION_FLAG_CHOICES)
    change_message = models.TextField(_('change message'), blank=True)
    alert_manager = AlertSupport()

    def get_action_flag_alert(self):
        if self.action_flag == self.ADDITION:
            return "info"
        if self.action_flag == self.CHANGE:
            return "warning"
        if self.action_flag == self.DELETION:
            return "danger"

    class Meta:
        verbose_name = _('История')
        verbose_name_plural = _('История')
        db_table = 'log_history'
        ordering = ['-action_time']
