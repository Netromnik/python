from swapper import swappable_setting
from django.db import models
from .base.models import AbstractNotification, notify_handler  # noqa


class Notification(AbstractNotification):
    is_push = models.BooleanField(default=True)
    def push_as_read(self):
        if self.is_push:
            self.is_push =False
            self.save()

    class Meta(AbstractNotification.Meta):
        abstract = False
        swappable = swappable_setting('notifications', 'Notification')
