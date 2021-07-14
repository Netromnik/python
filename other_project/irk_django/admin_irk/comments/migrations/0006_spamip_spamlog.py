# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0004_auto_20180327_1224'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpamIp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(verbose_name='IP \u0430\u0434\u0440\u0435\u0441', db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
            ],
            options={
                'verbose_name': '\u0421\u043f\u0430\u043c IP \u0430\u0434\u0440\u0435\u0441',
                'verbose_name_plural': '\u0421\u043f\u0430\u043c IP \u0430\u0434\u0440\u0435\u0441\u0430',
            },
        ),
        migrations.CreateModel(
            name='SpamLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='\u0442\u0435\u043a\u0441\u0442', blank=True)),
                ('ip', models.GenericIPAddressField(verbose_name='IP \u0430\u0434\u0440\u0435\u0441')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0414\u0430\u0442\u0430 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f')),
                ('reason', models.CharField(max_length=255, verbose_name='\u041f\u0440\u0438\u0447\u0438\u043d\u0430 \u0431\u0430\u043d\u0430', blank=True)),
                ('user', models.ForeignKey(verbose_name='\u0410\u043a\u043a\u0430\u0443\u043d\u0442', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': '\u041b\u043e\u0433 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0431\u0430\u043d\u0430 \u0441\u043f\u0430\u043c\u0435\u0440\u043e\u0432',
                'verbose_name_plural': '\u041b\u043e\u0433 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0431\u0430\u043d\u0430 \u0441\u043f\u0430\u043c\u0435\u0440\u043e\u0432',
            },
        ),
    ]
