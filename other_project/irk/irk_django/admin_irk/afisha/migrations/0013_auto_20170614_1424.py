# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0012_auto_20170609_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentsession',
            name='min_price',
            field=models.IntegerField(null=True, verbose_name='\u0426\u0435\u043d\u0430 \u043e\u0442'),
        ),
        migrations.AddField(
            model_name='sessions',
            name='price',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
