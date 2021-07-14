# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0006_currentlog_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='click_count',
            field=models.IntegerField(default=0, verbose_name='\u0422\u0435\u043a\u0443\u0449\u0435\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043a\u043b\u0438\u043a\u043e\u0432'),
        ),
        migrations.AddField(
            model_name='banner',
            name='click_monitor',
            field=models.BooleanField(default=False, verbose_name='\u041c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u0442\u044c \u043a\u043b\u0438\u043a\u0438'),
        ),
    ]
