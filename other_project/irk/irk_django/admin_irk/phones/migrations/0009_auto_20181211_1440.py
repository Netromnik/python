# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0008_auto_20180507_1706'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='firm',
        ),
        migrations.DeleteModel(
            name='PopularSearch',
        ),
        migrations.RemoveField(
            model_name='scanstore',
            name='firm',
        ),
        migrations.RemoveField(
            model_name='scanstore',
            name='ownership',
        ),
        migrations.DeleteModel(
            name='Searches',
        ),
        migrations.DeleteModel(
            name='UpdateSections',
        ),
        migrations.DeleteModel(
            name='UpdateUrls',
        ),
        migrations.RemoveField(
            model_name='vip',
            name='firm',
        ),
        migrations.DeleteModel(
            name='File',
        ),
        migrations.DeleteModel(
            name='ScanStore',
        ),
        migrations.DeleteModel(
            name='VIP',
        ),
    ]
