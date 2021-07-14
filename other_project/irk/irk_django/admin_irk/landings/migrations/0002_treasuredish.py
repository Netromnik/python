# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obed', '0006_auto_20181011_1041'),
        ('landings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreasureDish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_visible', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c')),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('content', models.TextField(default='', verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True)),
                ('establishment', models.ForeignKey(verbose_name='\u0417\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0435', to='obed.Establishment')),
                ('review', models.ForeignKey(verbose_name='\u0420\u0435\u0446\u0435\u043d\u0437\u0438\u044f', to='obed.Review', null=True)),
            ],
            options={
                'verbose_name': '\u0431\u043b\u044e\u0434\u043e \u0433\u0430\u0441\u0442\u0440\u043e\u043d\u043e\u043c\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u043a\u0430\u0440\u0442\u044b',
                'verbose_name_plural': '\u0431\u043b\u044e\u0434\u0430 \u0433\u0430\u0441\u0442\u0440\u043e\u043d\u043e\u043c\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u043a\u0430\u0440\u0442\u044b',
            },
        ),
    ]
