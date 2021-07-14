# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phones', '0007_auto_20170912_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firms',
            name='show_comments',
        ),
        migrations.AlterField(
            model_name='firms',
            name='disable_comments',
            field=models.BooleanField(default=False, help_text='\u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u0432\u044b\u0432\u043e\u0434\u0438\u0442\u0441\u044f', db_index=True, verbose_name='\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AlterField(
            model_name='firms',
            name='hide_comments',
            field=models.BooleanField(default=False, help_text='\u043e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u044b \u0431\u0435\u0437 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043f\u0440\u043e 24 \u0447\u0430\u0441\u0430', db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438'),
        ),
        migrations.DeleteModel(
            name='Prices',
        ),
    ]