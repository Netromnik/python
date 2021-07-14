# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0013_auto_20170614_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessions',
            name='price',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
