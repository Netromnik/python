# -*- coding: utf-8 -*-

import os
import glob
from django.conf import settings


def clean_thumbnails_pre_save(instance, **kwargs):
    from irk.gallery.models import Picture
    if instance.pk:
        picture = Picture.objects.get(pk=instance.pk)
        setattr(instance, 'old_watermark', picture.watermark)
    else:
        setattr(instance, 'old_watermark', False)


def clean_thumbnails_post_save(instance, **kwargs):
    if instance.old_watermark != instance.watermark:
        name, ext = os.path.splitext(instance.image.name)
        full_name = os.path.join(settings.MEDIA_ROOT, name)
        file_list = glob.glob(full_name + '_*')
        for f in file_list:
            os.remove(f)
