# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20171120_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpamPattern',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u041a\u043b\u044e\u0447\u0435\u0432\u043e\u0435 \u0441\u043b\u043e\u0432\u043e')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0430\u043d\u0442\u0438\u0441\u043f\u0430\u043c',
                'verbose_name_plural': '\u0430\u043d\u0442\u0438\u0441\u043f\u0430\u043c',
            },
        ),
        migrations.AlterField(
            model_name='commentclosure',
            name='depth',
            field=models.IntegerField(),
        ),
    ]
