# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0008_auto_20170510_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='guide',
            name='price',
            field=models.CharField(default=b'', max_length=255, verbose_name='\u0426\u0435\u043d\u044b', blank=True),
        ),
        migrations.AddField(
            model_name='hall',
            name='price',
            field=models.CharField(default=b'', max_length=255, verbose_name='\u0426\u0435\u043d\u044b', blank=True),
        ),
        migrations.RemoveField(
            model_name='hall',
            name='description',
        ),
        migrations.RemoveField(
            model_name='hall',
            name='notice',
        ),
    ]
