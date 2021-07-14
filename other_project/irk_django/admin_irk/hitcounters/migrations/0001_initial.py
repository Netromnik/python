# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialScrollStatistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('point_1', models.PositiveIntegerField(default=0, verbose_name='\u043e\u0442\u043a\u0440\u044b\u043b\u0438')),
                ('point_2', models.PositiveIntegerField(default=0, verbose_name='\u043d\u0430\u0447\u0430\u043b\u0438 \u0447\u0438\u0442\u0430\u0442\u044c')),
                ('point_3', models.PositiveIntegerField(default=0, verbose_name='\u0434\u043e\u0441\u043a\u0440\u043e\u043b\u0438\u043b\u0438 \u0434\u043e \u0441\u0435\u0440\u0435\u0434\u0438\u043d\u044b')),
                ('point_4', models.PositiveIntegerField(default=0, verbose_name='\u0434\u043e\u0441\u043a\u0440\u043e\u043b\u0438\u043b\u0438 \u0434\u043e \u043b\u0430\u0439\u043a\u043e\u0432')),
                ('point_5', models.PositiveIntegerField(default=0, verbose_name='\u0447\u0438\u0442\u0430\u043b\u0438 \u043a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438')),
                ('start_read', models.PositiveIntegerField(default=0, verbose_name='\u043d\u0430\u0447\u0430\u043b\u0438 \u0447\u0438\u0442\u0430\u0442\u044c \u0442\u0435\u043a\u0441\u0442')),
                ('read_time', models.PositiveIntegerField(default=0, verbose_name='\u0432\u0440\u0435\u043c\u044f \u0447\u0442\u0435\u043d\u0438\u044f (\u0441\u0435\u043a)')),
            ],
        ),
    ]
