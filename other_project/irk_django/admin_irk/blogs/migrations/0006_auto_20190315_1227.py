# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0005_auto_20180507_1756'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='author',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='site',
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
    ]
