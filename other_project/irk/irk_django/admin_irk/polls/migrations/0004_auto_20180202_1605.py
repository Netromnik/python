# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20170406_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollvote',
            name='created',
            field=models.DateTimeField(default=django.utils.datetime_safe.datetime.now, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='quiz',
            name='content',
            field=models.TextField(verbose_name='\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435', blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='title',
            field=models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a'),
        ),
    ]
