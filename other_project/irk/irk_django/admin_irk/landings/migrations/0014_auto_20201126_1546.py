# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-11-26 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landings', '0013_thank'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='thank',
            options={'verbose_name': '\u0411\u043b\u0430\u0433\u043e\u0434\u0430\u0440\u043d\u043e\u0441\u0442\u044c \u0432\u0440\u0430\u0447\u0430\u043c', 'verbose_name_plural': '\u0411\u043b\u0430\u0433\u043e\u0434\u0430\u0440\u043d\u043e\u0441\u0442\u0438 \u0432\u0440\u0430\u0447\u0430\u043c'},
        ),
        migrations.AddField(
            model_name='thank',
            name='contact',
            field=models.CharField(default='', max_length=300, verbose_name='\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='thank',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='thank',
            name='text',
            field=models.TextField(verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='thank',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f'),
        ),
    ]