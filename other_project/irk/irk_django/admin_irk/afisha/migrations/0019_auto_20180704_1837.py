# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0018_auto_20180507_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ramblerhall',
            name='hallid',
            field=models.CharField(max_length=100, verbose_name='hall id', db_index=True),
        ),
    ]
