# -*- coding: utf-8 -*-

import datetime


def extract_html5_banner(sender, instance, **kwargs):
    """Распаковка архива с баннером"""

    from irk.adv.models import File

    if not isinstance(instance, File):
        return

    if instance.html5 and not instance.html5.is_extract():
        instance.html5.extract()


def period_post_save(sender, instance, **kwargs):
    """Сохранение периода баннера"""

    instance.banner.last_modified = datetime.datetime.now()
    instance.banner.save()
