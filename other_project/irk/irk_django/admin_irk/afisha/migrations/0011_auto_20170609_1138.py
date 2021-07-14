# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('afisha', '0010_auto_20170511_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='kassysession',
            name='show_datetime',
            field=models.DateTimeField(null=True, verbose_name='\u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u043c\u044b\u0435 \u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f', db_index=True),
        ),
        migrations.AddField(
            model_name='kinomaxsession',
            name='show_datetime',
            field=models.DateTimeField(null=True, verbose_name='\u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u043c\u044b\u0435 \u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f', db_index=True),
        ),
        migrations.AddField(
            model_name='ramblersession',
            name='show_datetime',
            field=models.DateTimeField(null=True, verbose_name='\u043e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0435\u043c\u044b\u0435 \u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f', db_index=True),
        ),
        migrations.AlterField(
            model_name='kassysession',
            name='datetime',
            field=models.DateTimeField(null=True, verbose_name='\u0434\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f', db_index=True),
        ),
    ]
