# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(default='scheduled', max_length=20, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441')),
                ('scheduler', models.CharField(max_length=250, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0449\u0438\u043a\u0430')),
                ('task_name', models.CharField(max_length=250, verbose_name='\u0418\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0437\u0430\u0434\u0430\u0447\u0438')),
                ('when', models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0443\u0441\u043a\u0430')),
                ('meta', models.TextField(null=True, verbose_name='\u0421\u0435\u0440\u0438\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f')),
            ],
        ),
    ]
