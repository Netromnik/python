# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0007_auto_20170502_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='prism',
            name='svg',
            field=models.TextField(verbose_name='svg', blank=True),
        ),
    ]
