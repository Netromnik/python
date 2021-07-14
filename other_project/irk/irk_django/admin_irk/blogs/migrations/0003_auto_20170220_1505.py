# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_auto_20161212_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='disable_comments',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u041e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435'),
        ),
        migrations.AddField(
            model_name='entry',
            name='hide_comments',
            field=models.BooleanField(default=False, db_index=True, verbose_name='\u0421\u043a\u0440\u044b\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438'),
        ),
    ]
