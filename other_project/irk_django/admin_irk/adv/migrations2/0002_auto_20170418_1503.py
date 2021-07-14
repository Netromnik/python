# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='url',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='url',
            field=models.URLField(max_length=255, null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430', blank=True),
        ),
    ]
