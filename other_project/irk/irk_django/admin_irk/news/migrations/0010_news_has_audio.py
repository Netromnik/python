# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0008_auto_20170720_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='has_audio',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u0415\u0441\u0442\u044c \u0430\u0443\u0434\u0438\u043e'),
        ),
    ]
