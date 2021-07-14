# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('access_token', models.CharField(unique=True, max_length=40, verbose_name='\u041a\u043b\u044e\u0447 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u0438')),
                ('created', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435',
                'verbose_name_plural': '\u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f',
            },
        ),
    ]
