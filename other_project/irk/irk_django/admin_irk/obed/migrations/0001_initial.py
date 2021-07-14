# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdNews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('url', models.URLField(null=True, verbose_name='\u0412\u043d\u0435\u0448\u043d\u044f\u044f \u0441\u0441\u044b\u043b\u043a\u0430', blank=True)),
                ('visible', models.BooleanField(default=True, db_index=True, verbose_name='\u0412\u044b\u0432\u043e\u0434\u0438\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
            ],
            options={
                'verbose_name': '\u043d\u043e\u0432\u0438\u043d\u043a\u0430',
                'verbose_name_plural': '\u043d\u043e\u0432\u0438\u043d\u043a\u0438',
            },
        ),
    ]
