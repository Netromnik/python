import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


####

def validate_file(f):
    file_size = f.file.size

    if file_size > int(settings.MAX_UPLOAD_SIZE):
        raise ValidationError("Max size of file is %s MB" % settings.MAX_UPLOAD_SIZE // 1024 // 1024)

# File meneger
class CollectMedia(models.Model):
    name = models.CharField(max_length=30,unique=True)
    groups = models.ManyToManyField(
        "base.CustomGroup",
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="+",
    )

    obj = models.Manager()

    class Meta:
        verbose_name = _('Коллекция файлов')
        verbose_name_plural = _('Коллекции файлов')

    def __str__(self):
        return self.name


class File(models.Model):
    document = models.FileField(upload_to='documents/%Y/%m/%d/', validators=[validate_file, ], )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    collect = models.ForeignKey(to=CollectMedia, on_delete=models.DO_NOTHING,
                                related_name="colectFile", blank=True, null=True)
    obj = models.Manager()

    def url(self):
        return self.document.url

    def __str__(self):
        return os.path.basename(self.document.name)

    class Meta:
        verbose_name = _('Файл')
        verbose_name_plural = _('Файлы')


# Create  models  helpdesk.
