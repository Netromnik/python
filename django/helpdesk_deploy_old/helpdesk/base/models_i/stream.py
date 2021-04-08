from django.db import models
from django.utils.translation import gettext_lazy as _

from base.managers.stream import StreamManeger


class Stream(models.Model):
    queue = models.ForeignKey("base.Queue", on_delete=models.DO_NOTHING)
    in_public = models.BooleanField(_("Отображения"), help_text=_("Будет использованно для отображения в форму"),
                                    default=True)

    description = models.CharField(
        _('description'),
        max_length=30,
        blank=True
    )
    obj = models.Manager()
    support_manager = StreamManeger()

    def __str__(self):
        return self.description
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

